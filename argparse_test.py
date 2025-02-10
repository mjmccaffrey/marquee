import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='operation')

command_parser = subparsers.add_parser('command')
command_parser.add_argument('command_name', choices=['calibrate_all_dimmers'])

mode_parser = subparsers.add_parser('mode')
mode_parser.add_argument('mode_id', choices=['1', '2', 'ab', 'cd'])

pattern_parser = subparsers.add_parser('pattern')
pattern_parser.add_argument('--relay', nargs=1, type=lambda p: len(p)==10)
pattern_parser.add_argument('--dimmer', nargs=1, type=lambda p: len(p)==10)

print(parser.parse_args())

# mode_spec = mode_parser.add_mutually_exclusive_group(required=True)
# mode_spec.add_argument('--mode_name', required=False, choices=['ab', 'cd', 'ef'])
# mode_spec.add_argument('--mode_index', required=False, type=int, choices=[1, 2, 3])
