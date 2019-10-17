from typing import Any
from figtag.manage import Cog
from figtag.run import run

import logging
from os import environ


class Runner(Cog):  # pragma: no cover
    @staticmethod
    def initialize(arg_parse: Any) -> None:
        parser = arg_parse.add_parser(
            "run",
            help=('Driver script to call all the relevant components '
                  'and produce an image index')
        )

        required = parser.add_argument_group('required arguments')
        required.add_argument(
            '-query', dest='query', action='store', required=True,
            help='The query to perform against OpenI')
        required.add_argument(
            '-model-file', dest='model_path', action='store', required=True,
            help='The path to the file where the model was saved')

        parser.add_argument(
            '-o', dest='output_folder', action='store', default='',
            help='Path to the folder where to put all output files')

        parser.add_argument(
            '-file-limit', dest='file_limit', action='store', default=0,
            help='Max number of files to process', type=int)

        parser.set_defaults(func=Runner.execute)

    @staticmethod
    def execute(args: Any) -> int:
        FIGTAG_LOGLEVEL = environ.get('FIGTAG_LOGLEVEL', 'WARNING').upper()
        logging.basicConfig(level=FIGTAG_LOGLEVEL)
        return run(args.query, args.model_path, args.output_folder, args.file_limit)
