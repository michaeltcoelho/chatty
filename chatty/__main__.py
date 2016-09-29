import os.path

from asyncio import get_event_loop
from jinja2 import FileSystemLoader

from aiohttp import web
from aioredis import create_redis
from aiohttp_jinja2 import setup as setup_jinja2

from chatty.routes import routes
from chatty.settings import BASE_DIR
from chatty.auth.middlewares import token_based_auth_middleware


async def create_app():
    app = web.Application(middlewares=[
        token_based_auth_middleware,
    ])
    app.redis = await create_redis(('localhost', 6379))
    setup_jinja2(app, loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates')))
    for (method, path, handler, name) in routes:
        app.router.add_route(method, path, handler, name=name)
    return app

if __name__ == '__main__':
    loop = get_event_loop()
    app = loop.run_until_complete(create_app())
    web.run_app(app)
