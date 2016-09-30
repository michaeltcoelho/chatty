import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

USER_KEY = 'users:{name}'
TOKEN_KEY = 'tokens:{uuid}'
TOKEN_TTL = 60 * 60 * 24

PUBLIC_ROOM_KEY = 'rooms:public'
USER_PRIVATE_KEY = 'users:{name}:private'
USERS_ONLINE_KEY = 'users:online'

REDIS_HOST = ('localhost', 6379)
