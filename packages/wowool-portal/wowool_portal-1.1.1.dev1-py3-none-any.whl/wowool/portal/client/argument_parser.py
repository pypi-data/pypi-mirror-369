from argparse import ArgumentParser as ArgumentParserBase, RawDescriptionHelpFormatter
from gettext import gettext
from logging import getLogger
from sys import stderr

logger = getLogger(__name__)


class ArgumentParser(ArgumentParserBase):
    def __init__(self, *args, formatter_class=None, **kwargs):
        formatter_class = formatter_class if formatter_class is not None else RawDescriptionHelpFormatter
        super(ArgumentParser, self).__init__(*args, formatter_class=formatter_class, **kwargs)

    def error(self, message: str):
        self.print_usage(stderr)
        self.exit(
            2,
            gettext(f"{self.prog}: error: {message}\n"),
        )
