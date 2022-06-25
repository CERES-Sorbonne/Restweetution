from typing import List, Optional

from pydantic import BaseModel

from restweetution.models.twitter.media import Media
from restweetution.models.twitter.place import Place
from restweetution.models.twitter.poll import Poll
from restweetution.models.stream_rule import StreamRule
from restweetution.models.twitter.tweet import RestTweet
from restweetution.models.twitter.user import User


class BulkData(BaseModel):
    rules: Optional[List[StreamRule]] = []
    users: Optional[List[User]] = []
    tweets: Optional[List[RestTweet]] = []
    places: Optional[List[Place]] = []
    media: Optional[List[Media]] = []
    polls: Optional[List[Poll]] = []

    def __add__(self, other):
        self_dict = self.dict()
        other_dict = other.dict()

        for key in self_dict:
            self_dict[key].extend(other_dict[key])

        return BulkData(**self_dict)
