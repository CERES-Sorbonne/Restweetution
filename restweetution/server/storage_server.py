import asyncio
import json
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
from restweetution.data_view.media_view2 import MediaView2
from restweetution.data_view.tweet_view2 import TweetView2
from restweetution.models.linked.storage_collection import StorageCollection
from restweetution.models.storage.queries import TweetRowQuery, CollectedTweetQuery, CollectionQuery, \
    TweetFilter, ViewQuery, ExportQuery
from restweetution.models.view_types import ViewType
from restweetution.server.connection_manager import ConnectionManager
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.extractor import Extractor
from restweetution.tasks.server_task import ServerTask
from restweetution.tasks.tweet_export_task import ViewExportTask, ViewExportFileTask

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


class ExportRequest(BaseModel):
    export_type: str  # type of exporter (elastic, csv, etc..)
    id: str  # id of the exported data for future identification
    fields: List[str]
    query: ViewQuery


class Error(HTTPException):
    def __init__(self, value: str):
        super().__init__(status_code=400, detail=value)


async def launch():
    global exporter_elastic

    exporter_elastic = sys_conf.build_elastic_exporter()
    asyncio.create_task(send_update(2))


launch_task = async_loop.create_task(launch())


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


async def send_update(interval: int):
    while True:
        try:
            task_update = get_tasks()
            update = {'source': 'export_tasks', 'data': task_update}
            await manager.broadcast(json.dumps(update, default=str))
        except Exception as e:
            logger.warning(e.__str__())
        await asyncio.sleep(interval)


def register_exception(app_: FastAPI):
    @app_.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        # or logger.error(f'{exc}')
        logger.error(request, exc_str)
        content = {'status_code': 10422, 'message': exc_str, 'data': None}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/count/")
async def get_count(query: ViewQuery):
    if query.view_type == ViewType.TWEET:
        return await get_tweet_count(query.collection)
    if query.view_type == ViewType.MEDIA:
        return await get_media_count(query.collection)

    raise 'no count found for this view'


@app.post("/view/")
async def get_view(query: ViewQuery):
    print(query)
    if query.view_type == ViewType.MEDIA:
        return await get_view_media(query.collection)
    if query.view_type == ViewType.TWEET:
        return await get_view_tweet(query.collection)
    raise ValueError(f'{query.view_type} is not valid')


@app.post("/view/media")
async def get_view_media(query: CollectionQuery, tweet_filter: TweetFilter = None):
    old = time()

    tweet_filter = tweet_filter if tweet_filter else TweetFilter(media=1)
    tweet_filter.media = tweet_filter.media if tweet_filter.media > 0 else 1
    query.limit = query.limit if query.limit and 0 < query.limit < 100 else 100

    coll = StorageCollection(storage)
    medias = await coll.load_media_from_query(query)

    view = MediaView2.compute(medias)

    logger.info(f'media_view took {round(time() - old, 2)} seconds')

    return view.dict()


@app.post("/view/tweet")
async def get_view_tweet(query: CollectionQuery, tweet_filter: TweetFilter = None):
    old = time()

    tweet_filter = tweet_filter if tweet_filter else TweetFilter()
    query.limit = query.limit if query.limit and 0 < query.limit < 100 else 100

    data = await storage.query_tweets_sample(query=query)
    coll = StorageCollection(storage, data)
    # await coll.load_tweet_from_query(query)
    tweet_ids = [t.id for t in coll.data.get_tweets()]
    await coll.load_all_from_tweets()

    view = TweetView2.compute(coll.data.get_linked_tweets(tweet_ids))

    logger.info(f'tweet_view took {round(time() - old, 2)} seconds')

    return view.dict()


@app.post("/tweet_count")
async def get_tweet_count(query: CollectionQuery):
    logger.info(f'Start get_tweets_count {query}')
    count = await storage.query_count_tweets(query)
    print(count)
    return count


@app.post("/media_count")
async def get_media_count(query: CollectionQuery):
    logger.info(f'Start get_media_count {query}')
    count = await storage.query_count_medias(query)
    return count


#
# @app.post("/tweet_discover")
# async def get_tweet_discover(query: TweetRowQuery):
#     query.offset = None
#
#     count, tweets = await asyncio.gather(get_tweet_count(TweetCountQuery(**query.dict())), get_tweets(query))
#     return {"count": count, "tweets": tweets}


@app.post("/export/")
async def export_tweets(request: ExportRequest):
    print('export: ', request)

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
        export_query = ExportQuery(key=key, query=request.query, fields=request.fields)
        task = ViewExportFileTask(storage=storage, query=export_query, exporter=exporter)
        task.name = 'CSV Export'
        on_finish = convert_path

    if request.export_type == 'elastic':
        exporter = exporter_elastic
        export_query = ExportQuery(key=key, query=request.query, fields=request.fields)
        task = ViewExportTask(storage=storage, query=export_query, exporter=exporter)
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
