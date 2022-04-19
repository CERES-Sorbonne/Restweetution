import logging
import sys
import tempfile

import requests
import urllib.parse
import m3u8
from pathlib import Path
import re
import ffmpeg
import shutil

from restweetution.models.media import MediaType


class TwitterDownloader:
    """
    Utility class that allows to download videos and gifs
    """
    video_player_prefix = 'https://twitter.com/i/videos/tweet/'
    video_api = 'https://api.twitter.com/1.1/videos/tweet/config/'
    tweet_data = {}

    def __init__(self):
        self.requests = requests.Session()
        self.tweet_id = None
        self.logger = logging.getLogger("Storage")

    def _download_mp4(self):
        video_host, playlist = self.__get_playlist()

        plist = playlist.playlists[0]

        with tempfile.TemporaryDirectory() as storage:
            resolution_file = str(Path(storage) / Path('output.mp4'))

            playlist_url = video_host + plist.uri

            ts_m3u8_response = self.requests.get(playlist_url, headers={'Authorization': None})
            ts_m3u8_parse = m3u8.loads(ts_m3u8_response.text)

            ts_list = []

            ts_file = requests.get(video_host + ts_m3u8_parse.segment_map['uri'])
            ts_path = Path(storage) / Path(f"init.mp4")
            ts_list.append(ts_path)
            ts_path.write_bytes(ts_file.content)

            for index, ts_uri in enumerate(ts_m3u8_parse.segments.uri):
                ts_file = requests.get(video_host + ts_uri)
                ts_path = Path(storage) / Path(f"segment-{index + 1}.m4s")
                ts_list.append(ts_path)

                ts_path.write_bytes(ts_file.content)

            ts_full_file = str(Path(storage) / Path('ts_file.ts'))

            # Shamelessly taken from https://stackoverflow.com/questions/13613336/python-concatenate-text-files/27077437#27077437
            with open(str(ts_full_file), 'wb') as wfd:
                for f in ts_list:
                    with open(f, 'rb') as fd:
                        shutil.copyfileobj(fd, wfd, 1024 * 1024 * 10)

            ffmpeg \
                .input(ts_full_file) \
                .output(resolution_file, acodec='copy', vcodec='libx264', format='mp4',
                        loglevel='error') \
                .overwrite_output() \
                .run()

            with open(resolution_file, 'rb') as f:
                return f.read()

    def _download_gif(self):
        video_file = self.__get_playlist(video=False)
        with tempfile.TemporaryDirectory() as storage:
            input = str(Path(storage) / Path('input.mp4'))
            output = str(Path(storage) / Path('output.mp4'))
            with open(input, 'wb') as f:
                f.write(video_file.content)
            ffmpeg.input(input).filter('scale', 350, -2).output(output, format='mp4', vcodec='libx264', crf=18, preset='slow').overwrite_output().run()
            with open(output, 'rb') as f:
                return f.read()

    def download(self, tweet_id: str, media_type: MediaType = 'video') -> bytes:
        self.tweet_id = tweet_id
        # Get the bearer token
        self.__get_bearer_token()

        try:
            if media_type == 'animated_gif':
                return self._download_gif()
            else:
                return self._download_mp4()
        except:
            self.logger.warning("There was an error downloading media for tweet: " + tweet_id)

    def __get_bearer_token(self):
        video_player_url = self.video_player_prefix + self.tweet_id
        video_player_response = self.requests.get(video_player_url).text

        js_file_url = re.findall('src="(.*js)', video_player_response)[0]
        js_file_response = self.requests.get(js_file_url).text

        bearer_token_pattern = re.compile('Bearer ([a-zA-Z0-9%-])+')
        bearer_token = bearer_token_pattern.search(js_file_response)
        bearer_token = bearer_token.group(0)
        self.requests.headers.update({'Authorization': bearer_token})
        self.__get_guest_token()

        return bearer_token

    def __get_playlist(self, video: bool = True):
        player_config = self.requests.get(self.video_api + self.tweet_id + '.json').json()

        if 'errors' not in player_config:
            resource_url = player_config['track']['playbackUrl']

        else:
            print('[-] Rate limit exceeded. Could not recover. Try again later.')
            sys.exit(1)

        resource = self.requests.get(resource_url)

        # if it's a gif then there is no m3u8 and it's only a mp4 file
        if not video:
            return resource
        else:
            m3u8_url_parse = urllib.parse.urlparse(resource_url)
            video_host = m3u8_url_parse.scheme + '://' + m3u8_url_parse.hostname

            m3u8_parse = m3u8.loads(resource.text)

            return [video_host, m3u8_parse]

    def __get_guest_token(self):
        res = self.requests.post("https://api.twitter.com/1.1/guest/activate.json").json()
        self.requests.headers.update({'x-guest-token': res.get('guest_token')})


if __name__ == "__main__":
    td = TwitterDownloader()
    res = td.download("1450730417879912449", media_type='animated_gif')
    # res = td.download("1450769351238369281")
    with open('output.mp4', 'wb') as f:
        f.write(res)