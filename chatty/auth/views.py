from aiohttp import web
from aiohttp_jinja2 import template

from chatty.auth.decorators import login_required, anonymous_required
from chatty.auth.utils import is_user_exists, create_user, authorize, create_token
from chatty.auth.forms import RegisterForm, LoginForm


@anonymous_required
@template('register.html')
class RegisterView(web.View):

    async def get(self):
        form = RegisterForm()
        return {
            'form': form,
        }

    async def post(self):
        form = RegisterForm(await self.request.post())
        if form.validate():
            if not (await is_user_exists(self.request.app.redis, form.username.data)):
                token = await create_user(self.request.app.redis, form.username.data, form.password.data)
                return {
                    'token': token,
                }
            else:
                form.username.errors.append('User already exists')
        return {
            'form': form,
        }

@anonymous_required
@template('login.html')
class LoginView(web.View):

    async def get(self):
        form = LoginForm()
        return {
            'form': form,
        }

    async def post(self):
        form = LoginForm(await self.request.post())
        if form.validate():
            if (await authorize(self.request.app.redis, form.username.data, form.password.data)):
                token = await create_token(self.request.app.redis, form.username.data)
                return {
                    'token': token,
                }
            else:
                form.username.errors.append('Invalid username or password')
        return {
            'form': form,
        }


class LogoutView(web.View):

    def post(self):
        pass
