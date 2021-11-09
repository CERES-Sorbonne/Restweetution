import concurrent.futures
import hashlib

import requests

import pandas as pd
import os

ROOT_FOLDER = r"C:\Users\Orion\Documents\Projets\CERES\PMA\OutputCSV"
OUTPUT_FOLDER = r"C:\Users\Orion\Documents\Projets\CERES\PMA\OutputImages"

ids = [1381367533, 1028886934523977728, 1146074724]
names = ['Enfantdabord2', 'OnNaQuUneMaman', 'antoinne92']


def save_image(url, id, text, name):
    type = url.split('.')[-1]
    res: bytes = requests.get(url).content
    signature = hashlib.sha1(res).hexdigest()
    with open(os.path.join(OUTPUT_FOLDER, name, f'{signature}.{type}'), 'wb') as f:
        f.write(res)
    with open(os.path.join(OUTPUT_FOLDER, name, f'{signature}.txt'), 'a') as f:
        f.write(f'{id} {text}\n')


def download_image(row, name):
    text = row['text']
    id = row['id']
    images_url = row['images_url'].split(' ')
    for url in images_url:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(save_image, url, id, text, name)


if __name__ == "__main__":
    for name in names:
        df = pd.read_csv(os.path.join(ROOT_FOLDER, 'cleaned', f'{name}.csv'), sep=";", header=0, index_col=None)
        no_images = df['images_url'].isnull()
        subset = df[~no_images]
        subset.apply(download_image, args=[name], axis=1)


