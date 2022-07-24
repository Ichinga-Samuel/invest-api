from typing import Optional
from tortoise import Model, fields
from pydantic import BaseModel, Field
from fastapi_admin.models import AbstractAdmin

from utils import now, datetime


class Admin(AbstractAdmin):
    wallet_id = fields.CharField(max_length=64, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}"


class AdminModel(BaseModel):
    username: str
    wallet_id: Optional[str] = Field(alias="walletId")
    created_at: datetime
