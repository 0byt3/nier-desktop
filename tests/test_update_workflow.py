import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class UpdateWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.environment = dict(os.environ, PATH=str(self.directory))
        self.environment.pop('NIER_UPDATE_LOGGED', None)

    def executable(self, name, source):
        path = self.directory / name
        path.write_text('#!/bin/bash\n' + source)
        path.chmod(0o755)

    def test_missing_logging_dependency_fails_with_fedora_install_instruction(self):
        result = subprocess.run([str(ROOT / 'share/bin/nier-update')],
                                env=self.environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 127)
        self.assertIn('sudo dnf install util-linux-script', result.stderr)

    def test_logging_process_failure_is_preserved(self):
        (self.directory / 'env').symlink_to('/usr/bin/env')
        self.executable('script', '[[ $NIER_UPDATE_LOGGED == 1 ]] || exit 99\nexit 42\n')
        result = subprocess.run([str(ROOT / 'share/bin/nier-update'), '-y'],
                                env=self.environment, capture_output=True)
        self.assertEqual(result.returncode, 42)

    def test_terminal_preserves_status_and_reports_failure_or_success(self):
        self.executable('setsid', 'for last; do :; done\nexec /bin/bash -c "$last"\n')
        self.executable('nier-show-logo', ':\n')
        self.executable('nier-show-done', 'printf "%s" "$1" > "$RESULT_FILE"\n')
        status_file = self.directory / 'status'
        self.environment['RESULT_FILE'] = str(status_file)
        for status in (0, 7, 130):
            with self.subTest(status=status):
                status_file.unlink(missing_ok=True)
                result = subprocess.run([
                    str(ROOT / 'share/bin/nier-launch-floating-terminal-with-presentation'),
                    f"/bin/sh -c 'exit {status}'",
                ], env=self.environment)
                self.assertEqual(result.returncode, status)
                if status == 130:
                    self.assertFalse(status_file.exists())
                else:
                    self.assertEqual(status_file.read_text(), str(status))

    def test_fedora_multiple_kernel_reboot_detection(self):
        self.environment['PATH'] += ':/usr/bin:/bin'
        self.environment['HOME'] = str(self.directory)
        prompt = self.directory / 'prompt'
        self.environment['PROMPT_FILE'] = str(prompt)
        self.executable('uname', 'printf "%s\\n" "$RUNNING_KERNEL"\n')
        self.executable('rpm', '[[ ${NO_KERNEL_RPM:-0} == 0 ]] || exit 1\nprintf "%s\\n" "$INSTALLED_KERNELS"\n')
        self.executable('gum', 'printf "%s\\n" "$*" >> "$PROMPT_FILE"\nexit 1\n')
        self.executable('pgrep', 'exit 1\n')
        self.executable('nier-restart-shell', 'exit 0\n')
        installed = '6.19.9-300.fc44.x86_64\n6.19.10-300.fc44.x86_64'
        for running, missing, expected in (
            ('6.19.9-300.fc44.x86_64', '0', True),
            ('6.19.10-300.fc44.x86_64', '0', False),
            ('custom-kernel', '1', False),
        ):
            with self.subTest(running=running, missing=missing):
                prompt.unlink(missing_ok=True)
                self.environment.update(RUNNING_KERNEL=running,
                                        INSTALLED_KERNELS=installed,
                                        NO_KERNEL_RPM=missing)
                result = subprocess.run([str(ROOT / 'share/bin/nier-update-restart')],
                                        env=self.environment, capture_output=True)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(prompt.exists(), expected)


if __name__ == '__main__':
    unittest.main()
