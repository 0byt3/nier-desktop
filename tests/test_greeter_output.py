import importlib.util
from pathlib import Path
import unittest

source = Path(__file__).resolve().parents[1] / 'share/greeter/configure-output.py'
spec = importlib.util.spec_from_file_location('greeter_output', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class GreeterOutputTests(unittest.TestCase):
    def test_no_override_leaves_native_display_configuration(self):
        self.assertIsNone(module.output_arguments({}))

    def test_explicit_mode_is_passed_as_arguments_not_shell_code(self):
        settings = {'display': {'name': 'Virtual-1', 'mode': '2560x1440', 'scale': 1}}
        self.assertEqual(module.output_arguments(settings),
                         ['wlr-randr', '--output', 'Virtual-1', '--mode', '2560x1440', '--scale', '1'])

    def test_invalid_values_cannot_become_output_commands(self):
        for settings in (
            {'name': 'Virtual-1; command', 'mode': '2560x1440'},
            {'name': 'Virtual-1', 'mode': '2560x1440; command'},
            {'name': 'Virtual-1', 'mode': '2560x1440', 'scale': '1; command'},
            {'name': 'Virtual-1', 'mode': '2560x1440', 'scale': True},
            {'name': 'Virtual-1', 'mode': '2560x1440', 'scale': 0},
        ):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                module.output_arguments({'display': settings})

    def test_fractional_scale_and_explicit_refresh(self):
        args = module.output_arguments({'display': {'name': 'DP-1', 'mode': '2560x1440@60.007Hz', 'scale': 1.25}})
        self.assertEqual(args[-1], '1.25')


if __name__ == '__main__':
    unittest.main()
