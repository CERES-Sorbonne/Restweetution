from typing import Optional, List

from restweetution.models.linked.linked import Linked
from restweetution.models.linked.linked_media import LinkedMedia
from restweetution.models.rule import Rule
from restweetution.models.twitter import Tweet, Media, Poll, User


class LinkedTweet(Linked):
    def __init__(self, data, tweet: Tweet):
        super().__init__(data)
        self.tweet = tweet

    def get_media(self) -> List[LinkedMedia]:
        media_keys = self.tweet.get_media_keys()
        return [LinkedMedia(self.data, self.data.get_or_create_media(Media(media_key=key))) for key in media_keys]

    def get_polls(self) -> List[Poll]:
        poll_ids = self.tweet.get_poll_ids()
        return [self.data.get_or_create_poll(Poll(id=poll_id)) for poll_id in poll_ids]

    def get_retweeted_tweet(self) -> Optional[Tweet]:
        retweeted_id = self.tweet.get_retweeted_id()
        if not retweeted_id:
            return None
        return self.data.get_or_create_tweet(Tweet(id=retweeted_id))

    def get_quoted_tweet(self) -> Optional[Tweet]:
        quoted_id = self.tweet.get_quoted_id()
        if not quoted_id:
            return None
        return self.data.get_or_create_tweet(Tweet(id=quoted_id))

    def get_replied_to_tweet(self) -> Optional[Tweet]:
        replied_to_id = self.tweet.get_replied_to_id()
        if not replied_to_id:
            return None
        return self.data.get_or_create_tweet(Tweet(id=replied_to_id))

    def get_conversation_tweet(self) -> Optional[Tweet]:
        tweet_id = self.tweet.conversation_id
        if not tweet_id:
            return None
        return self.data.get_or_create_tweet(Tweet(id=tweet_id))

    def get_author_user(self) -> Optional[User]:
        author_id = self.tweet.author_id
        if not author_id:
            return None
        return self.data.get_or_create_user(User(id=author_id))

    def get_replied_user(self):
        user_id = self.tweet.in_reply_to_user_id
        if not user_id:
            return None
        return self.data.get_or_create_user(User(id=user_id))

    def get_rule_matches(self):
        return self.data.get_tweet_matches(self.tweet.id)

    def get_rules(self):
        matches = self.get_rule_matches()
        rules = [self.data.get_or_create_rule(Rule(id=m.rule_id)) for m in matches]
        return rules


