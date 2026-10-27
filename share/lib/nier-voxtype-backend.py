#!/usr/bin/env python3
"""Select a tested local Whisper backend without changing the packaged launcher."""

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import tomllib
import wave


LIB = Path('/usr/lib/voxtype')
TIMEOUT = 120


def run(command, timeout=TIMEOUT):
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, errors='replace', timeout=timeout, check=False)


def cpu_backend(flags, library=LIB):
    # The AVX-512 build targets x86-64-v4, which needs more than avx512f alone.
    candidates = []
    if {'avx2', 'avx512f', 'avx512bw', 'avx512cd', 'avx512dq', 'avx512vl'} <= flags:
        candidates.append('avx512')
    if 'avx2' in flags:
        candidates.append('avx2')
    candidates.append('baseline')
    for variant in candidates:
        binary = library / f'voxtype-{variant}'
        if os.access(binary, os.X_OK):
            try:
                if run([str(binary), '--version'], timeout=10).returncode == 0:
                    return binary
            except (OSError, subprocess.TimeoutExpired):
                pass
    raise RuntimeError('No working Voxtype CPU binary found; reinstall the Nier voxtype RPM.')


def hardware_names(summary):
    names = set()
    for device in re.split(r'(?m)^GPU\d+:', summary)[1:]:
        if re.search(r'deviceType\s*=\s*PHYSICAL_DEVICE_TYPE_(?:DISCRETE|INTEGRATED)_GPU', device):
            name = re.search(r'deviceName\s*=\s*(.+)', device)
            if name:
                names.add(name[1].strip().lower())
    return names


def gpu_evidence(output, hardware):
    """A successful process alone also covers silent CPU/software Vulkan fallback."""
    output = output.lower()
    rejected = ('no gpu found', 'falling back to cpu', 'no devices found', 'ggml_vulkan: error')
    selected = re.search(r'whisper_backend_init_gpu: using vulkan(\d+) backend', output)
    if not selected or any(marker in output for marker in rejected):
        return False
    index = selected[1]
    device = re.search(r'ggml_vulkan:\s+' + index + r' = (.+)', output)
    # Match the device actually selected by Whisper, rather than rejecting a
    # machine merely because an unused software ICD is also enumerated.
    if not device or not any(device[1].startswith(name + ' (') for name in hardware):
        return False
    allocation = re.search(
        r'whisper_model_load:\s+vulkan' + index
        + r'\s+(?:total|buffer) size\s*=\s*([0-9]+(?:\.[0-9]+)?) mb',
        output)
    return bool(allocation and float(allocation[1]) > 0)


def probe_vulkan(config, flags, log, library=LIB):
    binary = library / 'voxtype-vulkan'
    if 'avx2' not in flags:
        return False, 'the packaged Vulkan binary requires AVX2'
    if not os.access(binary, os.X_OK):
        return False, 'the Vulkan binary is unavailable'
    try:
        devices = run(['vulkaninfo', '--summary'], timeout=20)
        log.write(devices.stdout)
        # Mesa lavapipe can expose a fully functional Vulkan API on a CPU.
        hardware = hardware_names(devices.stdout)
        if devices.returncode or not hardware:
            return False, 'no usable hardware Vulkan device was found'

        with tempfile.TemporaryDirectory(prefix='nier-voxtype-probe-') as directory:
            directory = Path(directory)
            audio = directory / 'probe.wav'
            with wave.open(str(audio), 'wb') as sample:
                sample.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
                sample.writeframes(b'\0\0' * 32000)
            # Use the user's actual model/settings, but disable VAD, remote APIs,
            # and post-processing. This exercises inference without microphone input.
            whisper = config.get('whisper', {})
            settings = {'model': 'base.en', 'mode': 'local'}
            for key in ('model', 'language', 'translate', 'threads', 'gpu_device',
                        'flash_attention'):
                if key in whisper:
                    settings[key] = whisper[key]
            probe_config = directory / 'config.toml'
            probe_config.write_text('engine = "whisper"\n[vad]\nenabled = false\n[whisper]\n'
                                    + ''.join(f'{key} = {json.dumps(value)}\n'
                                              for key, value in settings.items()))
            result = run([str(binary), '--config', str(probe_config),
                          'transcribe', str(audio)])
            log.write(result.stdout)
            if result.returncode == 0 and gpu_evidence(result.stdout, hardware):
                return True, 'hardware Vulkan inference completed successfully'
            return False, 'Vulkan inference failed or GPU execution could not be confirmed'
    except subprocess.TimeoutExpired as error:
        output = error.stdout or b''
        log.write(output.decode(errors='replace') if isinstance(output, bytes) else output)
        return False, 'the Vulkan test timed out'
    except OSError as error:
        return False, f'the Vulkan test could not run: {error}'


def write_override(config_home, binary):
    directory = config_home / 'systemd/user/voxtype.service.d'
    directory.mkdir(parents=True, exist_ok=True)
    content = ('# Managed by Nier dictation setup; rerun setup to test acceleration again.\n'
               '[Service]\nExecStart=\n'
               f'ExecStart={binary} daemon\n')
    with tempfile.NamedTemporaryFile(mode='w', dir=directory, delete=False) as output:
        output.write(content)
        temporary = Path(output.name)
    temporary.replace(directory / '20-nier-backend.conf')


def main():
    config_home = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config')
    config_path = config_home / 'voxtype/config.toml'
    with config_path.open('rb') as source:
        config = tomllib.load(source)
    if (config.get('engine', 'whisper') != 'whisper'
            or config.get('whisper', {}).get('mode', 'local') != 'local'):
        print('Keeping the configured non-local-Whisper engine; automatic Vulkan setup is skipped.')
        subprocess.run(['voxtype', 'setup', '--download', '--no-post-install'], check=True)
        return
    flags = set(Path('/proc/cpuinfo').read_text().split())
    cpu = cpu_backend(flags, library=LIB)
    # A previously enabled/broken GPU launcher must not block model setup or fallback.
    subprocess.run([str(cpu), '--config', str(config_path),
                    'setup', '--download', '--no-post-install'], check=True)
    state_home = Path(os.environ.get('XDG_STATE_HOME') or Path.home() / '.local/state')
    state = state_home / 'nier'
    state.mkdir(parents=True, exist_ok=True)
    log_path = state / 'voxtype-vulkan.log'
    print('Testing Vulkan acceleration with generated audio (up to 120 seconds)...', flush=True)
    # Recreate with private permissions, including when an older log already exists.
    log_path.unlink(missing_ok=True)
    with open(log_path, 'x', opener=lambda path, flags: os.open(path, flags, 0o600)) as log:
        enabled, reason = probe_vulkan(config, flags, log)
        log.write(f'\nDecision: {reason}\n')
    binary = LIB / 'voxtype-vulkan' if enabled else cpu
    write_override(config_home, binary)
    print(f'Dictation backend: {binary.name} ({reason}).')
    print(f'Vulkan test log: {log_path}')


if __name__ == '__main__':
    main()
