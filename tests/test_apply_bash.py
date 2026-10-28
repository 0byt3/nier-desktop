import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(os.geteuid() == 0, 'User apply intentionally refuses root')
class ApplyBashTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        stub = self.home / 'bin'
        stub.mkdir()
        (stub / 'systemctl').write_text('#!/bin/bash\nexit 0\n')
        (stub / 'systemctl').chmod(0o755)
        self.env = dict(os.environ, HOME=str(self.home),
                        XDG_CONFIG_HOME=str(self.home / 'settings'),
                        XDG_STATE_HOME=str(self.home / 'state'),
                        NIER_PATH=str(ROOT / 'share'),
                        PATH=f'{stub}:/usr/bin:/bin')

    def apply(self, *args):
        return subprocess.run(['/bin/bash', str(ROOT / 'share/bin/nier-apply'), *args],
                              env=self.env, check=True, capture_output=True)

    def test_existing_bashrc_is_backed_up_preserved_and_activated_once(self):
        bashrc = self.home / '.bashrc'
        original = '# personal settings\nalias personal="echo preserved"\n'
        bashrc.write_text(original)
        self.apply()
        self.apply()
        self.assertTrue(bashrc.read_text().startswith(original))
        self.assertEqual(bashrc.read_text().count('# BEGIN Nier Bash customizations'), 1)
        backups = list(self.home.glob('.bashrc.bak.*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), original)
        result = subprocess.run(['/bin/bash', '--noprofile', '--rcfile', str(bashrc),
                                 '-ic', 'alias personal; alias ..; printf "%s" "$PS1"'],
                                env=dict(self.env, TERM='dumb'), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('echo preserved', result.stdout)
        self.assertIn('cd ..', result.stdout)
        self.assertIn('bash$', result.stdout)

    def test_fresh_user_gets_shell_files_in_xdg_directory(self):
        self.apply()
        source = ROOT / 'share/basic-cli/bash'
        self.assertEqual((self.home / '.bashrc').read_bytes(), (source / '.bashrc').read_bytes())
        for name in ('bashrc', 'prompt.bash', 'blesh.bash', 'blerc', 'aliases.d', 'completions.d'):
            self.assertTrue((self.home / 'settings/basic-cli' / name).exists(), name)
        for name in ('.bash_profile', '.bash_logout', '.inputrc'):
            self.assertTrue((self.home / name).exists(), name)

    def test_force_replaces_shell_configs_with_backups(self):
        bashrc = self.home / '.bashrc'
        bashrc.write_text('# personal\n')
        self.apply('--force')
        self.assertEqual(bashrc.read_bytes(), (ROOT / 'share/basic-cli/bash/.bashrc').read_bytes())
        self.assertEqual(next(self.home.glob('.bashrc.bak.*')).read_text(), '# personal\n')
