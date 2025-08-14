from argparse import Namespace

import wowool.portal.wow.command.list as list
import wowool.portal.wow.command.components as components
import wowool.portal.wow.command.process as process
import wowool.portal.wow.command.version as version


class CommandFactory:
    def __call__(self, arguments: Namespace):
        if arguments.version:
            return version.command
        elif arguments.tool == "list":
            return list.command
        elif arguments.tool == "components":
            return components.command
        else:
            return process.command
