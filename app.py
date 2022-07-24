import pathlib

import aioredis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from admin import app as admin_app, Admin, LoginProvider
from config.db import TORTOISE_ORM
from config.env import env
from dependencies.account import settle_deposits
from routes import user_router, auth_router
from utils import HttpExceptionResponse, RequestValidationErrorResponse

origins = [
    "http:localhost:4200",
    "http:localhost",
    "http:localhost:8080",
    "http:localhost:8000"
]

app = FastAPI()

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    res = HttpExceptionResponse(message=exc.detail)
    if exc.headers:
        res.headers = exc.headers
    return JSONResponse(content=jsonable_encoder(res, exclude_unset=True), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    res = RequestValidationErrorResponse(detail=exc.errors(), body=exc.body)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(res),
    )


app.mount('/admin', admin_app)

app.include_router(user_router, prefix='/api/v1')
app.include_router(auth_router, prefix='/api/v1')


@app.get('/')
def home():
    return RedirectResponse('/docs')


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="http://localhost:\d{4,5}",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
async def startup():
    redis = aioredis.from_url(url=env.REDIS_URL, decode_responses=True, encoding='utf8')
    await admin_app.configure(
        logo_url="https://preview.tabler.io/static/logo-white.svg",
        template_folders=[env.BASE_DIR / 'templates/admin'],
        favicon_url="https://raw.githubusercontent.com/fastapi-admin/fastapi-admin/dev/images/favicon.png",
        providers=[
            LoginProvider(
                login_logo_url="https://preview.tabler.io/static/logo.svg",
                admin_model=Admin,
            )
        ],
        redis=redis,
    )
    scheduler = AsyncIOScheduler()
    scheduler.add_job(settle_deposits, 'cron', hour=23, minute=59, timezone="Africa/Lagos")
    scheduler.start()
