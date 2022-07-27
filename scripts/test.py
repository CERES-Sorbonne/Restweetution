import asyncio

from restweetution.twitter_client import TwitterClient


async def aprint(x):
    print((x))

async def launch():
    client = TwitterClient(token='AAAAAAAAAAAAAAAAAAAAAKYtawEAAAAALVyaGmcVIhSoWYp5vVY0ptgXg7E%3DJsZNkfHKm8kAZzy02bsJOJfjkXbfG8HWd2u4lLRaZLkT4qE2gk')
    await client.connect_tweet_stream(params=None, line_callback=aprint)


asyncio.run(launch())