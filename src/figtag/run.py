from figtag.classifier import classifier
from figtag.imgsplitter import imgsplitter, OPENI_URL
from figtag.indexer import indexer
from figtag.openiparser import openiparser

from figtag.utils._filesystem import create_folder, Path

import csv
import logging
from os import path
import sys
from typing import Any, List
import urllib.parse


SUCCESS = 0
INVALID_ARGS = 2
PROCESSING_FAILURE = 10


class _FigTagRunner():
    def __init__(self, output_folder: str, file_limit: int):
        create_folder(output_folder)
        self._output_folder = output_folder
        if file_limit < 0:
            raise ValueError('The max number of files to process must be non-negative')
        self._file_limit = file_limit
        self.logger = logging.getLogger('_FigTagRunner')

    def run(self, query: str, model_path: str) -> int:
        self.logger.info('Running Open-I query')
        openi_output_list = self._call_openiparser(query)
        if not openi_output_list:
            return PROCESSING_FAILURE

        self.logger.info('Splitting images (if they are multipanel)')
        split_image_folder = self._split_images(openi_output_list)
        if not split_image_folder:
            return PROCESSING_FAILURE
        self.logger.info("Processed images are in folder %s", split_image_folder)

        image_cluster_list = self._cluster_images(split_image_folder)

        index_file = self._create_image_index(
            openi_output_list, image_cluster_list, split_image_folder)

        print('Index file: {}'.format(index_file))

        return SUCCESS

    def _call_openiparser(self, query: str) -> Path:
        if path.isfile(query) and path.exists(query):
            self.logger.info('Using existing file {}'.format(query))
            return query

        openi_output_list: Path = path.join(self._output_folder, 'openi_output_list.tsv')
        self.logger.info('Saving Open-I results to {}'.format(openi_output_list))

        try:
            openiparser(query, openi_output_list)
            return openi_output_list
        except Exception as err:
            print("An error occurred: " + str(err), file=sys.stderr)
            return None

    def _split_images(self, openi_output_list: Path) -> Path:
        img_output_folder: str = None
        try:
            with open(openi_output_list) as csvfile:
                has_header = csv.Sniffer().has_header(csvfile.read(2048))
                csvfile.seek(0)
                data_reader = csv.reader(csvfile, delimiter='\t')
                if has_header:
                    next(data_reader, None)

                img_output_folder: Path = path.join(self._output_folder, 'images_split')
                create_folder(img_output_folder)

                files_processed = 0
                for row in data_reader:
                    self._split_image(row, img_output_folder)
                    if self._file_limit > 0:
                        files_processed += 1
                        if files_processed >= self._file_limit:
                            self.logger.info(
                                'Processed {} files'.format(files_processed))
                            break

        except Exception as err:
            print("An error occurred: " + str(err), file=sys.stderr)
            return None

        return img_output_folder

    def _split_image(self, row: List[Any], img_output_folder: Path) -> None:
        idx, uid, img_path, _, _ = row
        if path.isfile(img_path) and path.exists(img_path):
            full_url = img_path
        else:
            full_url = urllib.parse.urljoin(OPENI_URL, img_path)
        image_uid = uid + '_' + idx
        self.logger.info('Processing file {}'.format(full_url))
        imgsplitter(full_url, image_uid, img_output_folder)

    def _cluster_images(self, split_image_folder: Path) -> Path:
        classifier('image_path', 'model_path', 'output')
        return '/dev/null'

    def _create_image_index(self,
                            image_list: Path, image_clusters: Path,
                            image_folder: Path) -> Path:
        # indexer('image_clusters', 'image_folder',
        #         'raw_data', 'mesh_terms',
        #         'database_file')
        return '/dev/null'


def run(query: str, model_path: str, output_folder: str, file_limit: int = 0) -> int:
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
        figtagrunner = _FigTagRunner(output_folder, file_limit)
    except ValueError as err:
        print("An error occurred: " + str(err), file=sys.stderr)
        return INVALID_ARGS

    return figtagrunner.run(query, model_path)
