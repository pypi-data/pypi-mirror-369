from functools import wraps
from logging import getLogger
from sys import exit, stderr

from wowool.io.console import console

from wowool.portal.client.environment import apply_environment_variables
from wowool.portal.client.error import PortalApiError, PortalClientError

logger = getLogger(__name__)


def display_help_if_no_args(parse_arguments):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args):
                func(*args, **kwargs)
            else:
                parse_arguments.print_help(stderr)
                exit(2)

        return wrapper

    return decorator


def handle_errors(prog: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except PortalApiError as error:
                # logger.exception(error)
                api_error_type = f"- {error.type}" if error.type else ""
                console.print(
                    f"<prog>{prog}</prog>: <error>error</error> ({error.status_code} {api_error_type}): {error}",
                    file=stderr,
                )
                raise error
            except PortalClientError as error:
                # logger.exception(error)
                console.print(f"<prog>{prog}</prog>: <error>error</error>: {error}", file=stderr)
                exit(1)
            except Exception as error:
                logger.exception(error)
                exit(-1)

        return wrapper

    return decorator


class CLI:
    def __init__(self, argument_parser, command_factory):
        self.parser = argument_parser
        self._create_command = command_factory

    def __call__(self, *argv):
        @display_help_if_no_args(self.parser)
        @handle_errors(self.parser.prog)
        def run(*argv):
            arguments = self.parser.parse_args(argv)
            if not (hasattr(arguments, "create") and arguments.create) or arguments.version:
                apply_environment_variables(arguments)
            command = self._create_command(arguments)
            exit(command(arguments))

        run(*argv)
