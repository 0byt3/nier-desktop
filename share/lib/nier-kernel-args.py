#!/usr/bin/env python3
"""Keep existing Fedora BLS entries and future kernel command lines aligned."""
import os
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile


def update_tokens(current, action, arguments):
    if action not in ('add', 'remove') or not arguments:
        raise ValueError('Usage: nier kernel args <add|remove> <arguments...>')
    if any(not re.fullmatch(r'[A-Za-z0-9_.-]+(?:=[^\s\x00\'"\\]+)?', arg) for arg in arguments):
        raise ValueError('Pass each kernel argument as a separate, unquoted token.')
    keys = {arg.split('=', 1)[0] for arg in arguments if action == 'add' or '=' not in arg}
    remaining = [arg for arg in current
                 if arg.split('=', 1)[0] not in keys and not (action == 'remove' and arg in arguments)]
    return remaining + (arguments if action == 'add' else [])


def update(action, arguments, cmdline=Path('/etc/kernel/cmdline')):
    if cmdline.exists():
        current = shlex.split(cmdline.read_text())
    else:
        info = subprocess.check_output(['grubby', '--info=DEFAULT'], text=True)
        match = re.search(r'^args=(.*)$', info, re.MULTILINE)
        if not match:
            raise RuntimeError('Cannot read the default Fedora kernel arguments.')
        value = shlex.split(match[1])
        current = shlex.split(value[0]) if value else []
    updated = update_tokens(current, action, arguments)
    # Kernel command lines recognize double quotes; shlex.join would introduce
    # shell single quotes and change existing parameters containing spaces.
    serialized = ' '.join(json.dumps(arg, ensure_ascii=False) if any(c.isspace() for c in arg)
                          else arg for arg in updated)
    option = '--args=' if action == 'add' else '--remove-args='
    subprocess.run(['grubby', '--update-kernel=ALL', option + ' '.join(arguments)], check=True)
    cmdline.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=cmdline.parent, delete=False) as output:
        output.write(serialized + '\n')
        temporary = Path(output.name)
    os.chmod(temporary, 0o644)
    temporary.replace(cmdline)


if __name__ == '__main__':
    try:
        update(sys.argv[1], sys.argv[2:])
    except (IndexError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
