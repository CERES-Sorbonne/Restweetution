import io
from typing import Optional

from pydantic import BaseModel

from restweetution.models.twitter import Media


class DownloadedMedia(BaseModel):
    media_key: str
    sha1: str
    format: str
    media: Optional[Media]
    bytes_: Optional[io.BytesIO]

    class Config:
        arbitrary_types_allowed = True
