from typing import Any
from figtag.manage import Cog
from figtag.openiparser import openiparser


class OpenIParser(Cog):  # pragma: no cover
    @staticmethod
    def initialize(arg_parse: Any) -> None:
        parser = arg_parse.add_parser(
            "openiparser",
            help=('Performs a query against OpenI and output a list of tuples: '
                  '<caption,img_url,uid>')
        )

        required = parser.add_argument_group('required arguments')
        required.add_argument(
            '-query', dest='query', action='store', required=True,
            help='The query to perform against OpenI')

        parser.add_argument(
            '-o', dest='output_list', action='store', default='-',
            help='path to output list of tuples')

        parser.set_defaults(func=OpenIParser.execute)

    @staticmethod
    def execute(args: Any) -> int:
        openiparser(args.query, args.output_list)
        return 0
