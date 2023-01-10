import asyncio
import logging
import os
from time import time

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from restweetution import config_loader
from restweetution.data_view.row_view import RowView
from restweetution.models.storage.queries import TweetCountQuery, TweetRowQuery, CollectedTweetQuery
from restweetution.server.connection_manager import ConnectionManager
from restweetution.storages.extractor import Extractor

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger('StorageServer')

sys_conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))

storage = sys_conf.build_storage()
extractor = Extractor(storage)
loop = asyncio.get_event_loop()

app = FastAPI()
manager = ConnectionManager()


class Error(HTTPException):
    def __init__(self, value: str):
        super().__init__(status_code=400, detail=value)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def register_exception(app_: FastAPI):
    @app_.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        # or logger.error(f'{exc}')
        logger.error(request, exc_str)
        content = {'status_code': 10422, 'message': exc_str, 'data': None}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/tweets")
async def get_tweets(query: TweetRowQuery):
    if not query.limit or query.limit > 100 or query.limit < 1:
        query.limit = 100

    old = time()

    t_query = CollectedTweetQuery(**query.dict())
    tweets = await storage.get_collected_tweets(**t_query.dict())
    logger.info(f'get_collected_tweets: {time() - old} seconds')
    if tweets:
        inter = time()
        bulk_data = await extractor.expand_collected_tweets(tweets)
        logger.info(f'expand_collected_tweets: {time() - inter} seconds')
        res = RowView.compute(bulk_data, only_ids=[t.tweet_id for t in tweets], fields=query.row_fields)
        logger.info(f'get_tweets: {time() - old} seconds')
        return res
    return []


@app.post("/tweet_count")
async def get_tweet_count(query: TweetCountQuery):
    logger.info(f'Start get_tweets_count {query}')
    count = await storage.get_tweets_count(**query.dict())
    return count


@app.post("/tweet_discover")
async def get_tweet_discover(query: TweetRowQuery):
    query.offset = None

    count, tweets = await asyncio.gather(get_tweet_count(TweetCountQuery(**query.dict())), get_tweets(query))
    return {"count": count, "tweets": tweets}


app.mount("/static", StaticFiles(directory="static"), name="static")
register_exception(app)
