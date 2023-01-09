import asyncio
import datetime
import logging
import os
from time import time
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from restweetution import config_loader
from restweetution.data_view.row_view import RowView
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


class TweetCountQuery(BaseModel):
    date_from: datetime.datetime = None
    date_to: datetime.datetime = None
    rule_ids: List[int] = None


class TweetQuery(TweetCountQuery):
    ids: List[str] = None
    offset: int = None
    limit: int = None
    desc: bool = False
    fields: List[str] = None


def register_exception(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        # or logger.error(f'{exc}')
        logger.error(request, exc_str)
        content = {'status_code': 10422, 'message': exc_str, 'data': None}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/tweets")
async def get_tweets(query: TweetQuery):
    if not query.limit or query.limit > 100 or query.limit < 1:
        query.limit = 100

    row_fields = query.fields
    if query.fields:
        query.fields = RowView.get_required_fields(query.fields)

    logger.info(f'Start get_tweets: {query}')
    tweets = await storage.get_collected_tweets(**query.dict())
    if tweets:
        bulk_data = await extractor.expand_collected_tweets(tweets)
        res = RowView.compute(bulk_data, only_ids=[t.id for t in tweets], fields=row_fields)
        return res
    return []


@app.post("/tweet_count")
async def get_tweet_count(query: TweetCountQuery):
    logger.info(f'Start get_tweets_count {query}')
    count = await storage.get_tweets_count(**query.dict())
    return count


@app.post("/tweet_discover")
async def get_tweet_discover(query: TweetQuery):
    count = await get_tweet_count(TweetCountQuery(**query.dict()))

    query.offset = None
    tweets = await get_tweets(query)
    return {"count": count, "tweets": tweets}


app.mount("/static", StaticFiles(directory="static"), name="static")
register_exception(app)
