from chatty.views import IndexView, ChatroomView
from chatty.auth.views import RegisterView, LoginView, LogoutView

routes = [
    ('GET', '/', IndexView, 'index'),
    ('GET', '/chat/', ChatroomView, 'chatroom'),
    ('*', '/register/', RegisterView, 'register'),
    ('*', '/login/', LoginView, 'Login'),
    ('POST', '/logout/', LogoutView, 'Logout'),
]
