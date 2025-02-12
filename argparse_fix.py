
from argparse import ArgumentParser, ArgumentError, ArgumentTypeError

class ArgumentParserNeverExit(ArgumentParser):
    """
    !!!!
    https://bugs.python.org/issue41255
    https://github.com/python/cpython/issues/103498
    https://stackoverflow.com/questions/67890157/python-3-9-1-argparse-exit-on-error-not-working-in-certain-situations
    https://stackoverflow.com/questions/69108632/unable-to-catch-exception-error-for-argparse
    """
    def error(self, message):
        raise ValueError(f"Argparse error:{message}")

    def exit(self, status=0, message=None):
        raise ValueError(f"Argparse error:{status}:{message}")
