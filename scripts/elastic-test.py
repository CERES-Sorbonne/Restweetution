import asyncio
from datetime import datetime
from elasticsearch import AsyncElasticsearch

from restweetution.models.tweet import Tweet

# es = Elasticsearch('http://elastic:vjD+mlOWmu6=oESqbxSb@ceres.huma-num.fr:9200')
es = AsyncElasticsearch(
    "https://ceres.huma-num.fr:443/elastic",
    basic_auth=("elastic", "vjD+mlOWmu6=oESqbxSb")
)


async def read():
    resp = await es.search(index="test-index", query={"match_all": {}})
    print("Got %d Hits:" % resp['hits']['total']['value'])
    for hit in resp['hits']['hits']:
        print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])


# doc = {
#     'author': 'kimchy',
#     'text': 'Elasticsearch: cool. bonsai cool.',
#     'timestamp': datetime.now(),
# }
# resp = es.index(index="test-index", id=1, document=doc)
# print(resp['result'])
#
# resp = es.get(index="test-index", id=1)
# print(resp['_source'])
#
# es.indices.refresh(index="test-index")

loop = asyncio.get_event_loop()
loop.run_until_complete(read())


def save_tweet(tweet: Tweet):
    resp = es.index(index="data", id=tweet.id, document=tweet.dict())
    es.indices.refresh(index="data")
    print(resp)
