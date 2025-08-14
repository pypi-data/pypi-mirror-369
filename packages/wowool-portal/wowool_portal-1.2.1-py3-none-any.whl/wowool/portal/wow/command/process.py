from argparse import Namespace

from wowool.wow import CLI as WowCommonCLI

from wowool.portal.client import Pipeline, Portal
from wowool.portal.client.error import ClientError


class _PipelineWrapper(Pipeline):
    def __init__(self, *args, **kwargs):
        super(_PipelineWrapper, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return super(_PipelineWrapper, self).__call__(*args, **kwargs)


class CLI(WowCommonCLI):
    def __init__(self, local_kwargs):
        super(CLI, self).__init__(local_kwargs)
        api_key = self.kwargs["api_key"]
        host = self.kwargs["host"]
        pipeline_name = self.kwargs["pipeline"] if "pipeline" in self.kwargs else None
        assert api_key, "API key is required. Pass it with the '-k' option or set the environment variable 'WOWOOL_PORTAL_API_KEY'"
        self.tool = self.kwargs["tool"] if "tool" in self.kwargs else "raw"
        self.portal = Portal(host=host, api_key=api_key)
        if self.tool != "list":
            if not pipeline_name:
                raise ClientError("Pipeline name is required. Pass it with the '-p' option")
            self.pipeline = _PipelineWrapper(name=pipeline_name, portal=self.portal)


def command(arguments: Namespace):
    cli = CLI(dict(arguments._get_kwargs()))
    return cli.run()
