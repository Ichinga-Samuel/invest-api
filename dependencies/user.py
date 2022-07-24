from fastapi import HTTPException, Depends, status

from models.account import (DepositView, ReferralView, AccountView, WithdrawalView, AccountORM, Account)
from models.user import UserORM, UserView, User, UserEdit
from utils import error_handler, ResponseModel
from .auth import get_user_from_token


# ToDo: Add logging for direct path operation functions, and dependencies


# TODO: get full dashboard of all user details and transactions
async def get_current_user(user: UserORM = Depends(get_user_from_token)) -> UserView:
    try:
        await user.fetch_related('account', 'referrals')
        account: AccountORM = user.account
        acc = Account.from_orm(account)
        await account.fetch_related('deposits', 'withdrawals')
        deposits = [DepositView.from_orm(deposit) for deposit in account.deposits]
        withdrawals = [WithdrawalView.from_orm(wit) for wit in account.withdrawals]
        referrals = [ReferralView.from_orm(ref) for ref in user.referrals]
        account_details = AccountView(deposits=deposits, withdrawals=withdrawals, **acc.dict())
        user_ = User.from_orm(user)
        user_view = UserView(**user_.dict())
        user_view.account_details = account_details
        user_view.referrals = referrals
        return user_view
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something Went Wrong")


@error_handler(error="Unable to update user account")
async def update_user(update: UserEdit, user: UserORM = Depends(get_user_from_token)) -> ResponseModel:
    await user.update_from_dict(**update.dict(exclude_unset=True))
    updates = tuple(update.dict(exclude_unset=True).keys())
    await user.save(update_fields=updates)
    return ResponseModel(message="User update successful")

