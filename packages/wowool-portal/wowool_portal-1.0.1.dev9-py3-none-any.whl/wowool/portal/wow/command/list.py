from argparse import Namespace
from wowool.portal.client import Portal


def command(arguments: Namespace):
    portal = Portal(host=arguments.host, api_key=arguments.api_key)
    print(portal.pipelines)
    for pipeline in portal.pipelines:
        print(pipeline)
