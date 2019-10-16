from typing import Any
from figtag.manage import Cog
from figtag.classifier import classifier


class Classifier(Cog):  # pragma: no cover
    @staticmethod
    def initialize(arg_parse: Any) -> None:
        parser = arg_parse.add_parser(
            "classifier",
            help=('Classifies an image by assigning it to a cluster')
        )

        required = parser.add_argument_group('required arguments')
        required.add_argument(
            '-image-path', dest='image_path', action='store', required=True,
            help='The path to the image to classify')
        required.add_argument(
            '-model-file', dest='model_path', action='store', required=True,
            help='The path to the file where the model was saved')

        parser.add_argument(
            '-o', dest='output', action='store', default='-',
            help='where to output the cluster id')

        parser.set_defaults(func=Classifier.execute)

    @staticmethod
    def execute(args: Any) -> int:
        classifier(args.image_path, args.model_path, args.output)
        return 0
