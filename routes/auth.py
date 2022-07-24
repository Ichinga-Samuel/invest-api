from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from dependencies.auth import authenticate_user, password_change, password_reset, reset_password, verify_account
from utils import ResponseModel, Token

router = APIRouter(prefix='/auth')


@router.post('/login', response_model=Token)
async def login_user(token: Token = Depends(authenticate_user)) -> Token:
    return token


@router.get('/verify/{token}', response_class=RedirectResponse, status_code=302)
async def get(res=Depends(verify_account)):
    return f"https://{res}?msg=verified"


@router.post('/changepassword', response_model=ResponseModel)
async def change_password(res: ResponseModel = Depends(password_change)) -> ResponseModel:
    return res


@router.post('/resetpassword', response_model=ResponseModel)
async def reset_password(res: ResponseModel = Depends(reset_password)) -> ResponseModel:
    return res


@router.post('/passwordreset', response_model=ResponseModel)
async def password_reset(res: ResponseModel = Depends(password_reset)) -> ResponseModel:
    return res
