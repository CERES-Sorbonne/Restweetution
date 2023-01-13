import asyncio
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
from restweetution.models.storage.queries import TweetCountQuery, TweetRowQuery, CollectedTweetQuery
from restweetution.server.connection_manager import ConnectionManager
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.extractor import Extractor
from restweetution.tasks.server_task import ServerTask
from restweetution.tasks.tweet_export_task import TweetExportTask, TweetExportFileTask

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger('StorageServer')

sys_conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))
exporter_elastic: ElasticStorage | None = None

storage = sys_conf.build_storage()
extractor = Extractor(storage)

async_loop = asyncio.get_event_loop()

app = FastAPI()
manager = ConnectionManager()

tasks: List[ServerTask] = []


class ExportTweetRequest(BaseModel):
    export_type: str  # type of exporter (elastic, csv, etc..)
    id: str  # id of the exported data for future identification
    query: TweetRowQuery


class Error(HTTPException):
    def __init__(self, value: str):
        super().__init__(status_code=400, detail=value)


async def launch():
    global exporter_elastic

    exporter_elastic = sys_conf.build_elastic_exporter()


async_loop.create_task(launch())


def convert_path(info: ServerTask):
    info.result['path'] = sys_conf.convert_local_to_public_url(info.result['path'])


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


@app.post("/export/tweets")
async def export_tweets(request: ExportTweetRequest):
    view = RowView()
    key = request.id.split('/')[-1]
    on_finish = None
    task: ServerTask | None = None

    print(request.query)

    if request.export_type == 'csv':
        path = request.id.split('/')
        sub_folder = None
        if len(path) > 2:
            raise ValueError('The requested id for the CSV export can contain only one --> / <--')
        if len(path) == 2:
            sub_folder = path[0]

        exporter = sys_conf.build_csv_exporter(sub_folder=sub_folder)

        if not key.endswith('.csv'):
            key = key + '.csv'

        task = TweetExportFileTask(storage=storage, query=request.query, view=view, exporter=exporter, key=key)
        task.name = 'CSV Export'
        on_finish = convert_path

    if request.export_type == 'elastic':
        exporter = exporter_elastic
        task = TweetExportTask(storage=storage, query=request.query, view=view, exporter=exporter, key=key)
        task.name = 'Elastic Export'

    if task:
        tasks.append(task)
        task.start(on_finish=on_finish)

    return get_tasks()


@app.get("/tasks")
def get_tasks():
    return [t.get_info().dict() for t in tasks]


app.mount("/static", StaticFiles(directory="static"), name="static")
register_exception(app)
