from restweetution.data_view.media_view2 import MediaView2
from restweetution.data_view.tweet_view2 import TweetView2
from restweetution.models.view_types import ViewType


def get_view(view_type: ViewType):
    if view_type == ViewType.TWEET:
        view = TweetView2()
    elif view_type == ViewType.MEDIA:
        view = MediaView2()
    else:
        raise ValueError(f'{view_type} is not valid')

    return view

