from pathlib import Path

import aiofiles
from aiohttp import web

app = web.Application()
routes = web.RouteTableDef()

base_uri = '/restweetution'

base_dir = Path(__file__).parent

path_to_static_folder = (base_dir / 'resources')


@routes.get('/')
async def hello2(request):
    async with aiofiles.open((path_to_static_folder / 'test.html').resolve(), 'r') as f:
        html = await f.read()
        return web.Response(text=html, content_type='text/html')


@routes.get(base_uri + '/info')
async def get_info(request):
    result = {
        "base": "acid",
        "neutre": "pas",
        "hehe": 1
    }
    return web.json_response(result)


routes.static('/resources', path_to_static_folder.resolve(), show_index=True)
app.add_routes(routes)


async def run_server():
    return await web._run_app(app)
