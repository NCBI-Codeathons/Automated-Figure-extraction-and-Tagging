import sqlite3
import pandas as pd
import os


def indexer(image_clusters: str, image_folder: str, openi_data: str, mesh_terms: str, database_file):
    db = database_file
    conn = sqlite3.connect(db)

    raw = pd.read_csv(openi_data, '\t', header=0, index_col=0)

    raw.to_sql('users', con=conn, if_exists='replace')

    cmd = 'ls ' + image_folder + ' > images.txt'

    os.system(cmd)

    calcData = pd.read_csv('images.txt',
                           '\t',
                           header=None).rename(columns={0: 'file_name'})
    calcData['idx'] = calcData.file_name.apply(lambda x: x.split('_')[0])
    calcData['img_id'] = calcData.file_name.apply(lambda x: x.split('_')[-1].split('.')[-2])
    calcData = calcData[['idx', 'img_id']].set_index('idx')

    for data in [image_clusters, mesh_terms]:

        calcData = calcData.join(pd.read_csv(data,
                                             '\t',
                                             header=0,
                                             index_col=0),
                                 on='idx')

    calcData.to_sql('calcData', con=conn, if_exists='replace')

    conn.commit()
    conn.close()
