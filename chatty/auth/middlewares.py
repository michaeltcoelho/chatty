from aiohttp import web

from chatty.settings import TOKEN_KEY


async def token_based_auth_middleware(app, handler):
    '''
    This middleware will check user access token if handler requires auth.
    '''
    async def middleware(request):
        token = request.headers.get('Authorization', None)
        login_required = getattr(handler, 'login_required', False)
        if login_required:
            if token:
                is_valid_token = await app.redis.get(TOKEN_KEY.format(uuid=token))
                if is_valid_token:
                    return await handler(request)
            return web.HTTPUnauthorized()
        else:
            anonymous_required = getattr(handler, 'anonymous_required', False)
            if anonymous_required and token:
                return web.HTTPFound('/')
            return await handler(request)
    return middleware
