from typing import Any
from figtag.manage import Cog
from figtag.indexer import indexer


class Indexer(Cog):  # pragma: no cover
    @staticmethod
    def initialize(arg_parse: Any) -> None:
        parser = arg_parse.add_parser(
            "indexer",
            help=('Creates a DB containing all the artifacts produced '
                  'by the other apps in this package and creates an index '
                  'using the figure id as key')
        )

        required = parser.add_argument_group('required arguments')
        required.add_argument(
            '-parsed-image-list', dest='image_list', action='store', required=True,
            help='The path to the file containing image URLs  ')

        required.add_argument(
            '-cluster-image-list', dest='image_clusters', action='store', required=True,
            help='The path to the file containing one image per line and '
                 'the id of the cluster the image belongs to')

        required.add_argument(
            '-image-folder', dest='image_folder', action='store', required=True,
            help='The path to the folder containing the image files')

        required.add_argument(
            '-o', dest='database_file', action='store', required=True,
            help='Path to the database file that will be produced')

        parser.set_defaults(func=Indexer.execute)

    @staticmethod
    def execute(args: Any) -> int:
        indexer(args.image_list, args.image_clusters, args.image_folder, args.database_file)
        return 0
