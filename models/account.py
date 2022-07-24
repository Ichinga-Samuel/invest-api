from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field
from tortoise import fields
from tortoise.models import Model

from . import to_camel_case, random_id
from utils import now, timedelta, datetime


class PlanEnum(str, Enum):
    Basic = "Basic"
    Gold = "Gold"
    Master = "Master"
    Premium = "Premium"
    VIP = "VIP"


class Plan(BaseModel):
    name: PlanEnum
    minimum: float
    maximum: float
    payout: float
    duration: timedelta
    referral_bonus: float

    def is_valid(self, amount):
        return self.minimum <= amount <= self.maximum

    def get_payment_details(self, deposit: float):
        return {'due': (self.payout + 100) * (deposit / 100), 'referral': (self.referral_bonus / 100) * deposit}

    def get_date(self):
        return {'payment_date': now(), 'due_date': self.duration + now()}

    class Config:
        orm_mode = True


class BaseAccount(BaseModel):
    balance: float = Field(default=0)

    class Config:
        orm_mode = True
        alias_generator = to_camel_case
        allow_population_by_field_name = True


class Account(BaseAccount):
    account_id: int = Field(default_factory=random_id)
    user_id: int


class BaseDeposit(BaseModel):
    plan_id: PlanEnum
    amount: float

    class Config:
        orm_mode = True
        alias_generator = to_camel_case
        allow_population_by_field_name = True


class DepositView(BaseDeposit):
    confirmed: bool = False
    settled: bool = False
    amount_due: float = 0
    payment_date: datetime = Field(default_factory=now)
    due_date: Optional[datetime]


class Deposit(DepositView):
    deposit_id: int = Field(default_factory=random_id)
    account_id: Optional[int]


class DepositCreate(BaseDeposit):
    pass


class ReferralView(BaseModel):
    amount: float = 0
    paid: bool = False

    class Config:
        orm_mode = True
        alias_generator = to_camel_case
        allow_population_by_field_name = True


class Referral(ReferralView):
    ref_id = int
    referrer_id: int
    referred_id: int


class BaseWithdrawal(BaseModel):
    amount: float
    wallet_id: str

    class Config:
        orm_mode = True
        alias_generator = to_camel_case
        allow_population_by_field_name = True


class WithdrawalView(BaseWithdrawal):
    paid: bool = False
    withdrawal_date: datetime = Field(default_factory=now)


class Withdrawal(WithdrawalView):
    account_id: Optional[int]
    withdrawal_id: int = Field(default_factory=random_id)


class WithdrawalCreate(BaseWithdrawal):
    pass


class AccountView(BaseAccount):
    deposits: list[DepositView]
    withdrawals: list[WithdrawalView]


class PlanView(Plan):
    deposits: list[DepositView]


class AccountORM(Model):
    account_id = fields.BigIntField(pk=True)
    user: fields.OneToOneRelation = fields.OneToOneField("models.UserORM", related_name="account", on_delete="CASCADE")
    balance = fields.FloatField()
    deposits: fields.ReverseRelation['DepositORM']
    withdrawals: fields.ReverseRelation['WithdrawalORM']

    def __str__(self):
        return f"{self.account_id}"

    class Meta:
        table = 'Accounts'


class PlanORM(Model):
    name = fields.CharField(pk=True, max_length=256)
    minimum = fields.FloatField()
    maximum = fields.FloatField()
    duration = fields.TimeDeltaField()
    payout = fields.FloatField()
    referral_bonus = fields.FloatField()
    deposits: fields.ReverseRelation['DepositORM']

    def __str__(self):
        return f"{self.name}"

    class Meta:
        table = 'plans'


class DepositORM(Model):
    deposit_id = fields.BigIntField(pk=True)
    amount = fields.FloatField(null=False)
    plan: fields.ForeignKeyNullableRelation = fields.ForeignKeyField("models.PlanORM", related_name='deposits', on_delete=fields.SET_NULL, null=True)
    account: fields.ForeignKeyRelation = fields.ForeignKeyField("models.AccountORM", related_name="deposits", on_delete="CASCADE")
    payment_date = fields.DatetimeField(null=True)
    due_date = fields.DatetimeField(null=True)
    settled = fields.BooleanField(default=False)
    confirmed = fields.BooleanField(default=False)
    amount_due = fields.FloatField(null=True)

    def __str__(self):
        return f"{self.deposit_id}"

    class Meta:
        table = 'Deposits'


class WithdrawalORM(Model):
    withdrawal_id = fields.BigIntField(pk=True)
    amount = fields.FloatField(null=False)
    paid = fields.BooleanField(default=False)
    account: fields.ForeignKeyRelation['AccountORM'] = fields.ForeignKeyField("models.AccountORM", related_name="withdrawals", on_delete="CASCADE")
    withdrawal_date = fields.DatetimeField(null=True)
    wallet_id = fields.CharField(max_length=100)

    def __str__(self):
        return f"{self.withdrawal_id}"

    class Meta:
        table = "Withdrawals"


class ReferralORM(Model):
    ref_id = fields.BigIntField(pk=True)
    paid = fields.BooleanField(null=False)
    amount = fields.FloatField()
    referrer: fields.ForeignKeyRelation['models.UserORM'] = fields.ForeignKeyField('models.UserORM', related_name='referrals', on_delete='CASCADE')
    referred: fields.OneToOneRelation['models.UserORM'] = fields.OneToOneField('models.UserORM', related_name='referral', on_delete='CASCADE')

    class Meta:
        table = "Referrals"
