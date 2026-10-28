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

    def test_keybindings_invitation_is_once_only_and_retries_delivery_failure(self):
        self.environment['PATH'] += ':/usr/bin:/bin'
        self.environment['HOME'] = str(self.directory)
        (self.directory / 'nier-done').symlink_to(ROOT / 'share/bin/nier-done')
        events = self.directory / 'events'
        self.environment['EVENTS'] = str(events)
        self.executable('nier-notification-send',
                        'printf "%s\\n" "$*" >> "$EVENTS"\nexit "${SEND_STATUS:-0}"\n')
        welcome = ['/bin/bash', str(ROOT / 'share/install/user/first-run/welcome.sh')]
        marker = self.directory / '.local/state/nier/done/keybindings-invitation'
        self.environment['SEND_STATUS'] = '1'
        result = subprocess.run(welcome, env=self.environment, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(marker.exists())
        self.environment['SEND_STATUS'] = '0'
        for _ in range(3):
            subprocess.run(welcome, env=self.environment, check=True)
        self.assertTrue(marker.exists())
        recorded = events.read_text()
        self.assertEqual(recorded.count('Learn Keybindings'), 2)
        self.assertIn('-u normal -t 15000', recorded)
        self.assertIn('--exec nier-menu-keybindings', recorded)

    def test_completed_install_does_not_repeat_keybindings_invitation(self):
        self.environment['PATH'] += ':/usr/bin:/bin'
        self.environment['HOME'] = str(self.directory)
        (self.directory / 'nier-done').symlink_to(ROOT / 'share/bin/nier-done')
        marker = self.directory / '.local/state/nier/done/first-run-user'
        marker.parent.mkdir(parents=True)
        marker.touch()
        # No notification sender is provided: completed installs must skip it.
        result = subprocess.run([
            '/bin/bash', str(ROOT / 'share/install/user/first-run/welcome.sh'),
        ], env=self.environment, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_first_run_update_notification_requires_available_updates(self):
        self.executable('nm-online', 'exit 0\n')
        self.executable('nier-update-available', 'exit "$UPDATE_STATUS"\n')
        events = self.directory / 'events'
        self.environment['EVENTS'] = str(events)
        self.executable('nier-notification-send', 'printf "send:%s\\n" "$*" >> "$EVENTS"\n')
        self.executable('nier-notification-dismiss', 'printf "dismiss:%s\\n" "$*" >> "$EVENTS"\n')
        for status, expected in ((0, 'send:'), (1, 'dismiss:Update System'), (2, '')):
            with self.subTest(status=status):
                events.unlink(missing_ok=True)
                self.environment['UPDATE_STATUS'] = str(status)
                result = subprocess.run([
                    '/bin/bash', str(ROOT / 'share/install/user/first-run/wifi.sh'),
                ], env=self.environment, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0)
                recorded = events.read_text() if events.exists() else ''
                if expected:
                    self.assertTrue(recorded.startswith(expected), recorded)
                else:
                    self.assertEqual(recorded, '')
                self.assertEqual(recorded.count('send:'), int(status == 0))

    def test_first_run_enabled_units_are_deployed_by_system_apply(self):
        script = (ROOT / 'share/install/user/first-run/enable-user-units.sh').read_text()
        units = [word for word in script.split() if word.endswith('.service')]
        self.assertGreater(len(units), 0)
        for unit in units:
            with self.subTest(unit=unit):
                deployed = ROOT / 'share/systemd/user' / unit
                self.assertTrue(deployed.is_file(), f'{unit} is missing from system deployment')
                self.assertEqual(deployed.read_bytes(),
                                 (ROOT / 'share/default/systemd/user' / unit).read_bytes())

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
