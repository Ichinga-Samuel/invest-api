from fastapi import APIRouter, Depends, Response

from dependencies.account import create_deposit, create_withdrawal
from dependencies.auth import get_user_from_token, create_user, verify_user, ResponseModel
from dependencies.user import get_current_user, update_user
from models.user import UserView

router = APIRouter(prefix='/user')


@router.post('/create', status_code=201, response_model=ResponseModel)
async def create(resp: Response, res: ResponseModel = Depends(create_user)) -> ResponseModel:
    if not res.status:
        resp.status_code = 200
    return res


@router.post('/update', response_model=ResponseModel)
async def update(res: ResponseModel = Depends(update_user)) -> ResponseModel:
    return res


@router.get('/me', dependencies=[Depends(get_user_from_token)], response_model=UserView)
async def get(user: UserView = Depends(get_current_user)) -> UserView:
    return user


@router.get('/verify', response_model=ResponseModel)
async def get(res: ResponseModel = Depends(verify_user)) -> ResponseModel:
    return res


@router.post('/deposit', dependencies=[Depends(get_user_from_token)], response_model=ResponseModel)
async def deposit(res: ResponseModel = Depends(create_deposit)) -> ResponseModel:
    return res


@router.post('/withdraw', dependencies=[Depends(get_user_from_token)], response_model=ResponseModel)
async def withdraw(res: ResponseModel = Depends(create_withdrawal)) -> ResponseModel:
    return res
