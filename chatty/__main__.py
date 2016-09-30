from asyncio import get_event_loop
from jinja2 import FileSystemLoader

from aiohttp import web
from aioredis import create_redis
from aiohttp_jinja2 import setup as setup_jinja2

from chatty.routes import routes
from chatty.settings import TEMPLATES_DIR, STATIC_DIR, REDIS_HOST
from chatty.auth.middlewares import token_based_auth_middleware


async def create_app():
    app = web.Application(middlewares=[
        token_based_auth_middleware,
    ])
    app.redis = await create_redis(REDIS_HOST)
    setup_jinja2(app, loader=FileSystemLoader(TEMPLATES_DIR))
    for (method, path, handler, name) in routes:
        app.router.add_route(method, path, handler, name=name)
    app.router.add_static('/static', STATIC_DIR)
    return app

if __name__ == '__main__':
    loop = get_event_loop()
    app = loop.run_until_complete(create_app())
    web.run_app(app)
