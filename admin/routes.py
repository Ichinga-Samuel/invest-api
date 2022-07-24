from fastapi import Depends, Request
from fastapi_admin.depends import get_resources
from fastapi_admin.template import templates
from fastapi_admin.app import app

from dependencies.account import confirm_deposit, complete_withdrawal, settle_deposit as settle


@app.get("/")
async def home(request: Request, resources=Depends(get_resources)):
    return templates.TemplateResponse(
        "dashboard.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Dashboard",
            "page_pre_title": "overview",
            "page_title": "Dashboard",
        },
)


@app.post("/{resource}/confirm/{deposit_id}")
async def confirm_deposit(msg: dict = Depends(confirm_deposit)):
    return msg


@app.post("/{resource}/settle_deposit/{deposit_id}")
async def settle_deposit(msg: dict = Depends(settle)):
    return msg


@app.post("/{resource}/settle/{wit_id}")
async def settle_withdrawal(request: Request, msg: dict = Depends(complete_withdrawal)):
    return msg


