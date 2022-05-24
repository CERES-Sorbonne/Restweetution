from typing import List, Optional

from pydantic import BaseModel

from restweetution.models.stream_rule import StreamRule
from restweetution.models.tweet import RestTweet
from restweetution.models.user import User


class BulkData(BaseModel):
    rules: Optional[List[StreamRule]] = []
    users: Optional[List[User]] = []
    tweets: Optional[List[RestTweet]] = []

    def __add__(self, other):
        self.rules.extend(other.rules)
        self.users.extend(other.users)
        self.tweets.extend(other.tweets)

        return self