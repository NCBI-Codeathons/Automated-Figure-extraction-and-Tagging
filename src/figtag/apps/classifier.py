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
            '-vae-model-file', dest='vae_model_path', action='store', required=True,
            help='The path to the file where the VAE model is saved')
        required.add_argument(
            '-kmeans-model-file', dest='kmeans_model_path', action='store', required=True,
            help='The path to the file where the K-Means model is saved')

        parser.add_argument(
            '-o', dest='output', action='store', default='-',
            help='where to output the cluster id')

        parser.set_defaults(func=Classifier.execute)

    @staticmethod
    def execute(args: Any) -> int:
        cluster_id = classifier(args.image_path, args.vae_model_path, args.kmeans_model_path)
        result_fmt = "cluster_id {}\n".format(cluster_id)
        if args.output == '-':
            print(result_fmt)
        else:
            with open(args.output, 'wt') as fcluster:
                fcluster.write(result_fmt)

        return 0
