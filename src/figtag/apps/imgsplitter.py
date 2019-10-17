from typing import Any
from figtag.manage import Cog
from figtag.imgsplitter import imgsplitter


class ImageSplitter(Cog):  # pragma: no cover
    @staticmethod
    def initialize(arg_parse: Any) -> None:
        parser = arg_parse.add_parser(
            "imgsplitter",
            help=('Splits an image into multiple images if the original '
                  'image is a multi-panel image. Otherwise, it outputs '
                  'the original image')
        )

        required = parser.add_argument_group('required arguments')
        required.add_argument(
            '-image-url', dest='image_url', action='store', required=True,
            help='The URL to the image to split if it is a multi-panel image')

        required.add_argument(
            '-uid', dest='image_uid', action='store', required=True,
            help='The unique id of an image. It consists of the id of the paper '
                 'where the image was found and the number of the figure in '
                 'that paper')

        required.add_argument(
            '-o', dest='output_folder', action='store', required=True,
            help='Path to the folder where to output the image(s)')

        parser.set_defaults(func=ImageSplitter.execute)

    @staticmethod
    def execute(args: Any) -> int:
        imgsplitter(args.image_url, args.image_uid, args.output_folder)
        return 0
