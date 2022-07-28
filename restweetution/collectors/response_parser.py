from restweetution.models.bulk_data import BulkData
from restweetution.models.twitter import TweetIncludes


def parse_includes(bulk_data: BulkData, includes: TweetIncludes):
    if includes:
        if includes.users:
            bulk_data.add_users(includes.users)
        if includes.places:
            bulk_data.add_places(includes.places)
        if includes.media:
            bulk_data.add_medias(includes.media)
        if includes.polls:
            bulk_data.add_polls(includes.polls)
        if includes.tweets:
            bulk_data.add_tweets(includes.tweets)