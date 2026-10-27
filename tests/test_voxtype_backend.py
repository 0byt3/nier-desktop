import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch
import wave


MODULE = Path(__file__).resolve().parents[1] / 'share/lib/nier-voxtype-backend.py'
SPEC = importlib.util.spec_from_file_location('voxtype_backend', MODULE)
backend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backend)

GPU_LOG = '''ggml_vulkan: 0 = Test GPU (test-driver) | uma: 1
whisper_backend_init_gpu: using Vulkan0 backend
whisper_model_load: Vulkan0 total size = 147.37 MB
Transcription completed in 0.23s: ""
'''
HARDWARE = 'GPU0:\n deviceType = PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU\n deviceName = Test GPU\n'


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for variant in ('baseline', 'avx2', 'avx512', 'vulkan'):
            binary = self.root / f'voxtype-{variant}'
            binary.write_text('#!/bin/sh\nexit 0\n')
            binary.chmod(0o755)

    def test_cpu_selection_checks_all_avx512_features_and_falls_back(self):
        v4 = {'avx2', 'avx512f', 'avx512bw', 'avx512cd', 'avx512dq', 'avx512vl'}
        for flags, expected in ((set(), 'baseline'), ({'avx2'}, 'avx2'),
                                ({'avx2', 'avx512f'}, 'avx2'), (v4, 'avx512')):
            with self.subTest(flags=flags):
                self.assertEqual(backend.cpu_backend(flags, self.root).name,
                                 f'voxtype-{expected}')
        (self.root / 'voxtype-avx512').write_text('#!/bin/sh\nexit 132\n')
        self.assertEqual(backend.cpu_backend(v4, self.root).name, 'voxtype-avx2')
        (self.root / 'voxtype-avx2').unlink()
        self.assertEqual(backend.cpu_backend(v4, self.root).name, 'voxtype-baseline')

    def test_gpu_requires_actual_compute_not_intent_or_software(self):
        self.assertTrue(backend.gpu_evidence(GPU_LOG, {'test gpu'}))
        self.assertTrue(backend.gpu_evidence(
            GPU_LOG + 'ggml_vulkan: 1 = llvmpipe (LLVM)\n', {'test gpu'}))
        for output in ('use gpu = 1', 'ggml_vulkan: Found 1 Vulkan devices:',
                       GPU_LOG.replace('using Vulkan0 backend', 'no GPU found'),
                       GPU_LOG.replace('147.37', '0.00'),
                       GPU_LOG.replace('Test GPU', 'llvmpipe'),
                       GPU_LOG.replace('Test GPU', 'lavapipe')):
            with self.subTest(output=output):
                self.assertFalse(backend.gpu_evidence(output, {'test gpu'}))

    def test_real_probe_uses_model_and_generated_audio_without_vad_or_hooks(self):
        def execute(command, timeout=120):
            if command[0] == 'vulkaninfo':
                return subprocess.CompletedProcess(command, 0, HARDWARE)
            config = tomllib.loads(Path(command[2]).read_text())
            self.assertEqual(config['whisper']['model'], 'small.en')
            self.assertEqual(config['whisper']['gpu_device'], 1)
            self.assertEqual(config['whisper']['mode'], 'local')
            self.assertFalse(config['vad']['enabled'])
            self.assertNotIn('output', config)
            with wave.open(command[-1]) as audio:
                self.assertEqual(audio.getframerate(), 16000)
                self.assertEqual(audio.getnchannels(), 1)
                self.assertEqual(audio.getnframes(), 32000)
            return subprocess.CompletedProcess(command, 0, GPU_LOG)
        config = {'whisper': {'model': 'small.en', 'gpu_device': 1},
                  'vad': {'enabled': True}, 'output': {'post_process': {'command': 'bad'}}}
        with patch.object(backend, 'run', side_effect=execute):
            self.assertTrue(backend.probe_vulkan(config, {'avx2'}, io.StringIO(),
                                                 self.root)[0])

    def test_no_avx2_or_no_hardware_skips_inference(self):
        with patch.object(backend, 'run') as execute:
            self.assertFalse(backend.probe_vulkan({}, set(), io.StringIO(), self.root)[0])
            execute.assert_not_called()
        with patch.object(backend, 'run', return_value=subprocess.CompletedProcess(
                [], 0, 'deviceType = PHYSICAL_DEVICE_TYPE_CPU')) as execute:
            self.assertFalse(backend.probe_vulkan({}, {'avx2'}, io.StringIO(), self.root)[0])
            self.assertEqual(execute.call_count, 1)

    def test_driver_error_crash_timeout_or_cpu_fallback_is_failure(self):
        for failure in (FileNotFoundError('vulkaninfo'), subprocess.TimeoutExpired([], 120),
                        subprocess.CompletedProcess([], 132, GPU_LOG),
                        subprocess.CompletedProcess([], 0, 'no GPU found')):
            with self.subTest(failure=failure):
                outcomes = [subprocess.CompletedProcess([], 0, HARDWARE), failure]
                with patch.object(backend, 'run', side_effect=outcomes):
                    self.assertFalse(backend.probe_vulkan({}, {'avx2'}, io.StringIO(),
                                                          self.root)[0])

    def test_rerunning_failed_probe_replaces_previous_gpu_service_override(self):
        config = self.root / 'voxtype'
        config.mkdir()
        (config / 'config.toml').write_text('[whisper]\nmodel = "base.en"\n')
        environment = {'XDG_CONFIG_HOME': str(self.root), 'XDG_STATE_HOME': str(self.root)}
        with patch.dict(os.environ, environment), patch.object(backend, 'LIB', self.root), \
                patch.object(backend, 'probe_vulkan', return_value=(True, 'tested')):
            backend.main()
        dropin = self.root / 'systemd/user/voxtype.service.d/20-nier-backend.conf'
        self.assertIn('voxtype-vulkan daemon', dropin.read_text())
        with patch.dict(os.environ, environment), patch.object(backend, 'LIB', self.root), \
                patch.object(backend, 'probe_vulkan', return_value=(False, 'driver failure')):
            backend.main()
        self.assertNotIn('voxtype-vulkan', dropin.read_text())
        self.assertIn('ExecStart=\nExecStart=', dropin.read_text())
        self.assertEqual((self.root / 'nier/voxtype-vulkan.log').stat().st_mode & 0o777, 0o600)


if __name__ == '__main__':
    unittest.main()
