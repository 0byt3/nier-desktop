"""Render default application/multimedia scope plus detected hardware families."""
import configparser
import io
from pathlib import Path
import re
import sys

NVIDIA = ('akmod-nvidia* kmod-nvidia* nvidia-kmod* nvidia-open-kmod* '
          'xorg-x11-drv-nvidia* nvidia-modprobe nvidia-persistenced '
          'nvidia-settings* nvidia-xconfig').split()
MESA = ['mesa-va-drivers-freeworld', 'mesa-vulkan-drivers-freeworld']
# USB products represented by the r5u87x-firmware package's firmware files.
RICOH = {'1803', '1810', '1812', '1830', '1832', '1833', '1834', '1835',
         '1836', '1837', '1839', '183a', '183b', '183e', '1841', '1870'}


def usb_ids(root=Path('/sys/bus/usb/devices')):
    result = []
    for device in root.glob('*'):
        try:
            result.append((device.joinpath('idVendor').read_text().strip().lower(),
                           device.joinpath('idProduct').read_text().strip().lower()))
        except (OSError, UnicodeError):
            continue
    return result


def render(template, pci, usb=()):
    free, nonfree = set(), set()
    for line in pci.splitlines():
        display = re.search(r'\b(?:VGA|3D|Display)\b', line, re.I)
        if display and re.search(r'\[10de:[0-9a-f]{4}\]', line, re.I):
            nonfree.update(NVIDIA)
            free.update(('akmods', 'kmodtool'))
        if display and re.search(r'\[(?:8086|1002):[0-9a-f]{4}\]', line, re.I):
            free.update(MESA)
        if display and re.search(r'\[8086:[0-9a-f]{4}\]', line, re.I):
            free.add('libva-intel-driver')
            nonfree.update(('intel-media-driver', 'libva-intel-hybrid-driver'))
        if re.search(r'\[14e4:(?:43a0|4331)\]', line, re.I):
            nonfree.update(('akmod-wl', 'kmod-wl*', 'broadcom-wl'))
            free.update(('akmods', 'kmodtool'))
    if any(vendor == '05ca' and product in RICOH for vendor, product in usb):
        nonfree.add('r5u87x-firmware')
    config = configparser.ConfigParser(interpolation=None)
    config.read_string(template)
    for name in config.sections():
        extra = nonfree if '-nonfree-' in name else free
        allowed = set(config[name]['includepkgs'].split()) | extra
        config[name]['includepkgs'] = ' '.join(sorted(allowed))
    output = io.StringIO()
    output.write('# Managed by Nier: default apps/multimedia plus detected hardware.\n')
    config.write(output)
    return output.getvalue()


if __name__ == '__main__':
    print(render(Path(sys.argv[1]).read_text(), sys.stdin.read(), usb_ids()), end='')
