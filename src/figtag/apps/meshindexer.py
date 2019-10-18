from typing import Any
from figtag.manage import Cog
from figtag.meshindexer import meshindexer


class MeshIndexer(Cog):  # pragma: no cover
    @staticmethod
    def initialize(arg_parse: Any) -> None:
        parser = arg_parse.add_parser(
            "meshindexer",
            help=('Extract MeSH keywords from figure legend texts')
        )

        required = parser.add_argument_group('required arguments')
        required.add_argument(
            '-figure-captions-file', dest='figure_captions_file',
            action='store', required=True,
            help=('Name of the file contains two tab separated '
                  'columns: row number and figure captions'))

        parser.add_argument(
            '-o', dest='output_list', action='store', default='-',
            help='path to output list of keywords')

        parser.set_defaults(func=MeshIndexer.execute)

    @staticmethod
    def execute(args: Any) -> int:
        meshindexer(args.figure_captions_file, args.output_list)
        return 0
