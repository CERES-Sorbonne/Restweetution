import asyncio
import datetime
import json
import logging
import math
import os
import time
import traceback
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketDisconnect

from restweetution import config_loader
from restweetution.collectors.searcher import TimeWindow
from restweetution.instances.system_instance import SystemInstance
from restweetution.models.config.user_config import RuleConfig, UserConfig, CollectTasks
from restweetution.models.instance_update import InstanceUpdate
from restweetution.models.rule import Rule
from restweetution.models.searcher import CountUnit
from restweetution.server.connection_manager import ConnectionManager
from restweetution.utils import chunks

logging.basicConfig()
logging.root.setLevel(logging.INFO)

sys_conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))

restweet: Optional[SystemInstance] = None
loop = asyncio.get_event_loop()

app = FastAPI()
manager = ConnectionManager()

last_streamer_update = time.time()


class CountRequest(BaseModel):
    query: str
    start: datetime.datetime = None
    end: datetime.datetime = None
    recent: bool = True


class Error(HTTPException):
    def __init__(self, value: str):
        super().__init__(status_code=400, detail=value)


async def sendUpdates(update: InstanceUpdate):
    global last_streamer_update
    if update.source == 'searcher':
        update.data = await searcher_info(update.user_id)
        await manager.broadcast(json.dumps(update.dict(), default=str))
    if update.source == 'streamer':
        now = time.time()
        if int(now - last_streamer_update) < 3:
            return
        last_streamer_update = now
        update.data = await streamer_info(update.user_id)
        await manager.broadcast(json.dumps(update.dict(), default=str))


async def launch():
    global restweet
    restweet = SystemInstance(sys_conf)
    await restweet.load_user_configs()
    restweet.event.add(sendUpdates)


loop.create_task(launch())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
async def path_root():
    return FileResponse('static/home.html')


@app.get('/users/info')
async def all_users():
    try:
        return {u.get_name(): u.user_config for u in restweet.get_user_list()}
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post('/users/add')
async def add_user(user_config: UserConfig):
    try:
        await restweet.add_user_instance(user_config)
        await restweet.save_user_config(user_config.name)
        return await all_users()
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post('/users/del')
async def del_users(names: List[str]):
    try:
        await restweet.remove_user_instances(names)
        return await all_users()
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


# @app.get("/downloader")
# async def downloader():
#     return {
#         "running": restweet.is_media_downloader_active(),
#         "downloading": restweet.get_actual_media_download(),
#         "queue_size": restweet.get_media_downloader_queue_size(),
#         "root_dir": restweet.get_media_root_dir()
#     }
#

@app.get("/rules/info")
async def get_rules():
    try:
        return await restweet.get_all_rule_info()
    except Exception as e:
        raise HTTPException(400, e.__str__())


@app.post("/rules/add")
async def add_rules(rules: List[RuleConfig]):
    try:
        rules = [Rule(**r.dict()) for r in rules]
        await restweet.storage_instance.storage.request_rules(rules)
        return await get_rules()
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/rules/test/{user_id}")
async def test_rule(user_id, rule: RuleConfig):
    try:
        user = restweet.user_instances[user_id]
        res = await user.test_rule(rule)
        return res
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.get("/streamer/info/{user_id}")
async def streamer_info(user_id):
    try:
        user = restweet.user_instances[user_id]
        return {
            "running": user.streamer_is_running(),
            "active_rules": user.streamer_get_rules(),
            "count": user.streamer_get_count(),
            "collect_tasks": user.streamer_get_collect_tasks(),
            "conflict": user.streamer_has_conflict()
        }
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.get('/streamer/debug/{user_id}')
async def streamer_debug(user_id):
    try:
        user = restweet.user_instances[user_id]
        return {
            "api_rules": await user.streamer_get_api_rules()
        }
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/streamer/add/rules/{user_id}")
async def streamer_add_rule(rules: List[RuleConfig], user_id):
    try:
        user = restweet.user_instances[user_id]
        await user.streamer_add_rules(rules)
        await user.save_user_config()
        return await streamer_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/streamer/del/rules/{user_id}")
async def streamer_del_rule(ids: List[int], user_id):
    try:
        user = restweet.user_instances[user_id]
        await user.streamer_del_rules(ids)
        await user.save_user_config()
        return await streamer_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/streamer/set/rules/{user_id}")
async def streamer_set_rule(rules: List[RuleConfig], user_id):
    try:
        user = restweet.user_instances[user_id]
        await user.streamer_set_rules(rules)
        await user.save_user_config()
        return await streamer_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/streamer/sync/{user_id}")
async def streamer_sync(user_id: str):
    try:
        user = restweet.user_instances[user_id]
        await user.streamer_sync()
        return await streamer_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/streamer/verify/{user_id}")
async def streamer_verify(user_id: str):
    try:
        user = restweet.user_instances[user_id]
        is_sync, api_rules = await user.streamer_verify()
        info = await streamer_info(user_id)
        info['api_rules'] = api_rules
        return info
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/streamer/set/collect_tasks/{user_id}")
async def streamer_set_collect_task(tasks: CollectTasks, user_id):
    try:
        user = restweet.user_instances[user_id]
        user.streamer_set_collect_tasks(tasks)
        await user.save_user_config()
        return await streamer_info(user_id)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(400, e.__str__())


@app.post("/streamer/start/{user_id}")
async def streamer_start(user_id):
    try:
        user = restweet.user_instances[user_id]
        if user.streamer_is_running():
            raise Exception('Streamer is already Running')
        user.streamer_start()
        await user.save_user_config()
        return await streamer_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/streamer/stop/{user_id}")
async def streamer_stop(user_id):
    try:
        user = restweet.user_instances[user_id]
        user.streamer_stop()
        await user.save_user_config()
        return await streamer_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.get("/searcher/info/{user_id}")
async def searcher_info(user_id):
    try:
        user = restweet.user_instances[user_id]
        res = {
            "running": user.searcher_is_running(),
            "sleeping": user.searcher_is_sleeping(),
            "fields": user.searcher_get_fields(),
            "rule": user.searcher_get_rule(),
            "time_window": user.searcher_get_time_window(),
            "collect_tasks": user.searcher_get_collect_tasks()
        }
        return res
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/searcher/set/rule/{user_id}")
async def searcher_set_rule(rules: RuleConfig, user_id):
    try:
        user = restweet.user_instances[user_id]
        await user.searcher_set_rule(rules)
        await user.save_user_config()
        return await searcher_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/searcher/del/rule/{user_id}")
async def searcher_del_rule(user_id):
    try:
        user = restweet.user_instances[user_id]
        user.searcher_del_rule()
        await user.save_user_config()
        return await searcher_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/searcher/set/collect_tasks/{user_id}")
async def searcher_set_collect_tasks(tasks: CollectTasks, user_id):
    try:
        user = restweet.user_instances[user_id]
        user.searcher_set_collect_tasks(tasks)
        await user.save_user_config()
        return await searcher_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/searcher/start/{user_id}")
async def searcher_start(user_id):
    try:
        user = restweet.user_instances[user_id]
        if user.searcher_is_running():
            raise Exception('Searcher is already Running')
        await user.searcher_start()
        await user.save_user_config()
        return await searcher_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/searcher/stop/{user_id}")
async def searcher_stop(user_id):
    try:
        user = restweet.user_instances[user_id]
        user.searcher_stop()
        await user.save_user_config()
        return await searcher_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/searcher/set/time/{user_id}")
async def searcher_set_time(user_id, time_window: TimeWindow):
    try:
        user = restweet.user_instances[user_id]
        user.searcher_set_time_window(time_window)
        await user.save_user_config()
        return await searcher_info(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


@app.post("/searcher/count/{user_id}")
async def searcher_count(user_id, req: CountRequest, max_points=60):
    try:
        user = restweet.user_instances[user_id]
        total, arr = await user.searcher_count(query=req.query, start=req.start, recent=req.recent)

        if len(arr) > max_points:
            res = []
            div = math.floor(len(arr) / max_points)
            for counts in chunks(arr, div):
                counts: List[CountUnit]
                new_count = CountUnit(start=counts[0].start, end=counts[-1].end,
                                      tweet_count=sum((c.tweet_count for c in counts)))
                res.append(new_count)
            arr = res

        points = [{"date": c.start, "count": c.tweet_count} for c in arr]
        return {
            "total": total,
            "points": points,
            "query": req.query
        }

    except Exception as e:
        print(e)
        raise HTTPException(400, e.__str__())


app.mount("/static", StaticFiles(directory="static"), name="static")
