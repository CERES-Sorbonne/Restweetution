import io
from typing import Optional

from restweetution.models.twitter import Media


class DownloadedMedia(Media):
    sha1: str
    format: str
    bytes_: Optional[io.BytesIO]

    class Config:
        arbitrary_types_allowed = True
