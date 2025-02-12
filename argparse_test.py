
from argparse import ArgumentParser, ArgumentError, ArgumentTypeError

class ArgumentParserNeverExit(ArgumentParser):
    """
    !!!!
    https://bugs.python.org/issue41255
    https://github.com/python/cpython/issues/103498
    https://stackoverflow.com/questions/67890157/python-3-9-1-argparse-exit-on-error-not-working-in-certain-situations
    https://stackoverflow.com/questions/69108632/unable-to-catch-exception-error-for-argparse
    """ 

    def add_argument(self, *args, **kwargs):
        print(f"add_args in:{args}")

        new_args = []
        for arg in args:
            new_args.append(arg)
            if arg.startswith('-') and ('-' + arg) not in args:
                new_args.append('-' + arg)
            args = tuple(new_args)

        #new_args = [
        #    '-' + arg if arg.startswith('-') and ('-' + arg) not in args
        #]
        args = tuple(new_args + list(args))

        #if len(args) == 1 and args[0].startswith('-'):
        #    args = (args[0], ('-' + args[0]))
        #    print(f"add_args out:{args}")

        return super().add_argument(*args, **kwargs)
    
    def error(self, message):
        raise ValueError(f"Argparse error:{message}")

    def exit(self, status=0, message=None):
        raise ValueError(f"Argparse error:{status}:{message}")

def str_to_bool(arg):
    values = {
        'true': True, 
        'yes': True, 
        'on': True,
        'false': False, 
        'no': False, 
        'off': False,
    }
    try:
        return values[arg.lower()]
    except KeyError:
        raise ValueError

parser = ArgumentParserNeverExit()
subparsers = parser.add_subparsers(dest='operation', required=True)
command_parser = subparsers.add_parser('command')
command_parser.add_argument('command_name', choices=['calibrate_all_dimmers'])
mode_parser = subparsers.add_parser('mode')
mode_parser.add_argument('mode_id', choices=['1', '2', 'ab', 'cd'])
pattern_parser = subparsers.add_parser('pattern')
pattern_parser.add_argument('-relay', nargs=1, type=lambda p: len(p)==10)
pattern_parser.add_argument('-dimmer', nargs=1, type=lambda p: len(p)==10)
pattern_parser.add_argument('-derive_missing', dest='derive_missing', type=str_to_bool, default=True)

print(parser.parse_args())
