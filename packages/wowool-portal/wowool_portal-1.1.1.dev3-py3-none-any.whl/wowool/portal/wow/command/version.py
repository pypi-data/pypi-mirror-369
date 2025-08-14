from wowool.io.console import console

from wowool.portal import get_version


def command(**_):
    console.print(f"client version: {get_version()}")
    return 0
