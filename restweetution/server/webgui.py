import asyncio
import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.status import HTTP_302_FOUND

import restweetution.config_loader as config
from restweetution.models.rule import StreamerRule
from restweetution.restweetution import Restweetution

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file('../../private_config/config.yaml')
restweet: Optional[Restweetution] = None


async def launch():
    global restweet
    restweet = Restweetution(main_conf)
    await restweet.init_streamer()

    print(main_conf.persistent_path)
    await main_conf.write_config()


loop = asyncio.get_event_loop()
loop.create_task(launch())

app = FastAPI()


@app.get("/")
async def path_root():
    return FileResponse('static/home.html')


@app.get("/streamer")
async def streamer():
    return {
        "running": restweet.is_streamer_running(),
        "active_rules": restweet.get_active_streamer_rules(),
    }


# @app.get("/streamer/history")
# async def streamer():
#     return {
#         "rule_history": restweet.get_all_rules()
#     }

@app.get('/streamer/debug')
async def streamer_debug():
    return {
        "api_rules": await restweet.get_streamer_api_rules()
    }


@app.get("/downloader")
async def downloader():
    return {
        "running": restweet.is_media_downloader_active(),
        "downloading": restweet.get_actual_media_download(),
        "queue_size": restweet.get_media_downloader_queue_size(),
        "root_dir": restweet.get_media_root_dir()
    }


@app.get("/rules")
async def rules():
    return {
        "rules": await restweet.get_all_rule_info()
    }


@app.get("/rules/streamer")
async def rules():
    return {
        "rules": await restweet.get_all_rule_info(type_='streamer')
    }


@app.get("/rules/searcher")
async def rules():
    return {
        "rules": await restweet.get_all_rule_info(type_='searcher')
    }


@app.post("/downloader/start_stop")
async def downloader_start_stop():
    restweet.set_media_downloader_active(not restweet.is_media_downloader_active())
    return RedirectResponse('/', status_code=HTTP_302_FOUND)


@app.post("/streamer/add_rule")
async def streamer_add_rule(request: Request):
    data = await request.form()
    name = data['name']
    tag = data['tag']
    query = data['query']

    if not name or not query:
        return RedirectResponse('/', status_code=HTTP_302_FOUND)

    rule = StreamerRule(name=name, tag=tag, query=query)
    await restweet.add_streamer_rules([rule])
    return RedirectResponse('/', status_code=HTTP_302_FOUND)


@app.post("/streamer/del_rule")
async def streamer_del_rule(request: Request):
    data = await request.form()
    id_ = int(data['id'])

    if id_:
        await restweet.remove_streamer_rules([id_])

    return RedirectResponse('/', status_code=HTTP_302_FOUND)


@app.post("/streamer/start_stop")
async def streamer_del_rule():
    if restweet.is_streamer_running():
        restweet.stop_streamer()
    else:
        restweet.start_streamer()

    return RedirectResponse('/', status_code=HTTP_302_FOUND)


app.mount("/static", StaticFiles(directory="static"), name="static")

# try:
#     loop.run_forever()
# except KeyboardInterrupt as e:
#     pass
