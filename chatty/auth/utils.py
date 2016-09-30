from chatty.settings import TOKEN_KEY

async def is_valid_token(redis, token):
    '''
    This method returns username if provided token is exists,
    else returns false.
    '''
    user = await redis.get(TOKEN_KEY.format(uuid=token))
    if user:
        return user.decode('utf-8')
    return False
