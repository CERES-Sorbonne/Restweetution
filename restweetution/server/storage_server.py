import asyncio
import datetime
import logging
import os
from time import time
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketDisconnect

from restweetution import config_loader
from restweetution.data_view.row_view import RowView
from restweetution.server.connection_manager import ConnectionManager
from restweetution.storages.extractor import Extractor

logging.basicConfig()
logging.root.setLevel(logging.INFO)

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


class TweetQuery(BaseModel):
    ids: List[str] = None
    date_from: datetime.datetime = None
    date_to: datetime.datetime = None
    offset: int = None
    limit: int = None
    rule_ids: List[int] = None
    desc: bool = False


@app.get("/tweets")
async def get_tweets(query: TweetQuery, fields: List[str] = None):
    # if not query.limit or query.limit > 1000 or query.limit < 1:
    #     query.limit = 1000
    storage_fields = None
    if fields:
        storage_fields = RowView.get_required_fields(fields)
    tweets = await storage.get_tweets(**query.dict(), fields=storage_fields)
    bulk_data = await extractor.expand_tweets(tweets)
    res = RowView.compute(bulk_data, only_ids=[t.id for t in tweets], fields=fields)
    return res


app.mount("/static", StaticFiles(directory="static"), name="static")
