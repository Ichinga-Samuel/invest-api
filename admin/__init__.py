from fastapi_admin.exceptions import (
    forbidden_error_exception,
    not_found_error_exception,
    server_error_exception,
    unauthorized_error_exception,
)
from fastapi_admin.app import app
from fastapi import status

from .providers import LoginProvider
from . import resources, routes
from models.admin import Admin

app.add_exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR, server_error_exception)
app.add_exception_handler(status.HTTP_404_NOT_FOUND, not_found_error_exception)
app.add_exception_handler(status.HTTP_403_FORBIDDEN, forbidden_error_exception)
app.add_exception_handler(status.HTTP_401_UNAUTHORIZED, unauthorized_error_exception)
