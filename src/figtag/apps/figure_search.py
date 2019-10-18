from typing import Any
from figtag.manage import Cog
from figtag.figure_search import querier


class FigureSearch(Cog):  # pragma: no cover
    @staticmethod
    def initialize(arg_parse: Any) -> None:
        parser = arg_parse.add_parser(
            "figure-search",
            help=('Performs a query against the figure index created by our pipeline')
        )

        required = parser.add_argument_group('required arguments')
        required.add_argument(
            '-query', dest='query', action='store', required=True,
            help='The query to perform against the index')

        required.add_argument(
            '-index', dest='index_file', action='store', required=True,
            help='path to the index file')

        parser.set_defaults(func=FigureSearch.execute)

    @staticmethod
    def execute(args: Any) -> int:
        querier(args.query, args.index_file)
        return 0
