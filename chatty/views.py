from enum import Enum

from aiohttp import web

from chatty.auth.decorators import login_required


class Message(Enum):

    JOIN  = 0
    LEAVE = 1
    PUBLIC = 2
    PRIVATE = 3


class IndexView(web.View):

    def get(self):
        pass

class ChatroomView(web.View):

    def get(self):
        pass

    def send(self, room=None):
        pass
