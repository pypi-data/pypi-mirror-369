import sys
from wowool.portal.client.cli import CLI
from wowool.portal.wow.argument_parser import ArgumentParser
from wowool.portal.wow.command import CommandFactory


def main(*argv):

    # logging.getLogger("wowool.portal.client.service").setLevel(logging.DEBUG)
    argv = argv or sys.argv[1:]
    cli = CLI(ArgumentParser(), CommandFactory())
    cli(*argv)


if "__main__" == __name__:
    main()
