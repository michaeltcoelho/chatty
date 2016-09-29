from aiohttp import web


async def token_based_auth_middleware(app, handler):
    async def middleware(request):
        pass
    return middleware
