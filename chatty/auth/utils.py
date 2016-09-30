from hashlib import pbkdf2_hmac
from binascii import hexlify

from chatty.settings import USER_KEY, TOKEN_KEY, TOKEN_TTL, SECRET_KEY


async def is_valid_token(redis, token):
    '''
    This function returns username if provided token is exists,
    else returns false.
    '''
    user = await redis.get(TOKEN_KEY.format(uuid=token))
    if user:
        return user.decode('utf-8')
    return False

async def is_user_exists(redis, username):
    '''
    Checks that USER_KEY with given username exists.
    '''
    exists = await redis.exists(USER_KEY.format(name=username))
    return exists

def create_hash(password):
    '''
    Creates pbkdf2 hash using provided password and SECRET_KEY defined at settings
    '''
    if not isinstance(password, bytes):
        password = password.encode('utf-8')
    dk = pbkdf2_hmac('sha256', password, SECRET_KEY, 100000)
    return hexlify(dk).decode('utf-8')

async def delete_token(redis, token):
    '''
    Deletes user access token when user logouts
    '''
    token_key = TOKEN_KEY.format(uuid=token)
    await redis.delete(token_key)

async def create_token(redis, username):
    '''
    Returns token that user must use in authorization.
    '''
    token = create_hash(username)
    token_key = TOKEN_KEY.format(uuid=token)
    await redis.set(token_key, username)
    await redis.expire(token_key, TOKEN_TTL)
    return token

async def create_user(redis, username, password):
    '''
    Actually, just stores password hash at formatted USER_KEY.
    '''
    password = create_hash(password)
    await redis.set(USER_KEY.format(name=username), password)
    token = await create_token(redis, username)
    return token

async def authorize(redis, username, password):
    '''
    Checks that provided password of user matches password hash stored at redis.
    '''
    true_password_hash = await redis.get(USER_KEY.format(name=username))
    provided_password_hash = create_hash(password).encode('utf-8')
    return true_password_hash == provided_password_hash
