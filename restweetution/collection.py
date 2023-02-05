from typing import Dict, List

from restweetution.models.extended_types import ExtendedTweet, ExtendedMedia
from restweetution.models.rule import Rule
from restweetution.models.twitter import Tweet, Media


class Collection:
    rules: Dict[int, Rule] = {}
    tweets: Dict[str, ExtendedTweet] = {}
    medias: Dict[str, ExtendedMedia] = {}

    def add_tweets(self, tweets: List[ExtendedTweet]):
        for t in tweets:
            self.tweets[t.id] = t

    def add_medias(self, medias: List[ExtendedMedia]):
        for m in medias:
            self.medias[m.media_key] = m

    def add_rules(self, rules: List[Rule]):
        for r in rules:
            self.rules[r.id] = r


class Node:
    def __init__(self, tree, generated=False):
        self._tree: CollectionTree = tree
        self.generated = generated


class TweetNone(Node):
    def __init__(self, tree, tweet: ExtendedTweet, generated=False):
        super().__init__(tree=tree, generated=generated)
        self._xtweet = tweet
        self.data = tweet.tweet
        self.id = tweet.id

    def medias(self):
        keys = self.data.media_keys()
        if not keys:
            return []
        medias = [self._tree.get_media(k) for k in keys]
        medias = [m for m in medias if m]
        return medias

    def rules(self):
        sources = self._xtweet.sources
        rules_ids = [s.rule_id for s in sources]
        rules = [self._tree.get_rule(r) for r in rules_ids]
        rules = [r for r in rules if r]
        return rules


class MediaNode(Node):
    def __init__(self, tree, media: ExtendedMedia, generated=False):
        super().__init__(tree, generated=generated)
        self.xmedia = media
        self.data = media.media
        self.id = media.media_key
        self.downloaded = media.downloaded

    def tweets(self):
        tweet_ids = self.xmedia.tweet_ids
        if not tweet_ids:
            return []
        tweets = [self._tree.get_tweet(t) for t in tweet_ids]
        tweets = [t for t in tweets if t]
        return tweets

    def rules(self):
        tweets = self.tweets()
        rules = []
        for t in tweets:
            rules.extend(t.rules())
        return rules


class RuleNode(Node):
    def __init__(self, tree, rule: Rule, generated=False):
        super().__init__(tree, generated=generated)
        self.data = rule
        self.id = rule.id


class CollectionTree:
    def __init__(self, collection: Collection):
        self._data = collection

    def get_tweet(self, tweet_id: str):
        if tweet_id not in self._data.tweets:
            return TweetNone(self._data, ExtendedTweet(Tweet(id=tweet_id)), generated=True)
        return TweetNone(self, self._data.tweets[tweet_id])

    def get_tweets(self, tweet_ids: List[str] = None):
        if not tweet_ids:
            return [self.get_tweet(t.id) for t in list(self._data.tweets.values())]
        res = [self.get_tweet(t) for t in tweet_ids]
        res = [r for r in res if r]
        return res

    def get_media(self, media_key: str):
        if media_key not in self._data.medias:
            return MediaNode(self._data, ExtendedMedia(Media(media_key=media_key)), generated=True)
        return MediaNode(self, self._data.medias[media_key])

    def get_rule(self, rule_id: int):
        if rule_id not in self._data.rules:
            return None
        return RuleNode(self, self._data.rules[rule_id])


