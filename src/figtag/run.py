from figtag.classifier import _classify_image  # classifier
from figtag.imgsplitter import imgsplitter, OPENI_URL
from figtag.indexer import indexer
from figtag.openiparser import openiparser

from figtag.utils._filesystem import (
    create_folder, list_files, Path)

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

    def run(self, query: str, model_file: Path, mesh_terms_file: Path) -> int:
        try:
            return self._try_run(query, model_file, mesh_terms_file)
        except Exception as err:
            print("An error occurred: " + str(err), file=sys.stderr)
            return PROCESSING_FAILURE

    def _try_run(self, query: str, model_file: Path, mesh_terms_file: Path) -> int:
        self.logger.info('Running Open-I query')
        openi_output_list = self._parse_openi_query(query)
        if not openi_output_list:
            return PROCESSING_FAILURE

        self.logger.info('Processing images (multipanel ones will be split)')
        split_image_folder = self._split_images(openi_output_list)
        if not split_image_folder:
            return PROCESSING_FAILURE
        self.logger.info("Processed images are in folder %s", split_image_folder)

        self.logger.info('Classifying images')
        image_cluster_list = self._get_images_clusters(split_image_folder, model_file)
        if not image_cluster_list:
            return PROCESSING_FAILURE
        self.logger.info("Information about images and the clusters they belong to "
                         "can be found in '%s'", image_cluster_list)

        self.logger.info('Indexing data')
        index_file = self._create_image_index(
            openi_output_list, split_image_folder,
            image_cluster_list, mesh_terms_file)
        if not index_file:
            return PROCESSING_FAILURE
        print('Index file: {}'.format(index_file))

        return SUCCESS

    def _parse_openi_query(self, query: str) -> Path:
        if path.isfile(query) and path.exists(query):
            self.logger.info('Using existing file {}'.format(query))
            return query

        openi_output_list: Path = path.join(self._output_folder, 'openi_output_list.tsv')
        self.logger.info('Saving Open-I results to {}'.format(openi_output_list))

        openiparser(query, openi_output_list)
        return openi_output_list

    def _split_images(self, openi_output_list: Path) -> Path:
        img_output_folder: str = None
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

    def _get_images_clusters(self, split_image_folder: Path, model_file: str) -> Path:
        # classifier('image_path', 'model_file', 'output')
        image_files = list_files(split_image_folder, r'.*\.png$')

        if not image_files:
            self.logger.error("No PNG images found in '%s'", split_image_folder)
            return None

        image_cluster_list: Path = path.join(self._output_folder, 'image_cluster_list.tsv')

        with open(image_cluster_list, 'wt') as imgclusterlst:
            for image_path in image_files:
                cluster_id = _classify_image(image_path, model_file)
                imgclusterlst.write('{}\t{}\n'.format(
                    path.basename(image_path), cluster_id))

        return image_cluster_list

    def _get_image_cluster(self, image_path: Path) -> str:
        return _classify_image(image_path, "model_file")

    def _create_image_index(self,
                            openi_data: Path, image_folder: Path,
                            image_clusters: Path, mesh_terms_file: Path) -> Path:
        index_file: Path = path.join(self._output_folder, 'index.db')

        indexer(openi_data, image_folder,
                image_clusters, mesh_terms_file,
                index_file)
        return index_file


def run(query: str, model_file: Path, mesh_terms_file: Path,
        output_folder: Path, file_limit: int = 0) -> int:
    """
    Takes an open-i query and a classification model file, and
    produces an index file
    """
    try:
        figtagrunner = _FigTagRunner(output_folder, file_limit)
    except ValueError as err:
        print("An error occurred: " + str(err), file=sys.stderr)
        return INVALID_ARGS

    return figtagrunner.run(query, model_file, mesh_terms_file)
