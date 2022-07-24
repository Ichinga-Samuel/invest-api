import asyncio

from dependencies.auth import hash_password, create_referral

from models.admin import Admin
from scripts import users, UserORM, ref_users, UserCreate


async def create_user(user: UserCreate):
    user_ = await UserORM.create(**user.dict(), password_hash=hash_password(user.password))
    if user.referrer_id:
        await create_referral(referrer_id=user.referrer_id, referred_id=user_.user_id)


async def create_users():
    await UserORM.bulk_create(objects=[UserORM(**user.dict(), password_hash=hash_password(user.password)) for user in users])
    tasks = [create_user(user) for user in ref_users]
    await asyncio.gather(*tasks)


async def create_admin():
    await Admin.create(username="SuperAdmin", password="SuperAdmin")
