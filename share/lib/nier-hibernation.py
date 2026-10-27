#!/usr/bin/env python3
"""Fedora Btrfs swapfile resume integration. Called by the root shell wrappers."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


SWAP = '/swap/nier/swapfile'
STATE = '/etc/nier/hibernation.json'
DRACUT = '/etc/dracut.conf.d/90-nier-resume.conf'
MARKER = '/swap/nier/.nier-owned'


def run(*arguments):
    return subprocess.check_output(arguments, text=True).strip()


def atomic(path, content, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as output:
        output.write(content)
        temporary = Path(output.name)
    temporary.chmod(mode)
    temporary.replace(path)


def root_path(root, path):
    return root / path.lstrip('/')


def setup(no_rebuild=False, root=Path('/')):
    path = lambda name: root_path(root, name)
    if not path('/sys/power/image_size').exists():
        raise RuntimeError('This kernel does not support hibernation.')
    lockdown = path('/sys/kernel/security/lockdown')
    if lockdown.exists() and re.search(r'\[(integrity|confidentiality)\]', lockdown.read_text()):
        raise RuntimeError('Kernel lockdown blocks hibernation. Nier will not change Secure Boot policy.')
    if run('findmnt', '-n', '-o', 'FSTYPE', '/') != 'btrfs':
        raise RuntimeError('Automatic Nier hibernation setup requires a Btrfs root filesystem.')
    if not path('/boot/loader/entries').is_dir():
        raise RuntimeError('Fedora GRUB/BLS entries are required.')
    state_path = path(STATE)
    if state_path.exists():
        previous = json.loads(state_path.read_text())
        if previous.get('swap') != SWAP:
            raise RuntimeError('Existing Nier hibernation state is invalid.')
        current = path('/etc/kernel/cmdline').read_text().split()
        for value in current:
            if value.startswith(('resume=', 'resume_offset=')) and value not in previous.get('args', []):
                raise RuntimeError('Resume settings changed since Nier setup; reconcile them first.')
    if not state_path.exists():
        cmdline = path('/etc/kernel/cmdline')
        current = cmdline.read_text() if cmdline.exists() else path('/proc/cmdline').read_text()
        if re.search(r'(^|\s)resume(?:_offset)?=', current):
            raise RuntimeError('Existing resume settings are not owned by Nier; keep or remove them manually first.')
    swap = path(SWAP)
    if swap.parent.exists() and not path(MARKER).is_file():
        raise RuntimeError('/swap/nier already exists without a Nier ownership marker; refusing to reuse it.')
    if path(DRACUT).exists() and not state_path.exists():
        raise RuntimeError('The Nier resume dracut filename is already in use without ownership state.')
    if not swap.parent.exists():
        swap.parent.parent.mkdir(parents=True, exist_ok=True)
        run('btrfs', 'subvolume', 'create', str(swap.parent))
        atomic(path(MARKER), 'Nier hibernation swap subvolume\n', 0o600)
    if not swap.exists():
        meminfo = path('/proc/meminfo').read_text()
        memory = int(re.search(r'^MemTotal:\s+(\d+)', meminfo, re.M)[1]) * 1024
        size = ((memory + 256 * 1024**2 + 4095) // 4096) * 4096
        if shutil.disk_usage(swap.parent).free < size + 1024**3:
            raise RuntimeError('Not enough free space for the hibernation swapfile and 1 GiB reserve.')
        run('btrfs', 'filesystem', 'mkswapfile', '--size', str(size), str(swap))
    offset = run('btrfs', 'inspect-internal', 'map-swapfile', '-r', str(swap))
    uuid = run('findmnt', '-n', '-o', 'UUID', '-T', str(swap))
    if not offset.isdecimal() or not re.fullmatch(r'[a-fA-F0-9-]{8,}', uuid):
        raise RuntimeError('Cannot determine the Btrfs swapfile resume device and physical offset.')
    arguments = [f'resume=UUID={uuid}', f'resume_offset={offset}']
    # Ownership state is written before configuration so interrupted setup is retryable.
    atomic(state_path, json.dumps({'swap': SWAP, 'args': arguments}) + '\n', 0o600)
    fstab = path('/etc/fstab')
    contents = fstab.read_text()
    if not any(line.split() and line.split()[0] == SWAP for line in contents.splitlines()):
        atomic(fstab, contents.rstrip() + f'\n# Nier hibernation swap\n{SWAP} none swap defaults,pri=0 0 0\n')
    active = run('swapon', '--show=NAME', '--noheadings').splitlines()
    if str(swap) not in active:
        run('swapon', '-p', '0', str(swap))
    atomic(path(DRACUT), 'add_dracutmodules+=" resume "\n')
    if not no_rebuild:
        run('dracut', '--force', '--regenerate-all')
    run(sys.executable, str(Path(__file__).with_name('nier-kernel-args.py')), 'add', *arguments)
    print('Hibernation configured. Reboot before testing suspend-to-disk.')
    if no_rebuild:
        print('Run dracut --force --regenerate-all before rebooting (--no-rebuild was requested).')


def remove(root=Path('/')):
    path = lambda name: root_path(root, name)
    state_path = path(STATE)
    if not state_path.exists():
        print('Nier hibernation is not configured.')
        return
    state = json.loads(state_path.read_text())
    if state.get('swap') != SWAP or not path(MARKER).is_file():
        raise RuntimeError('Hibernation ownership state is invalid; refusing to remove swap.')
    arguments = state.get('args', [])
    if (len(arguments) != 2 or not re.fullmatch(r'resume=UUID=[a-fA-F0-9-]{8,}', arguments[0])
            or not re.fullmatch(r'resume_offset=\d+', arguments[1])):
        raise RuntimeError('Hibernation resume state is invalid; no files were removed.')
    if path(DRACUT).exists() and path(DRACUT).read_text() != 'add_dracutmodules+=" resume "\n':
        raise RuntimeError('The resume dracut file was changed; reconcile it before removing hibernation.')
    # Do not remove a replacement resume configuration installed by the user.
    cmdline = path('/etc/kernel/cmdline').read_text().split()
    for arg in arguments:
        key = arg.split('=', 1)[0] + '='
        if any(value.startswith(key) and value != arg for value in cmdline):
            raise RuntimeError('Resume settings changed since setup; reconcile them before removing Nier swap.')
    run(sys.executable, str(Path(__file__).with_name('nier-kernel-args.py')), 'remove', *arguments)
    path(DRACUT).unlink(missing_ok=True)
    # Rebuild before deleting swap. On a build failure it remains available for retry.
    run('dracut', '--force', '--regenerate-all')
    swap = path(SWAP)
    active = run('swapon', '--show=NAME', '--noheadings').splitlines()
    if str(swap) in active:
        run('swapoff', str(swap))
    fstab = path('/etc/fstab')
    lines = [line for line in fstab.read_text().splitlines()
             if line != '# Nier hibernation swap' and not (line.split() and line.split()[0] == SWAP)]
    atomic(fstab, '\n'.join(lines) + '\n')
    swap.unlink(missing_ok=True)
    remaining = {entry.name for entry in swap.parent.iterdir()}
    if remaining == {'.nier-owned'}:
        path(MARKER).unlink()
        run('btrfs', 'subvolume', 'delete', str(swap.parent))
    else:
        print('/swap/nier has additional files; preserving that subvolume and ownership marker.')
    state_path.unlink()
    print('Nier hibernation removed. Reboot to clear the running kernel resume settings.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('setup', 'remove'))
    parser.add_argument('--no-rebuild', action='store_true')
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error('Run this helper through sudo nier hibernation setup/remove.')
    try:
        setup(args.no_rebuild) if args.action == 'setup' else remove()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))


if __name__ == '__main__':
    main()
