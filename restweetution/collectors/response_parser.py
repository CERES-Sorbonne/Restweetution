from restweetution.models.twitter import Includes


def parse_includes(includes: Includes):
    res = {}
    if includes:
        if includes.users:
            res['users'] = includes.users
        if includes.places:
            res['places'] = includes.places
        if includes.media:
            res['medias'] = includes.media
        if includes.polls:
            res['polls'] = includes.polls
        if includes.tweets:
            res['tweets'] = includes.tweets
    return res


