from enum import Enum
from typing import Optional

from pydantic import BaseModel, root_validator, Field
from tortoise import fields
from tortoise.models import Model

from utils import now, datetime
from . import to_camel_case, random_id, ref_id
from .account import AccountView, AccountORM, ReferralORM, ReferralView


class Gender(str, Enum):
    male = "Male"
    female = "Female"


class Login(BaseModel):
    password: str
    email: str


class BaseUser(BaseModel):
    name: str
    email: str
    gender: Gender

    class Config:
        orm_mode = True
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        extra = "allow"


class User(BaseUser):
    user_id: int = Field(default_factory=random_id)
    referral_id: str = Field(default_factory=ref_id)
    created: datetime = Field(default_factory=now)
    last_login: datetime = Field(default_factory=now)
    token: Optional[str]
    verified: bool = False


class UserView(User):
    account_details: Optional[AccountView]
    referrals: Optional[list[ReferralView]]


class UserEdit(BaseModel):
    name: Optional[str]
    email: Optional[str]
    gender: Optional[Gender]


class UserCreate(BaseUser):
    password: str
    password_confirm: str
    referrer_id: Optional[str]

    @root_validator()
    def pswd_match(cls, values):
        p = values.get("password")
        pc = values.get('password_confirm')
        if p != pc:
            raise ValueError('Password Mismatch')
        return values


class UserDB(User):
    password_hash: str
    verified: bool


class PasswordChange(BaseModel):
    old_password: str
    password: str
    password_confirm: str

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True

    @root_validator()
    def pswd_match(cls, values):
        p = values.get("password")
        pc = values.get('password_confirm')
        if p != pc:
            raise ValueError('Password Mismatch')
        return values


class PasswordReset(BaseModel):
    password: str
    password_confirm: str
    token: str

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True


class ResetPassword(BaseModel):
    email: str


class UserORM(Model):
    user_id = fields.BigIntField(pk=True)
    account: fields.ReverseRelation['AccountORM']
    name = fields.CharField(max_length=100, null=False)
    gender = fields.CharField(max_length=6, null=False)
    email = fields.CharField(max_length=100, unique=True, null=False)
    created = fields.DatetimeField(auto_now_add=True)
    last_login = fields.DatetimeField(auto_now=True)
    referral_id = fields.CharField(max_length=32, unique=True)
    password_hash = fields.CharField(max_length=255, null=False)
    verified = fields.BooleanField(default=False)
    referral: fields.ReverseRelation['ReferralORM']
    referrals: fields.ReverseRelation['ReferralORM']

    def __str__(self):
        return f"{self.email}"

    class Meta:
        table = 'Users'
        unique_together = (('email', 'name'),)
