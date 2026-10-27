"""Apply optional administrator display settings inside the greeter compositor."""
import json
from pathlib import Path
import re
import subprocess


def output_arguments(settings):
    display = settings.get('display')
    if not display:
        return None
    name, mode = display.get('name', ''), display.get('mode', '')
    scale = display.get('scale', 1)
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]+', name):
        raise ValueError('Invalid display name')
    if not isinstance(mode, str) or not re.fullmatch(r'\d{3,5}x\d{3,5}(@\d+(\.\d+)?Hz)?', mode):
        raise ValueError('Invalid display mode')
    if not isinstance(scale, (float, int)) or isinstance(scale, bool) or not 0.5 <= scale <= 4:
        raise ValueError('Invalid display scale')
    return ['wlr-randr', '--output', name, '--mode', mode, '--scale', str(scale)]


if __name__ == '__main__':
    try:
        settings = json.loads(Path('/etc/nier/greeter.json').read_text())
        arguments = output_arguments(settings)
        if arguments:
            subprocess.run(arguments, check=True)
    except (OSError, ValueError, TypeError, AttributeError, subprocess.SubprocessError):
        # A bad monitor configuration must not prevent the login UI appearing.
        print('Nier: using the default greeter display mode')
