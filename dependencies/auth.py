from fastapi import HTTPException, Depends, status, Path, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.transactions import in_transaction

from config.env import env
from models.account import ReferralORM, Referral, Account
from models.user import UserORM, UserCreate, User, PasswordChange, PasswordReset, ResetPassword
from utils import now, timedelta, error_handler, ResponseModel, Token
from utils.emails import VerificationEmail, PasswordResetEmail
from .account import create_account

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_in: float = 24) -> str:
    exp = now() + timedelta(hours=expires_in)
    data.update({'exp': exp})
    return jwt.encode(data, env.SECRET_KEY, env.ALGORITHM)


def decode_access_token(token, detail: str = "Invalid Token", headers=None):
    try:
        payload = jwt.decode(token, env.SECRET_KEY, algorithms=[env.ALGORITHM])
        return payload
    except JWTError:
        headers = {} if not headers else {"WWW-Authenticate": "Bearer"}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers)


async def get_user_from_token(req: Request, token: str = Depends(oauth2_scheme)) -> UserORM:
    try:
        payload = decode_access_token(token, detail="Your session has expires please login again", headers=credentials.headers)
        user = await UserORM.get(email=payload.get('sub')).prefetch_related('account')
        req.state.user = user
        return user
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No User With This Email", headers={"WWW-Authenticate": "Bearer"})


async def authenticate_user(login: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = await UserORM.get(email=login.username)
    if not verify_password(login.password, user.password_hash):
        raise credentials

    await user.save(update_fields=('last_login',))
    data = {'password': login.password, 'sub': login.username, 'last_login': str(now())}
    token = create_access_token(data)
    return Token(accessToken=token)


async def create_referral(*, referrer_id: str, referred_id: int):
    referrer = await UserORM.get(referral_id=referrer_id)
    ref = Referral(referrer_id=referrer.user_id, referred_id=referred_id)
    await ReferralORM.create(**ref.dict(exclude_none=True))


@error_handler(error="Unable to create your account at this time. Try again")
async def create_user(user_create: UserCreate, req: Request) -> ResponseModel:
    async with in_transaction():
        pwd_hash = hash_password(user_create.password)
        user = User(**user_create.dict())
        user = await UserORM.create(**user.dict(), password_hash=pwd_hash)
        await create_account(Account(user_id=user.user_id))
        message = "User Successfully Created."
        token = create_access_token({'sub': user.email, 'client': req.client.host}, expires_in=2)
        link = f'{req.base_url}auth/verify/{token}'
        email = VerificationEmail(name=user.name, link=link, recipients=[user.email])
        res = await email.send()
        message = f"{message} A verification link has been sent to your email." if res else f"{message} Unable to verify your email."

        if user_create.referrer_id:
            await create_referral(referrer_id=user_create.referrer_id, referred_id=user.user_id)

        return ResponseModel(message=message)


@error_handler(error="Unable to change your password")
async def password_change(password_data: PasswordChange, user: UserORM = Depends(get_user_from_token)) -> ResponseModel:
    if not (verify_password(password_data.old_password, user.password_hash) and password_data.password == password_data.password_confirm):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    password_hash = hash_password(password_data.password)
    user = await user.update_from_dict({'password_hash': password_hash})
    await user.save(update_fields=('password_hash',))
    return ResponseModel(message="Password Change Successful")


@error_handler(error="Unable to verify your account")
async def verify_account(token: str = Path(...), ):
    payload = decode_access_token(token)
    client = payload.get('client')
    user = await UserORM.get(email=payload.get('sub'))
    await user.update_from_dict({"verified": True})
    await user.save(update_fields=('verified',))
    return client


@error_handler
async def verify_user(req: Request, user: UserORM = Depends(get_user_from_token)) -> ResponseModel:
    token = create_access_token(data={"client": req.client.host, "sub": user.email}, expires_in=2)
    link = f"{req.base_url}/auth/verify/{token}"
    email = VerificationEmail(name=user.name, link=link, recipients=[user.email])
    res = await email.send()
    if res:
        return ResponseModel(message="A verification link has been sent to your email address")
    return ResponseModel(message="Unable to verify your email address")


@error_handler(error="Password reset was unsuccessful")
async def reset_password(data: ResetPassword, req: Request) -> ResponseModel:
    email = data.email
    user = await UserORM.get_or_none(email=email)
    if not user:
        return ResponseModel(message="No User With This Email Address Was Found")
    token = create_access_token({'sub': email}, expires_in=2)
    link = f"https://{req.client.host}/user/resetpassword/{token}"
    email = PasswordResetEmail(name=user.name, link=link, recipients=[user.email])
    res = await email.send()
    message = "A password reset link, that will expire in two hours has been sent to your email address" if res else "Unable to send password reset " \
                                                                                                                     "link verify your email address"
    return ResponseModel(message=message)


@error_handler(error="Unable to change password")
async def password_reset(data: PasswordReset) -> ResponseModel:
    payload = decode_access_token(data.token)
    user = await UserORM.get_or_none(email=payload.get('sub'))
    if not user:
        return ResponseModel(message="No user with that email was found")
    await user.update_from_dict({"password_hash": hash_password(data.password)})
    await user.save(update_fields=('password_hash',))
    return ResponseModel(message="Password Reset Successful")
