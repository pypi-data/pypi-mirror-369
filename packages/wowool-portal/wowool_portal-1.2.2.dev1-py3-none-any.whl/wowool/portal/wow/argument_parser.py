from wowool.portal.client.argument_parser import (
    ArgumentParser as ArgumentParserBase,
)
from wowool.portal.client.defines import (
    WOWOOL_PORTAL_API_KEY_ENV_NAME,
    WOWOOL_PORTAL_HOST_ENV_NAME,
)

# fmt: off
class ArgumentParser(ArgumentParserBase):
    def __init__(self):
        """
        EyeOnText Wowool Portal Client
        usage:
          wow [options]

        example:
          wow -f test.txt -p english,entities -k [api-key]

        tools:

            --tool raw:           Display all linguistic information: language, tokens, concepts, sentences
            --tool json:          Display all linguistic information in JSON format. To pretty print, pipe the results ( | python -m tool.json )
            --tool stagger:       Display only the concepts in a JSON object
            --tool sequence:      Display a Wowoolian sequence from the input that can be used as a rule
            --tool stats:         Generate an analysis of your corpus
            --tool list:          List the available pipelines
            --tool components:    List the available components
        """
        super(ArgumentParserBase, self).__init__(prog="wow", description=ArgumentParser.__call__.__doc__)
        self.add_argument("--version"      ,  help="Version information", default=False, action="store_true")
        self.add_argument("-k", "--api-key",  help=f"API key, available via the Portal. Environment variable: {WOWOOL_PORTAL_API_KEY_ENV_NAME}")
        self.add_argument("--host"    ,       help=f"URL to the Portal. Environment variable: {WOWOOL_PORTAL_HOST_ENV_NAME}")
        self.add_argument("-p", "--pipeline", help="Name of the pipeline to process your documents")
        self.add_argument("-f", "--file"   ,  help="Folder or file to process")
        self.add_argument("-i", "--text"   ,  help="Input text to process")
        self.add_argument("-e","--encoding",  help="Encoding of the files to process, use 'auto' if you do not know the encoding", default="utf8")
        self.add_argument("-t", "--tool"   ,  help="Tool to run", choices=["raw", "json", "list", "sequence", "stagger", "text", "stats", "components","none"], default="raw")
        self.add_argument("--ignore-errors",  help="Ignore errors during processing", default=False, action="store_true")

# fmt: on
