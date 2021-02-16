import urllib
from typing import Optional
import base64
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.templating import Jinja2Templates, _TemplateResponse

from app.dependencies import get_settings
from app.models.pydantic import User
from app.settings import Settings
from app.util import auth
from app.util.auth import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
def login(request: Request, redirect: Optional[str]=None) -> Response:
    if not redirect:
        redirect = base64.b64encode(b"/").decode("utf-8")

    return templates.TemplateResponse("login.html", {"request": request, "redirect": redirect})


@router.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: Optional[str]=Form(""), password: Optional[str]=Form(""), redirect: Optional[str]=None, settings: Settings=Depends(get_settings)) -> Response:
    if not redirect:
        redirect = base64.b64encode(b"/").decode("utf-8")

    user = auth.authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "username": username, "incorrect_credentials": True, "redirect": redirect})

    token = auth.create_access_token(settings.secret_key, user)
    token_value = "Bearer " + quote(token.access_token)
    quoted_token_value = quote(token_value)
    redirect_url = base64.b64decode(redirect).decode("utf-8")
    response = RedirectResponse(url=redirect_url)
    response.set_cookie("Authorization", quoted_token_value)

    return response


@router.get("/proposals", response_class=HTMLResponse)
def proposals(user: User = Depends(get_current_user)) -> Response:
    return HTMLResponse("<h1>Proposals")
