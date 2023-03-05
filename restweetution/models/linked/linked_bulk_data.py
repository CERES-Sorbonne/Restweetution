from collections import defaultdict
from typing import List, DefaultDict

from restweetution.models.bulk_data import BulkData
from restweetution.models.linked.linked_media import LinkedMedia
from restweetution.models.linked.linked_tweet import LinkedTweet
from restweetution.models.rule import Rule
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.downloaded_media import DownloadedMedia
from restweetution.models.twitter import User, Tweet, Place, Media, Poll


class LinkedBulkData(BulkData):
    media_to_tweets: DefaultDict[str, set]

    def __init__(self):
        super().__init__()
        self.media_to_tweets = defaultdict(set)

    def add_tweets(self, tweets: List[Tweet]):
        super().add_tweets(tweets)
        for tweet in tweets:
            for media_key in tweet.get_media_keys():
                self.media_to_tweets[media_key].add(tweet.id)

    def get_or_create_rule(self, rule: Rule) -> Rule:
        if rule.id in self.rules:
            return self.rules[rule.id]
        else:
            self.rules[rule.id] = rule
            return rule

    def get_or_create_user(self, user: User) -> User:
        if user.id in self.users:
            return self.users[user.id]
        else:
            self.users[user.id] = user
            return user

    def get_or_create_tweet(self, tweet: Tweet) -> Tweet:
        if tweet.id in self.tweets:
            return self.tweets[tweet.id]
        else:
            self.tweets[tweet.id] = tweet
            return tweet

    def get_or_create_place(self, place: Place) -> Place:
        if place.id in self.places:
            return self.places[place.id]
        else:
            self.places[place.id] = place
            return place

    def get_or_create_media(self, media: Media) -> Media:
        if media.media_key in self.medias:
            return self.medias[media.media_key]
        else:
            self.medias[media.media_key] = media
            return media

    def get_or_create_downloaded_media(self, downloaded_media: DownloadedMedia) -> DownloadedMedia:
        if downloaded_media.media_key in self.downloaded_medias:
            return self.downloaded_medias[downloaded_media.media_key]
        else:
            self.downloaded_medias[downloaded_media.media_key] = downloaded_media
            return downloaded_media

    def get_or_create_poll(self, poll: Poll) -> Poll:
        if poll.id in self.polls:
            return self.polls[poll.id]
        else:
            self.polls[poll.id] = poll
            return poll

    def get_or_create_custom_data(self, custom_data: CustomData) -> CustomData:
        if custom_data.id in self.custom_datas:
            return self.custom_datas[custom_data.id]
        else:
            self.custom_datas[custom_data.id] = custom_data
            return custom_data

    # def get_linked_rules(self, rule_id: int):
    #     rule = self.rules.get(rule_id)
    #     if rule:
    #         return LinkedRule(data=self, rule=rule)
    #     else:
    #         return None
    #
    # def get_linked_users(self, user_id: str):
    #     user = self.users.get(user_id)
    #     if user:
    #         return LinkedUser(data=self, user=user)
    #     else:
    #         return None

    def get_linked_tweet(self, tweet_id: str):
        tweet = self.tweets.get(tweet_id)
        if tweet:
            return LinkedTweet(data=self, tweet=tweet)
        else:
            return None

    def get_linked_tweets(self, tweet_ids: List[str] = None):
        if tweet_ids is None:
            tweet_ids = self.tweets.keys()

        tweets = [self.get_linked_tweet(t_id) for t_id in tweet_ids]
        tweets = [t for t in tweets if t]
        return tweets

    #
    # def get_linked_places(self, place_id: str):
    #     place = self.places.get(place_id)
    #     if place:
    #         return LinkedPlace(data=self, place=place)
    #     else:
    #         return None
    #
    def get_linked_media(self, media_id: str):
        media = self.medias.get(media_id)
        if media:
            return LinkedMedia(data=self, media=media)
        else:
            return None

    def get_linked_medias(self, media_keys: List[str] = None):
        if media_keys is None:
            media_keys = self.medias.keys()

        medias = [self.get_linked_media(m) for m in media_keys]
        medias = [m for m in medias if m]
        return medias
    #
    # def get_linked_polls(self, poll_id: str):
    #     poll = self.polls.get(poll_id)
    #     if poll:
    #         return LinkedPoll(data=self, poll=poll)
    #     else:
    #         return None
