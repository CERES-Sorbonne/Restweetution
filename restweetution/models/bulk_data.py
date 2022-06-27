from typing import List, Optional, Dict

from pydantic import BaseModel

from restweetution.models.twitter.media import Media
from restweetution.models.twitter.place import Place
from restweetution.models.twitter.poll import Poll
from restweetution.models.stream_rule import StreamRule
from restweetution.models.twitter.tweet import RestTweet
from restweetution.models.twitter.user import User


class BulkData(BaseModel):
    rules: Dict[str, StreamRule] = {}
    users: Dict[str, User] = {}
    tweets: Dict[str, RestTweet] = {}
    places: Dict[str, Place] = {}
    media: Dict[str, Media] = {}
    polls: Dict[str, Poll] = {}

    def __add__(self, other):
        self_dict = self.dict()
        other_dict = other.dict()

        for key1 in other_dict:
            if key1 == 'rules':
                for key2 in other_dict[key1]:
                    if key2 not in self_dict[key1]:
                        self_dict[key1][key2] = other_dict[key1][key2]
                    else:
                        self_dict[key1][key2]['tweet_ids'].extend(other_dict[key1][key2]['tweet_ids'])
            else:
                for key2 in other_dict[key1]:
                    self_dict[key1][key2] = other_dict[key1][key2]

        return BulkData(**self_dict)


