from argparse import Namespace
from wowool.portal.client import Portal


def command(arguments: Namespace):
    portal = Portal(host=arguments.host, api_key=arguments.api_key)
    for component in portal.components:
        print(f"{component.name:<35}| {component.type:<8}| {component.short_description}")
