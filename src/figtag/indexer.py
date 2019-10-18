import sqlite3
import logging
import pandas as pd
import os


_LOGGER = logging.getLogger('indexer')


def indexer(openi_data: str, image_folder: str,
            image_clusters: str, mesh_terms: str,
            database_file: str):
    _LOGGER.info("Creating/Opening DB {}".format(database_file))
    db = database_file
    conn = sqlite3.connect(db)

    _LOGGER.info("Saving OpenI data from {}".format(openi_data))
    raw = pd.read_csv(openi_data, '\t', header=0, index_col=0)

    raw.to_sql('users', con=conn, if_exists='replace')

    cmd = 'ls ' + image_folder + ' > images.txt'

    os.system(cmd)

    _LOGGER.info("Saving image list from {}".format(image_folder))
    calcData = pd.read_csv('images.txt',
                           '\t',
                           header=None).rename(columns={0: 'file_name'})
    calcData['idx'] = calcData.file_name.apply(lambda x: x.split('_')[1])
    calcData.idx = calcData.idx.astype(int)
    calcData['img_id'] = calcData.file_name.apply(lambda x: x.split('_')[-1].split('.')[-2])
    calcData = calcData[['idx', 'img_id']].set_index('idx')

    if image_clusters:
        _LOGGER.info("Joining Image clusters data from {}".format(image_clusters))
        calcData = _join_data(image_clusters, calcData)

    if mesh_terms:
        _LOGGER.info("Joining MeSH terms from {}".format(mesh_terms))
        calcData = _join_data(mesh_terms, calcData)

    calcData.to_sql('calcData', con=conn, if_exists='replace')

    conn.commit()
    conn.close()


def _join_data(data, calcData):
    return calcData.join(pd.read_csv(data,
                                     '\t',
                                     header=0,
                                     index_col=0),
                         on='idx')
