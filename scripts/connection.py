from tortoise import Tortoise, run_async

from config.db import TORTOISE_ORM
from scripts.user import create_admin, create_users
from scripts.account import create_plans, create_accounts, create_deposits


async def connect():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)
    await create_users()
    await create_admin()
    await create_plans()
    await create_accounts()
    await create_deposits()
    print("Complete!")

run_async(connect())
