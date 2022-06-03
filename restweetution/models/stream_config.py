from pydantic import BaseModel
from typing import Optional, Union, Callable

from restweetution.models.examples_config import BASIC_CONFIG
from restweetution.models.tweet_config import TweetConfig


class CollectorConfig(BaseModel):
    token: str
    tweet_config: Optional[TweetConfig] = BASIC_CONFIG
    max_retries: Optional[int] = 3
    verbose: Optional[bool] = False
    download_media: Optional[bool] = True
    average_hash: Optional[bool] = False
    custom_handler: Optional[Union[Callable]]

    # allows to use custom classes as types
    class Config:
        arbitrary_types_allowed = True
