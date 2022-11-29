import asyncio
import logging
from typing import Optional, List

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.status import HTTP_302_FOUND

import restweetution.config_loader as config
from restweetution.instances.system_instance import SystemInstance
from restweetution.models.config.user_config import RuleConfig, UserConfig
from restweetution.models.rule import StreamerRule
from restweetution.restweetution import Restweetution

logging.basicConfig()
logging.root.setLevel(logging.INFO)

sys_conf = config.load_system_config('../../private_config/system_config.yaml')
restweet: Optional[SystemInstance] = None


async def launch():
    global restweet
    restweet = SystemInstance(sys_conf)
    await restweet.load_user_configs()


loop = asyncio.get_event_loop()
loop.create_task(launch())

app = FastAPI()


@app.get("/")
async def path_root():
    return FileResponse('static/home.html')


# @app.get("/streamer/history")
# async def streamer():
#     return {
#         "rule_history": restweet.get_all_rules()
#     }

@app.get('/users/info')
async def all_users():
    return {u.get_name(): u.user_config for u in restweet.get_user_list()}


@app.post('/users/add')
async def add_user(user_config: UserConfig):
    await restweet.add_user_instance(user_config)
    await restweet.save_user_config(user_config.name)
    return await all_users()


# @app.get("/downloader")
# async def downloader():
#     return {
#         "running": restweet.is_media_downloader_active(),
#         "downloading": restweet.get_actual_media_download(),
#         "queue_size": restweet.get_media_downloader_queue_size(),
#         "root_dir": restweet.get_media_root_dir()
#     }
#

@app.get("/rules")
async def get_rules():
    return {
        "rules": await restweet.get_all_rule_info()
    }


@app.get("/rules/streamer")
async def get_streamer_rules():
    return {
        "rules": await restweet.get_all_rule_info(type_='streamer')
    }


@app.get("/rules/searcher")
async def get_searcher_rules():
    return {
        "rules": await restweet.get_all_rule_info(type_='searcher')
    }


# @app.post("/downloader/start_stop")
# async def downloader_start_stop():
#     restweet.set_media_downloader_active(not restweet.is_media_downloader_active())
#     return RedirectResponse('/', status_code=HTTP_302_FOUND)
#
#

@app.get("/streamer/info/{user_id}")
async def streamer_info(user_id):
    user = restweet.user_instances[user_id]
    return {
        "running": user.streamer_is_running(),
        "active_rules": user.streamer_get_rules(),
    }


@app.get('/streamer/debug/{user_id}')
async def streamer_debug(user_id):
    user = restweet.user_instances[user_id]
    return {
        "api_rules": await user.streamer_get_api_rules()
    }


@app.post("/streamer/add/rules/{user_id}")
async def streamer_add_rule(rules: List[RuleConfig], user_id):
    user = restweet.user_instances[user_id]
    streamer_rules = await user.streamer_add_rules(rules)
    await restweet.save_user_config(user_id)
    return streamer_rules


@app.post("/streamer/del/rules/{user_id}")
async def streamer_del_rule(ids: List[int], user_id):
    user = restweet.user_instances[user_id]
    streamer_rules = await user.streamer_del_rules(ids)
    await restweet.save_user_config(user_id)
    return streamer_rules


@app.post("/streamer/start/{user_id}")
async def streamer_start(user_id):
    user = restweet.user_instances[user_id]
    if user.streamer_is_running():
        raise Exception('Streamer is already Running')
    user.streamer_start()
    await restweet.save_user_config(user_id)
    return await streamer_info(user_id)


@app.post("/streamer/stop/{user_id}")
async def streamer_stop(user_id):
    user = restweet.user_instances[user_id]
    user.streamer_stop()
    await restweet.save_user_config(user_id)
    return await streamer_info(user_id)


@app.get("/searcher/info/{user_id}")
async def searcher_info(user_id):
    user = restweet.user_instances[user_id]
    return {
        "running": user.searcher_is_running(),
        "rule": user.searcher_get_rule(),
    }


@app.post("/searcher/set/rule/{user_id}")
async def searcher_set_rule(rules: RuleConfig, user_id):
    user = restweet.user_instances[user_id]
    await user.searcher_set_rule(rules)
    await restweet.save_user_config(user_id)
    return user.searcher_get_rule()


@app.post("/searcher/del/rule/{user_id}")
async def searcher_del_rule(user_id):
    user = restweet.user_instances[user_id]
    user.searcher_del_rule()
    await restweet.save_user_config(user_id)
    return user.searcher_get_rule()


@app.post("/searcher/start/{user_id}")
async def searcher_start(user_id):
    user = restweet.user_instances[user_id]
    if user.searcher_is_running():
        raise Exception('Searcher is already Running')
    user.searcher_start()
    await restweet.save_user_config(user_id)
    return await searcher_info(user_id)


@app.post("/searcher/stop/{user_id}")
async def searcher_stop(user_id):
    user = restweet.user_instances[user_id]
    user.searcher_stop()
    await restweet.save_user_config(user_id)
    return await searcher_info(user_id)


app.mount("/static", StaticFiles(directory="static"), name="static")

# try:
#     loop.run_forever()
# except KeyboardInterrupt as e:
#     pass
