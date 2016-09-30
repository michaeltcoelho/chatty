import json
import asyncio

from enum import IntEnum

from aiohttp import web, WSMsgType
from aioredis import create_redis
from aiohttp_jinja2 import template

from chatty.settings import (
    REDIS_HOST,
    USER_KEY,
    PUBLIC_ROOM_KEY,
    USER_PRIVATE_KEY,
    USERS_ONLINE_KEY,
)
from chatty.auth.decorators import login_required
from chatty.auth.utils import is_valid_token, is_user_exists


class Message(IntEnum):

    JOIN  = 0
    LEAVE = 1
    PUBLIC = 2
    PRIVATE = 3

    AUTH = 4
    INFO = 5
    ERROR = 6


@template('index.html')
class IndexView(web.View):

    def get(self):
        return {}

class ChatroomView(web.View):

    async def get(self):
        connection = web.WebSocketResponse()
        await connection.prepare(self.request)
        async for message in connection:
            if message.type == WSMsgType.TEXT:
                message = json.loads(message.data)
                message_type = message.get('type', None)
                if not getattr(self.request, 'is_authorized', False):
                    if message_type == Message.AUTH:
                        user = await is_valid_token(self.request.app.redis, message.get('token', None))
                        if user:
                            self.request.is_authorized = True
                            self.request.user = user
                            self.request.redis = await create_redis(REDIS_HOST)
                            self.request.channels = await self.request.redis.subscribe(*[
                                PUBLIC_ROOM_KEY,
                                USER_PRIVATE_KEY.format(name=self.request.user),
                            ])
                            self.request.connection = connection
                            await self.on_join()
                            continue
                    response = json.dumps({
                        'type': Message.ERROR,
                        'message': 'Invalid token',
                    })
                    connection.send_str(response)
                    await connection.close()
                    return connection
                else:
                    if not message_type:
                        response = json.dumps({
                            'type': Message.ERROR,
                            'message': 'Invalid message type',
                        })
                        connection.send_str(response)
                    else:
                        await self.on_message(message_type, message) 
        await self.on_leave()
        for channel in self.request.channels:
            channel.close()
        self.request.redis.close()
        return connection

    async def subscribe(self, channel):
        while (await channel.wait_message()):
            message = await channel.get(encoding='utf-8')
            self.request.connection.send_str(message)

    async def on_message(self, message_type, message):
        message_text = message.get('text', None)
        if not message_text:
            response = json.dumps({
                'type': Message.ERROR,
                'message': 'Invalid request',
            })
            self.request.connection.send_str(response)
        message['from'] = self.request.user
        if message_type == Message.PUBLIC:
            await self.request.app.redis.publish_json(PUBLIC_ROOM_KEY, message);
        elif message_type == Message.PRIVATE:
            username = message.pop('to', None)
            if not username:
                response = json.dumps({
                    'type': Message.ERROR,
                    'message': 'Invalid request',
                })
                self.request.connection.send_str(response)
            user_exists = await is_user_exists(self.request.app.redis, username)
            if user_exists:
                channel = USER_PRIVATE_KEY.format(name=username)
                await self.request.app.redis.publish_json(channel, message)
            else:
                response = json.dumps({
                    'type': Message.ERROR,
                    'message': 'User doesn\'t exist',
                })
                self.request.connection.send_str(response)
        else:
            response = json.dumps({
                'type': Message.ERROR,
                'message': 'Unknown message type',
            })
            self.request.connection.send_str(response)

    async def on_join(self):
        await self.request.app.redis.sadd(USERS_ONLINE_KEY, self.request.user)
        await self.request.app.redis.publish_json(PUBLIC_ROOM_KEY, {
            'type': Message.JOIN,
            'user': self.request.user,
        })
        await self.notify_users()
        tasks = [
            asyncio.Task(self.subscribe(channel)) for channel in self.request.channels
        ]

    async def on_leave(self):
        await self.request.app.redis.srem(USERS_ONLINE_KEY, self.request.user)
        await self.request.app.redis.publish_json(PUBLIC_ROOM_KEY, {
            'type': Message.LEAVE,
            'user': self.request.user,
        })
        await self.notify_users()

    async def notify_users(self):
        users = await self.request.app.redis.smembers(USERS_ONLINE_KEY)
        users = [username.decode('utf-8') for username in users]
        await self.request.app.redis.publish_json(PUBLIC_ROOM_KEY, {
            'type': Message.INFO,
            'users': users,
        })
