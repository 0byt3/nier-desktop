import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'share/lib/{name}.py')
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


kernel = module('nier-kernel-args')
hibernate = module('nier-hibernation')
rpm_wait = module('nier-rpm-wait')
rpmfusion = module('nier-rpmfusion')


class ShellTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.log = self.directory / 'commands'
        self.env = dict(os.environ, PATH=str(self.directory) + ':/usr/bin:/bin',
                        COMMAND_LOG=str(self.log), HOME=str(self.directory))
        self.stub('sudo', 'exec "$@"')
        self.stub('dnf', 'printf "%s\\n" "$*" >> "$COMMAND_LOG"\n'
                         'printf "%s" "${DNF_OUTPUT:-}"\nexit "${DNF_STATUS:-0}"')

    def stub(self, name, script):
        target = self.directory / name
        target.write_text('#!/bin/bash\n' + script + '\n')
        target.chmod(0o755)

    def helper(self, name, *args):
        return subprocess.run([str(ROOT / 'share/bin' / ('nier-' + name)), *args],
                              env=self.env, capture_output=True, text=True)

    def test_upgrade_cache_and_keyring_use_fedora_commands_and_preserve_failure(self):
        for helper, command in [('update-system-pkgs', 'upgrade --refresh -y'),
                                ('update-pkg-prune', 'clean packages'),
                                ('update-keyring', 'upgrade --refresh -y fedora-gpg-keys fedora-repos')]:
            self.env['DNF_STATUS'] = '7'
            self.assertEqual(self.helper(helper).returncode, 7)
            self.assertEqual(self.log.read_text().splitlines()[-1], command)

    def test_update_check_distinguishes_updates_current_and_broken_repositories(self):
        for status, expected in [('0', 1), ('100', 0), ('1', 2)]:
            self.env.update(DNF_STATUS=status, DNF_OUTPUT='kernel.x86_64 1.2 updates\n')
            result = self.helper('update-available')
            self.assertEqual(result.returncode, expected)
            if status == '1':
                self.assertNotIn('up to date', result.stdout)

    def test_unused_packages_are_reviewed_without_noninteractive_removal(self):
        self.env['DNF_OUTPUT'] = 'unused.x86_64\n'
        self.assertEqual(self.helper('update-orphan-pkgs').returncode, 0)
        self.assertNotIn('autoremove', self.log.read_text())
        self.env['DNF_STATUS'] = '9'
        self.assertEqual(self.helper('update-orphan-pkgs').returncode, 9)

    def test_flatpak_installs_and_removes_in_matching_user_scope(self):
        self.stub('nier-pkg-add', 'printf "pkg %s\\n" "$*" >> "$COMMAND_LOG"')
        self.stub('flatpak', 'printf "flatpak %s\\n" "$*" >> "$COMMAND_LOG"')
        self.assertEqual(self.helper('flatpak-app', 'install', 'org.signal.Signal').returncode, 0)
        self.assertIn('flatpak install --user -y flathub org.signal.Signal', self.log.read_text())
        self.assertEqual(self.helper('flatpak-app', 'remove', 'org.signal.Signal').returncode, 0)
        self.assertIn('flatpak uninstall --user -y org.signal.Signal', self.log.read_text())
        self.assertEqual(self.helper('flatpak-app', 'install', '--system').returncode, 2)

    def test_emacs_installer_does_not_launch_after_package_failure(self):
        self.stub('nier-pkg-add', 'exit 6')
        self.stub('setsid', 'touch "$HOME/launched"')
        self.assertEqual(self.helper('install-editor-emacs').returncode, 6)
        self.assertFalse((self.directory / 'launched').exists())

    def test_no_arch_commands_remain_in_executable_source(self):
        import re
        legacy = re.compile(r'\b(?:pacman(?:-key)?|yay|paru|paccache|makepkg|mkinitcpio|limine(?:-[\w-]+)?)\b')
        for directory in ('share/bin', 'share/lib', 'share/install'):
            for source in (ROOT / directory).rglob('*'):
                if source.is_file() and '__pycache__' not in source.parts:
                    self.assertIsNone(legacy.search(source.read_text()), str(source))

    def test_bar_defaults_preserve_other_settings_without_optional_services(self):
        self.env['NIER_PATH'] = str(ROOT / 'share')
        (self.directory / 'nier-shell-config').symlink_to(ROOT / 'share/bin/nier-shell-config')
        self.stub('nier-shell', 'exit 0')
        config = self.directory / '.config/nier/shell.json'
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({'bar': {'layout': {'right': ['nier.dropbox']}},
                                      'plugins': ['local.custom'], 'custom': {'enabled': True}}))
        result = self.helper('bar', 'defaults')
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = json.loads(config.read_text())
        defaults = json.loads((ROOT / 'share/config/nier/shell.json').read_text())
        self.assertEqual(actual['bar'], defaults['bar'])
        self.assertEqual(actual['plugins'], ['local.custom'])
        self.assertEqual(actual['custom'], {'enabled': True})

    def test_retired_agent_choices_fail_before_install_or_default_change(self):
        self.stub('mise', 'touch "$HOME/install-attempt"; exit 0')
        for agent in ('hermes', 'openclaw', 't3-code'):
            result = self.helper('default-agent', agent)
            self.assertEqual(result.returncode, 1)
            self.assertIn('Usage:', result.stdout)
        self.assertFalse((self.directory / 'install-attempt').exists())
        self.assertFalse((self.directory / '.config/nier/defaults/agent').exists())

    def tuxedo(self, function, path):
        return subprocess.run(['bash', '-eu', '-c',
                               'source "$1"; "$2" "$3"', 'bash',
                               str(ROOT / 'share/lib/nier-tuxedo.sh'), function, str(path)],
                              env=self.env, capture_output=True, text=True)

    def test_tuxedo_repository_is_only_added_for_matching_hardware(self):
        self.env['NIER_PATH'] = str(ROOT / 'share')
        self.stub('uname', 'echo x86_64')
        self.stub('install', 'printf "install %s\\n" "$*" >> "$COMMAND_LOG"')
        vendor = self.directory / 'sys_vendor'
        vendor.write_text('QEMU\n')
        self.assertEqual(self.tuxedo('nier_tuxedo_backlight', vendor).returncode, 0)
        self.assertFalse(self.log.exists())
        for name in ('TUXEDO', 'SLIMBOOK'):
            vendor.write_text(name + '\n')
            result = self.tuxedo('nier_tuxedo_backlight', vendor)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('--enablerepo=tuxedo install -y -- tuxedo-drivers tuxedo-control-center',
                          self.log.read_text())
        self.env['DNF_STATUS'] = '8'
        self.assertEqual(self.tuxedo('nier_tuxedo_backlight', vendor).returncode, 8)

    def test_motorcomm_prefers_native_driver_and_falls_back_only_for_exact_pci_id(self):
        self.env['NIER_PATH'] = str(ROOT / 'share')
        self.stub('uname', 'echo x86_64')
        self.stub('install', 'printf "install %s\\n" "$*" >> "$COMMAND_LOG"')
        devices = self.directory / 'pci'
        device = devices / '0000:01:00.0'
        device.mkdir(parents=True)
        (device / 'vendor').write_text('0x1f0a\n')
        (device / 'device').write_text('0x6802\n')
        self.stub('modinfo', 'exit 1')
        self.assertEqual(self.tuxedo('nier_tuxedo_ethernet', devices).returncode, 0)
        self.assertFalse(self.log.exists())
        (device / 'device').write_text('0x6801\n')
        self.stub('modinfo', 'echo "pci:v00001F0Ad00006801sv*sd*bc*sc*i*"')
        self.assertEqual(self.tuxedo('nier_tuxedo_ethernet', devices).returncode, 0)
        self.assertFalse(self.log.exists())
        self.stub('modinfo', 'exit 1')
        self.assertEqual(self.tuxedo('nier_tuxedo_ethernet', devices).returncode, 0)
        self.assertIn('--enablerepo=tuxedo install -y -- tuxedo-yt6801', self.log.read_text())

    def test_rpmfusion_always_deploys_defaults_and_propagates_install_failure(self):
        self.env['NIER_PATH'] = str(ROOT / 'share')
        self.stub('nier-pkg-add', 'printf "packages %s\\n" "$*" >> "$COMMAND_LOG"\n'
                  'exit "${PACKAGE_STATUS:-0}"')
        self.stub('lspci', 'printf "%s\\n" "$PCI_OUTPUT"')
        self.stub('install', 'exit_status=${INSTALL_STATUS:-0}\n'
                  '(( exit_status == 0 )) || exit "$exit_status"\n'
                  'if [[ $3 == /etc/yum.repos.d/nier-rpmfusion-hardware.repo ]]; then '
                  'cp "$2" "$HOME/applied.repo"; fi')
        self.env['PCI_OUTPUT'] = 'VGA compatible controller: Red Hat QXL [1b36:0100]'
        script = ROOT / 'share/install/hardware/rpmfusion.sh'
        result = subprocess.run(['bash', '-eu', str(script)], env=self.env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = (self.directory / 'applied.repo').read_text()
        self.assertIn('discord', actual)
        self.assertNotIn('akmod-nvidia', actual)
        self.assertEqual(self.log.read_text().splitlines(), [
            'packages fedora-workstation-repositories dnf5-plugins',
            'config-manager setopt --create-missing-dir rpmfusion-nonfree-steam.enabled=1'])
        self.env['PCI_OUTPUT'] = 'VGA compatible controller: NVIDIA [10de:2684]'
        result = subprocess.run(['bash', '-eu', str(script)], env=self.env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('rpmfusion-nonfree-nvidia-driver.enabled=1', self.log.read_text().splitlines()[-1])
        actual = (self.directory / 'applied.repo').read_text()
        self.env['INSTALL_STATUS'] = '7'
        result = subprocess.run(['bash', '-eu', str(script)], env=self.env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 7)
        self.assertEqual((self.directory / 'applied.repo').read_text(), actual)
        self.env['INSTALL_STATUS'] = '0'
        self.env['DNF_STATUS'] = '6'
        result = subprocess.run(['bash', '-eu', str(script)], env=self.env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 6)
        (self.directory / 'applied.repo').unlink()
        self.env['PACKAGE_STATUS'] = '8'
        result = subprocess.run(['bash', '-eu', str(script)], env=self.env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 8)
        self.assertFalse((self.directory / 'applied.repo').exists())

    def rpmfusion_scope(self, pci='', usb=()):
        import configparser
        config = configparser.ConfigParser(interpolation=None)
        template = (ROOT / 'share/default/dnf/nier-rpmfusion-hardware.repo').read_text()
        config.read_string(rpmfusion.render(template, pci, usb))
        return config

    def allows(self, config, package):
        import fnmatch
        return any(fnmatch.fnmatchcase(package, p)
                   for s in config.sections() for p in config[s]['includepkgs'].split())

    def test_rpmfusion_defaults_include_apps_and_codecs_without_hardware(self):
        config = self.rpmfusion_scope('VGA compatible controller: QXL [1b36:0100]')
        self.assertEqual(len(config.sections()), 4)
        for s in config.sections():
            self.assertEqual(config[s]['enabled'], '1')
            self.assertEqual(config[s]['gpgcheck'], '1')
            self.assertIn('/usr/share/distribution-gpg-keys/rpmfusion/', config[s]['gpgkey'])
        for package in ('steam', 'discord', 'vlc', 'vlc-plugins-freeworld', 'ffmpeg',
                        'ffmpeg-libs', 'gstreamer1-plugins-ugly', 'x264-libs'):
            self.assertTrue(self.allows(config, package), package)
        for package in ('akmod-nvidia', 'akmod-wl', 'intel-media-driver',
                        'mesa-va-drivers-freeworld', 'r5u87x-firmware', 'dropbox', 'VirtualBox'):
            self.assertFalse(self.allows(config, package), package)

    def test_rpmfusion_hardware_scope_is_specific_and_combines_hybrid_graphics(self):
        cases = [('VGA compatible controller: NVIDIA [10de:2684]', 'akmod-nvidia', 'akmod-wl'),
                 ('Display controller: Intel [8086:1234]', 'intel-media-driver', 'akmod-nvidia'),
                 ('VGA compatible controller: AMD [1002:1234]', 'mesa-va-drivers-freeworld', 'intel-media-driver'),
                 ('Network controller: Broadcom [14e4:43a0]', 'akmod-wl', 'intel-media-driver')]
        for device, included, excluded in cases:
            config = self.rpmfusion_scope(device)
            self.assertTrue(self.allows(config, included), included)
            self.assertFalse(self.allows(config, excluded), excluded)
            self.assertTrue(self.allows(config, 'discord'))
        hybrid = self.rpmfusion_scope(cases[0][0] + '\n' + cases[1][0])
        self.assertTrue(self.allows(hybrid, 'akmod-nvidia'))
        self.assertTrue(self.allows(hybrid, 'intel-media-driver'))
        self.assertFalse(self.allows(self.rpmfusion_scope('Network controller: Intel [8086:1234]'),
                                     'intel-media-driver'))
        self.assertFalse(self.allows(self.rpmfusion_scope('Broadcom [14e4:9999]'), 'akmod-wl'))
        self.assertTrue(self.allows(self.rpmfusion_scope(usb=[('05ca', '1830')]), 'r5u87x-firmware'))
        self.assertFalse(self.allows(self.rpmfusion_scope(usb=[('05ca', '9999')]), 'r5u87x-firmware'))


class KernelTests(unittest.TestCase):
    def test_add_replaces_by_key_and_remove_preserves_other_settings(self):
        original = ['ro', 'root=UUID=123', 'resume=old', 'resume_offset=1', 'quiet']
        new = kernel.update_tokens(original, 'add', ['resume=new', 'resume_offset=2'])
        self.assertEqual(new, ['ro', 'root=UUID=123', 'quiet', 'resume=new', 'resume_offset=2'])
        self.assertEqual(kernel.update_tokens(new, 'add', ['resume=new', 'resume_offset=2']), new)
        self.assertIn('resume=new', kernel.update_tokens(new, 'remove', ['resume=old']))
        self.assertEqual(kernel.update_tokens(new, 'remove', ['resume=new', 'resume_offset=2']),
                         ['ro', 'root=UUID=123', 'quiet'])
        for bad in ('x y', 'x="quoted"', 'x=foo\\bar'):
            with self.assertRaises(ValueError):
                kernel.update_tokens(original, 'add', [bad])

    def test_grubby_failure_preserves_persistent_cmdline(self):
        with tempfile.TemporaryDirectory() as directory:
            cmdline = Path(directory) / 'cmdline'
            cmdline.write_text('ro root=UUID=123 quiet custom="a b"\n')
            with patch.object(kernel.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'grubby')):
                with self.assertRaises(subprocess.CalledProcessError):
                    kernel.update('add', ['fred=on'], cmdline)
            self.assertEqual(cmdline.read_text(), 'ro root=UUID=123 quiet custom="a b"\n')
            with patch.object(kernel.subprocess, 'run') as execute:
                kernel.update('add', ['fred=on'], cmdline)
                self.assertIn('--update-kernel=ALL', execute.call_args.args[0])
            self.assertIn('fred=on', cmdline.read_text())
            self.assertIn('"custom=a b"', cmdline.read_text())
            self.assertNotIn("'", cmdline.read_text())

    def test_rpm_persistent_lock_file_is_not_itself_a_busy_transaction(self):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / '.rpm.lock'
            lock.touch()
            self.assertTrue(rpm_wait.wait_for_rpm(lock, seconds=0))
            child = subprocess.Popen(['/usr/bin/python3', '-c',
                                      'import fcntl,sys; f=open(sys.argv[1],"r+"); '
                                      'fcntl.lockf(f,fcntl.LOCK_EX); print("ready",flush=True); sys.stdin.read()',
                                      str(lock)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            try:
                self.assertEqual(child.stdout.readline().strip(), 'ready')
                self.assertFalse(rpm_wait.wait_for_rpm(lock, seconds=0))
                self.assertTrue(lock.exists())
            finally:
                child.communicate('')


class HibernationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.commands = []
        self.failure = None
        self.write('/sys/power/image_size', '1000')
        self.write('/proc/meminfo', 'MemTotal: 16000 kB\n')
        self.write('/proc/cmdline', 'ro root=UUID=abcdef quiet')
        self.write('/etc/kernel/cmdline', 'ro root=UUID=abcdef quiet')
        self.write('/etc/fstab', '/existing/swap none swap defaults 0 0\n')
        self.path('/boot/loader/entries').mkdir(parents=True)
        mock = patch.object(hibernate, 'run', side_effect=self.execute)
        mock.start()
        self.addCleanup(mock.stop)
        disk = patch.object(hibernate.shutil, 'disk_usage', return_value=SimpleNamespace(free=10 * 1024**3))
        disk.start()
        self.addCleanup(disk.stop)

    def path(self, path):
        return self.root / path.lstrip('/')

    def write(self, path, text):
        target = self.path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def execute(self, *args):
        self.commands.append(args)
        if self.failure and args[0] == self.failure:
            raise subprocess.CalledProcessError(1, args)
        if args[:4] == ('findmnt', '-n', '-o', 'FSTYPE'):
            return 'btrfs'
        if args[:4] == ('findmnt', '-n', '-o', 'UUID'):
            return '12345678-abcd-1234-abcd-123456789abc'
        if args[:3] == ('btrfs', 'subvolume', 'create'):
            Path(args[3]).mkdir()
        elif args[:3] == ('btrfs', 'subvolume', 'delete'):
            Path(args[3]).rmdir()
        elif args[:3] == ('btrfs', 'filesystem', 'mkswapfile'):
            Path(args[-1]).write_bytes(b'fake-swap')
        elif args[:3] == ('btrfs', 'inspect-internal', 'map-swapfile'):
            return '12345'
        elif len(args) > 2 and args[1].endswith('nier-kernel-args.py'):
            cmdline = self.path('/etc/kernel/cmdline')
            cmdline.write_text(' '.join(kernel.update_tokens(cmdline.read_text().split(), args[2], list(args[3:]))))
        return ''

    def test_setup_and_remove_preserve_existing_swap_and_kernel_settings(self):
        hibernate.setup(root=self.root)
        state = json.loads(self.path(hibernate.STATE).read_text())
        self.assertIn('resume_offset=12345', state['args'])
        self.assertIn('/existing/swap', self.path('/etc/fstab').read_text())
        self.assertIn('resume', self.path(hibernate.DRACUT).read_text())
        self.assertLess(next(i for i, c in enumerate(self.commands) if c[0] == 'dracut'),
                        next(i for i, c in enumerate(self.commands) if c[0].endswith('python3') or c[1].endswith('nier-kernel-args.py')))
        hibernate.setup(root=self.root)  # Repeat without recreating/reallocating swap.
        self.assertEqual(sum(c[:3] == ('btrfs', 'filesystem', 'mkswapfile') for c in self.commands), 1)
        hibernate.remove(root=self.root)
        self.assertFalse(self.path(hibernate.STATE).exists())
        self.assertFalse(self.path(hibernate.SWAP).exists())
        self.assertEqual(self.path('/etc/fstab').read_text(), '/existing/swap none swap defaults 0 0\n')
        self.assertIn('root=UUID=abcdef', self.path('/etc/kernel/cmdline').read_text())

    def test_refuse_unowned_swap_and_preexisting_resume_and_lockdown(self):
        self.path('/swap/nier').mkdir(parents=True)
        with self.assertRaisesRegex(RuntimeError, 'ownership marker'):
            hibernate.setup(root=self.root)
        self.path('/swap/nier').rmdir()
        self.write('/etc/kernel/cmdline', 'ro resume=UUID=other')
        with self.assertRaisesRegex(RuntimeError, 'not owned'):
            hibernate.setup(root=self.root)
        self.write('/sys/kernel/security/lockdown', 'none [integrity] confidentiality')
        with self.assertRaisesRegex(RuntimeError, 'lockdown'):
            hibernate.setup(root=self.root)
        self.assertFalse(self.path(hibernate.SWAP).exists())

    def test_dracut_failure_keeps_owned_swap_for_safe_retry(self):
        hibernate.setup(root=self.root)
        self.failure = 'dracut'
        with self.assertRaises(subprocess.CalledProcessError):
            hibernate.remove(root=self.root)
        self.assertTrue(self.path(hibernate.SWAP).exists())
        self.assertTrue(self.path(hibernate.STATE).exists())
        self.failure = None
        hibernate.remove(root=self.root)

    def test_changed_resume_settings_are_not_taken_over_or_removed(self):
        hibernate.setup(root=self.root)
        self.write('/etc/kernel/cmdline', 'ro resume=UUID=other resume_offset=999')
        with self.assertRaisesRegex(RuntimeError, 'changed'):
            hibernate.remove(root=self.root)
        with self.assertRaisesRegex(RuntimeError, 'changed'):
            hibernate.setup(root=self.root)
        self.assertTrue(self.path(hibernate.SWAP).exists())


if __name__ == '__main__':
    unittest.main()
