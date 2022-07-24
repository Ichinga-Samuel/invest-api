from fastapi import Request

from tortoise.transactions import in_transaction
from tortoise.expressions import F
from models.account import (Withdrawal, WithdrawalCreate, Deposit, ReferralORM, WithdrawalORM, DepositORM, AccountORM, Account, PlanORM, Plan,
                            DepositCreate)

from utils.emails import DepositReceivedEmail, WithdrawalEmail, ReferralEmail, DepositConfirmationEmail, AccountAlertEmail
from utils import now, error_handler, ResponseModel


async def create_account(account: Account) -> AccountORM:
    return await AccountORM.create(**account.dict())


async def update_account(*, acc_id: int, **kwargs):
    account = await AccountORM.get(account_id=acc_id)
    await account.update_from_dict(kwargs)
    await account.save(update_fields=list(kwargs.keys()))
    return True


@error_handler(error="Unable to create deposit")
async def create_deposit(req: Request, deposit: DepositCreate) -> ResponseModel:
    async with in_transaction():
        plan = await PlanORM.get(name=deposit.plan_id)
        plan = Plan.from_orm(plan)
        deposit = Deposit(**deposit.dict())
        dep = await DepositORM.create(**deposit.dict(exclude_none=True), account_id=req.state.user.account.account_id)
        email = DepositReceivedEmail(name=req.state.user.name, recipients=[req.state.user.email], plan=plan.name, amount=dep.amount)
        await email.send()
        return ResponseModel(message=f"Deposit of {dep.amount} Successfully Logged")


async def settle_deposits():
    try:
        async with in_transaction():
            deposits = DepositORM.filter(confirmed=True, settled=False, due_date__lte=now()).prefetch_related('account__user')
            async for deposit in deposits:
                await deposit.update_from_dict({"settled": True})
                await deposit.save(update_fields=("settled",))
                deposit.account.balance = F("balance") + deposit.amount_due
                await deposit.account.save(update_fields=("balance",))
                message = f"Your Deposit has matured and your account has been credited with {deposit.amount_due}"
                user = deposit.account.user
                email = AccountAlertEmail(name=user.name, recipients=[user.email], message=message)
                await email.send()
    except Exception as err:
        print(err)


@error_handler(error="Unable to settle deposit")
async def settle_deposit(*, deposit_id: int) -> ResponseModel:
    async with in_transaction():
        deposit = await DepositORM.get(deposit_id=deposit_id).prefetch_related("account__user")
        account = deposit.account
        user = account.user
        dep = await deposit.update_from_dict({"settled": True})
        await dep.save(update_fields=("settled",))
        account.balance = F("balance") + deposit.amount_due
        await account.save(update_fields=("balance",))
        message = f"Your deposit has matured and your account has been credited with {deposit.amount_due}"
        email = AccountAlertEmail(name=user.email, recipients=[user.email], message=message)
        await email.send()
        return ResponseModel(message="Deposit Settled")


@error_handler(error="Unable to confirm deposit")
async def confirm_deposit(*, deposit_id) -> ResponseModel:
    async with in_transaction():
        deposit = await DepositORM.get_or_none(deposit_id=deposit_id, confirmed=False).prefetch_related("account__user__referral", "plan")
        if deposit is None:
            return ResponseModel(message="Deposit not found")

        account = deposit.account
        plan = Plan.from_orm(deposit.plan)
        pd = plan.get_payment_details(deposit=deposit.amount)

        if (referral := account.user.referral) and not account.user.referral.paid:
            await pay_referral(referral, pd["referral"])

        dates = plan.get_date()
        await deposit.update_from_dict({"confirmed": True, "amount_due": pd["due"], **dates})
        await deposit.save(update_fields=("confirmed", "payment_date", "due_date", "amount_due"))

        user = account.user
        email = DepositConfirmationEmail(name=user.name, payment_date=deposit.payment_date, due_date=deposit.due_date, plan=plan.name,
                                         amount=deposit.amount, deposit_id=deposit_id, recipients=[user.email])
        await email.send()
        return ResponseModel(message="Successfully Confirmed Deposit")


async def pay_referral(referral: ReferralORM, amount: float):
    try:
        async with in_transaction():
            await referral.fetch_related("referred", "referrer__account")
            ref = await referral.update_from_dict({"amount": amount, "paid": True})
            await ref.save(update_fields=("amount", "paid"))
            acc = referral.referrer.account
            acc.balance = F("balance") + amount
            await acc.save(update_fields=("balance",))
            user = referral.referrer
            message = f"""You have received a sum ${amount} for referring {referral.referred.name}"""
            email = ReferralEmail(name=user.name, recipients=[user.email], message=message)
            await email.send()
    except Exception as err:
        print(err)


@error_handler(error="Unable to create request")
async def create_withdrawal(req: Request, wit: WithdrawalCreate) -> ResponseModel:
    async with in_transaction():
        user = req.state.user
        wit = Withdrawal(**wit.dict())
        await WithdrawalORM.create(**wit.dict(exclude_none=True), account_id=user.account.account_id)
        await update_account(acc_id=user.account.account_id, amount=wit.amount)
        message = f"""You have requested for a withdrawal of ${wit.amount}
        You will be notified once will process your withdrawal usually between 12 and 24 hours."""
        email = WithdrawalEmail(name=user.name, recipients=[user.email], message=message)
        await email.send()
        return ResponseModel(message=f"Withdrawal request for $f{wit.amount} received")


@error_handler(error="Unable to complete withdrawal")
async def complete_withdrawal(*, wit_id) -> ResponseModel:
    async with in_transaction():
        wit = await WithdrawalORM.get(withdrawal_id=wit_id).prefetch_related("account__user")
        user = wit.account.user
        await wit.update_from_dict({"paid": True})
        await wit.save(update_fields=("paid",))
        message = f"""We are pleased to inform you that your withdrawal of {wit.amount} has been successful processed."""
        email = WithdrawalEmail(name=user.name, recipients=[user.email], title="Withdrawal Completed", subject="Withdrawal Confirmation",
                                message=message)
        await email.send()
        return ResponseModel(message="Withdrawal completed")
