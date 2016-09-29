from aiohttp import web

from chatty.settings import TOKEN_KEY


async def token_based_auth_middleware(app, handler):
    '''
    This middleware will check user access token if handler requires auth.
    '''
    async def middleware(request):
        login_required = getattr(handler, 'login_required', False)
        if login_required:
            token = request.headers.get('Authorization', None)
            if token:
                is_valid_token = await app.redis.get(TOKEN_KEY.format(uuid=token))
                if is_valid_token:
                    return await handler(request)
            return web.HTTPUnauthorized()
        else:
            return await handler(request)
    return middleware
