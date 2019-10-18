from figtag.utils._filesystem import list_files, Path

import sqlite3
import pandas as pd
from os import path


def indexer(openi_data: Path, image_folder: Path,
            image_clusters: Path, mesh_terms: Path,
            database_file: Path):

    db = database_file
    conn = sqlite3.connect(db)

    raw = pd.read_csv(openi_data, '\t', header=0, index_col=0)

    raw.to_sql('users', con=conn, if_exists='replace')

    image_files = list_files(image_folder, r'.*\.png$')
    image_list = [path.basename(img_path) for img_path in image_files]

    calcData = pd.DataFrame({'file_name': image_list})

    calcData['idx'] = calcData.file_name.apply(lambda x: x.split('_')[1])
    calcData.idx = calcData.idx.astype(int)
    calcData['img_id'] = calcData.file_name.apply(lambda x: x.split('_')[-1].split('.')[-2])
    calcData.img_id = calcData.img_id.astype(int)
    calcData = calcData[['idx', 'img_id']]

    clusters = pd.read_csv(image_clusters,
                           '\t',
                           header=None).rename(columns={0: 'path', 1: 'cid'})
    clusters['idx'] = clusters.path.apply(lambda x: x.split('_')[1])
    clusters['img_id'] = clusters.path.apply(lambda x: x.split('_')[-1].split('.')[-2])
    clusters.idx = clusters.idx.astype(int)
    clusters.img_id = clusters.img_id.astype(int)
    clusters = clusters[['idx', 'img_id', 'cid']]

    meshdf = pd.read_csv(mesh_terms,
                         '\t',
                         header=None).rename(columns={0: 'idx', 1: 'mesh'})
    meshdf.idx = clusters.idx.astype(int)

    calcData = calcData.join(meshdf.set_index('idx'),
                             on='idx',
                             how='left')
    calcData = calcData.join(clusters.set_index(['idx', 'img_id']),
                             on=['idx', 'img_id'],
                             how='right')

    calcData.to_sql('calcData', con=conn, if_exists='replace')

    conn.commit()
    conn.close()
