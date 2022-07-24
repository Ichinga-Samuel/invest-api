from scripts import AccountORM, PlanORM, DepositORM, deposits, accounts, plans, ref_accounts, ref_deposits


async def create_accounts():
    await AccountORM.bulk_create(objects=[AccountORM(**account.dict()) for account in accounts])
    await AccountORM.bulk_create(objects=[AccountORM(**account.dict()) for account in ref_accounts])


async def create_deposits():
    await DepositORM.bulk_create(objects=[DepositORM(**deposit.dict()) for deposit in deposits])
    await DepositORM.bulk_create(objects=[DepositORM(**deposit.dict()) for deposit in ref_deposits])


async def create_plans():
    await PlanORM.bulk_create(objects=[PlanORM(**plan.dict()) for plan in plans])
