from fastapi_admin.models import AbstractAdmin
from tortoise import Model, fields

from utils import datetime, now


class Admin(AbstractAdmin):
    last_login = fields.DatetimeField(default=now)
    email = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}"
