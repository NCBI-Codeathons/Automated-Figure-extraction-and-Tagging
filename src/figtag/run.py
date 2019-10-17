from figtag.classifier import classifier
from figtag.imgsplitter import imgsplitter, OPENI_URL
from figtag.indexer import indexer
from figtag.openiparser import openiparser

from figtag.utils._filesystem import create_folder, Path

import csv
from os import path
import sys
from typing import Any, List


SUCCESS = 0
INVALID_ARGS = 2
OPENI_PARSER_FAILURE = 10


class _FigTagRunner():
    def __init__(self, output_folder: str):
        create_folder(output_folder)
        self._output_folder = output_folder

    def run(self, query: str, model_path: str) -> int:
        openi_output_list = self._call_openiparser(query)
        if not openi_output_list:
            return OPENI_PARSER_FAILURE

        split_image_folder = self._split_images(openi_output_list)

        image_cluster_list = self._cluster_images(split_image_folder)

        index_file = self._create_image_index(
            openi_output_list, image_cluster_list, split_image_folder)

        print('Index file: {}'.format(index_file))

        return SUCCESS

    def _call_openiparser(self, query: str) -> Path:
        openi_output_list: Path = path.join(self._output_folder, 'openi_output_list.tsv')
        try:
            openiparser(query, openi_output_list)
            return openi_output_list
        except Exception as err:
            print("An error occurred: " + str(err), file=sys.stderr)
            return None

    def _split_images(self, openi_output_list: Path) -> Path:
        with open(openi_output_list) as csvfile:
            has_header = csv.Sniffer().has_header(csvfile.read(2048))
            csvfile.seek(0)
            data_reader = csv.reader(csvfile)
            if has_header:
                next(data_reader, None)

            for row in data_reader:
                self._split_image(row)

    def _split_image(self, row: List[Any]) -> None:
        uid, img_path, fig_num, caption = row
        full_url = path.join(OPENI_URL, img_path)
        imgsplitter(full_url, uid)

    def _cluster_images(self, split_image_folder: Path) -> Path:
        pass
        classifier('image_path', 'model_path', 'output')

    def _create_image_index(self,
                            image_list: Path, image_clusters: Path,
                            image_folder: Path) -> Path:
        pass
        indexer('image_list', 'image_clusters', 'image_folder', 'database_file ouput')


def run(query: str, model_path: str, output_folder: str) -> int:
    """
    Starts with parameters openi query, model file location, and output file
    Call openiparser to get the list of tuples <img url,uid,caption,figid> and save to a file
    Iterate over the images
        call imgsplitter with a image url and uid and tell it where to store the output images
    Iterate over the folder where `imgsplitter` saved the images
        call classifier with an image file path, and get cluster id
    Save image path, cluster id in a list
    Call indexer with the list output by openiparser, the list of image, cluster id,
            and the path to such images
    Indexer creates an DB in a location provided as parameter
    """
    try:
        figtagrunner = _FigTagRunner(output_folder)
    except ValueError as err:
        print("An error occurred: " + str(err), file=sys.stderr)
        return INVALID_ARGS

    return figtagrunner.run(query, model_path)
