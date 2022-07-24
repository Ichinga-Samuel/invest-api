from models.account import Deposit, Account, Plan, PlanEnum, AccountORM, PlanORM, DepositORM, DepositCreate
from models.user import UserCreate, UserORM, User
from utils import timedelta

users = [
    User(**(UserCreate(name="Ichinga", email="ichingasamuel@gmail.com", gender="Male", password="password", password_confirm="password").dict())),
]

ref_users = [
    User(**UserCreate(name="Samuel", email="samuelichinga@gmail.com", gender="Male", password="password", password_confirm="password",
               referrer_id=users[0].referral_id).dict())
]

plans = [
    Plan(
        name=PlanEnum.Basic,
        minimum=20,
        maximum=499,
        payout=20,
        referral_bonus=5,
        duration=timedelta(hours=20),
    ),

    Plan(
        name=PlanEnum.Gold,
        minimum=500,
        maximum=1999,
        payout=30,
        referral_bonus=5,
        duration=timedelta(hours=48)
    ),

    Plan(
        name=PlanEnum.Master,
        minimum=2000,
        maximum=4999,
        payout=45,
        referral_bonus=10,
        duration=timedelta(hours=72)
    ),

    Plan(
        name=PlanEnum.Premium,
        minimum=5000,
        maximum=9999,
        payout=60,
        referral_bonus=10,
        duration=timedelta(hours=96)
    ),

    Plan(
        name=PlanEnum.VIP,
        minimum=10000,
        maximum=1000000000,
        payout=120,
        referral_bonus=10,
        duration=timedelta(hours=120)
    )
]

deps = [("Basic", 300), ("Gold", 1500), ("Master", 3000), ("Premium", 6000), ("VIP", 20000)]

r_deps = [("Basic", 250), ("Gold", 1000), ("Master", 4000), ("Premium", 7000), ("VIP", 15000)]

accounts = [Account(user_id=user.user_id) for user in users]

ref_accounts = [Account(user_id=user.user_id) for user in ref_users]

deposits = [Deposit(**DepositCreate(plan_id=dep[0], amount=dep[1]).dict(), account_id=account.account_id) for account, dep in zip(accounts, deps)]

ref_deposits = [Deposit(**DepositCreate(plan_id=dep[0], amount=dep[1]).dict(), account_id=account.account_id) for account, dep in zip(accounts, r_deps)]
