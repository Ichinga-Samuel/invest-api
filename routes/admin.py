from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Link

from models.admin import Admin

LoginProvider = UsernamePasswordProvider(
    admin_model=Admin,
    login_logo_url="https://preview.tabler.io/static/logo.svg"
)


@admin_app.register
class Home(Link):
    label = "Home"
    icon = "fas fa-home"
    url = "/admin"

