import asyncio
import json
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

from restweetution import config_loader
from restweetution.models.storage.downloaded_media import DownloadedMedia

media_dir = '/home/felixalie/collectes_twitter/IVG/media'

conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))


# def chunker(seq, size):
#     return (seq[pos:pos + size] for pos in range(0, len(seq), size))


async def launch():
    storage = conf.build_storage()
    base = Path(media_dir)

    sha1_file = base / 'sha1.json'

    with open(sha1_file) as f:
        key_to_sha1 = json.load(f)
        media_keys = key_to_sha1.keys()

    res = await storage.get_medias(media_keys=media_keys)

    media_keys = [r.media_key for r in res]

    downloaded = []
    for media_key in media_keys:
        sha1 = key_to_sha1[media_key].split('.')[0]
        format_ = key_to_sha1[media_key].split('.')[1]
        d = DownloadedMedia(media_key=media_key, sha1=sha1, format=format_)
        downloaded.append(d)

    await storage.save_downloaded_medias(downloaded)


asyncio.run(launch())
