from fastapi import Request
from fastapi_admin.enums import Method
from fastapi_admin.app import app
from fastapi_admin.resources import Action, Dropdown, Link, Field, Model, ToolbarAction, ComputeField
from fastapi_admin.widgets import filters, inputs, displays

from models.admin import Admin
from models.account import AccountORM, DepositORM, WithdrawalORM, PlanORM, ReferralORM
from models.user import UserORM


@app.register
class Dashboard(Link):
    label = "Dashboard"
    icon = "fas fa-home"
    url = "/admin"


class UserName(ComputeField):
    async def get_value(self, request: Request, obj: dict):
        if model := self.input.model:
            return await model.get(pk=obj.get(self.name))
        return obj.get(self.name)


class AccountName(ComputeField):
    async def get_value(self, request: Request, obj: dict):
        val = await AccountORM.get(pk=obj.get(self.name)).prefetch_related('user')
        return val.user.email


@app.register
class AdminResource(Model):
    label = "Admin"
    model = Admin
    icon = "fas fa-user"
    page_pre_title = "admin list"
    page_title = "admin model"
    fields = [
        "id",
        "username",
        "created_at",
        "wallet_id",
        Field(
            name="password",
            label="Password",
            display=displays.InputOnly(),
            input_=inputs.Password(),
        )
    ]

    # async def get_toolbar_actions(self, request: Request) -> list[ToolbarAction]:
    #     return []

    async def cell_attributes(self, request: Request, obj: dict, field: Field) -> dict:
        if field.name == "id":
            return {"class": "bg-danger text-white"}
        return await super().cell_attributes(request, obj, field)

    # async def get_bulk_actions(self, request: Request) -> list[Action]:
    #     return []


@app.register
class UserResource(Model):
    label = "Users"
    model = UserORM
    icon = "fas fa-user"
    page_pre_title = "Users"
    page_title = "User"
    filters = [
        filters.Search(
            name="email",
            label="Email",
            search_mode="equal",
            placeholder="Search for email"
        ),
        filters.Date(name="created", label="Joined")
    ]
    fields = [
        "name",
        "email",
        "gender",
        "referral_id",
        Field(name="created", label="Joined"),
        Field(name="verified", label="Verified", input_=inputs.Radio(options=[('True', True), ('False', False)]))
    ]


@app.register
class AccountResource(Model):
    label = "Account"
    model = AccountORM
    icon = "fas fa-user"
    page_pre_title = "Accounts"
    page_title = "Account"
    fields = [
        "balance",
        "account_id",
        UserName(name='user_id', label="User", input_=inputs.ForeignKey(model=UserORM))
    ]
    filters = [
        filters.Search(
            name="balance",
            label="Account Balance",
            search_mode="range",
            placeholder="search by balance"
        )
    ]


@app.register
class DepositResource(Model):
    label = "Deposit"
    icon = "fas fa-money"
    model = DepositORM
    page_pre_title = "Deposits"
    page_title = "Deposits"
    fields = [
        "amount",
        "settled",
        "confirmed",
        "amount_due",
        "due_date",
        "payment_date",
        Field(name="plan_id", label="Plan", input_=inputs.ForeignKey(model=PlanORM)),
        AccountName(name="account_id", label="Account", input_=inputs.DisplayOnly())
    ]
    filters = [
        "confirmed",
        "settled",
    ]

    async def cell_attributes(self, request: Request, obj: dict, field: Field) -> dict:
        if field.name == "confirmed":
            return {"class": "bg-info text-white"}
        return await super().cell_attributes(request, obj, field)

    async def get_actions(self, request: Request) -> list[Action]:
        actions = await super().get_actions(request=request)
        confirm = Action(label="confirm", icon="ti ti-edit", name="confirm", method=Method.POST)
        settle = Action(label="settle", icon="ti ti-edit", name="settle_deposit", method=Method.POST)
        actions.extend((settle, confirm))
        return actions


@app.register
class WithdrawalResource(Model):
    label = "Withdrawal"
    model = WithdrawalORM
    page_title = "Withdrawals"
    fields = [
        "amount",
        "paid",
        "wallet_id",
        "withdrawal_date",
        AccountName(name="account_id", label="Account", input_=inputs.DisplayOnly())
    ]

    async def get_actions(self, request: Request) -> list[Action]:
        actions = await super().get_actions(request=request)
        confirm = Action(label="settle", icon="ti ti-edit", name="settle", method=Method.POST)
        actions.append(confirm)
        return actions
