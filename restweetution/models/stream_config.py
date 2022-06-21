from typing import Optional, Union, Callable

from pydantic import BaseModel

from restweetution.models.config.query_params_config import BASIC_CONFIG
from restweetution.models.tweet_config import QueryParams


class StreamConfig(BaseModel):
    token: str
    tweet_config: Optional[QueryParams] = BASIC_CONFIG
    max_retries: Optional[int] = 3
    verbose: Optional[bool] = False
    download_media: Optional[bool] = True
    average_hash: Optional[bool] = False
    fetch_minutes: bool = False
    custom_handler: Optional[Union[Callable]]

    # allows to use custom classes as types
    class Config:
        arbitrary_types_allowed = True
