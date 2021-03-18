import base64
from typing import Optional
from urllib.parse import quote

from aiomysql import Pool
from fastapi import APIRouter, Depends, Form
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.templating import Jinja2Templates

from app.dependencies import (
    get_current_user,
    get_db,
    get_semester,
    get_settings,
)
from app.jinja2.filters import autoversion
from app.models.pydantic import Semester, User
from app.service import block as block_service
from app.settings import Settings
from app.util import auth

router = APIRouter()

templates = Jinja2Templates(directory="templates")

templates.env.filters["autoversion"] = autoversion


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> Response:
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
def login(request: Request, redirect: Optional[str] = None) -> Response:
    if not redirect:
        redirect = base64.b64encode(b"/").decode("utf-8")

    return templates.TemplateResponse(
        "login.html", {"request": request, "redirect": redirect}
    )


@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: Optional[str] = Form(""),
    password: Optional[str] = Form(""),
    redirect: Optional[str] = None,
    settings: Settings = Depends(get_settings),
    db: Pool = Depends(get_db),
) -> Response:
    if not redirect:
        redirect = base64.b64encode(b"/").decode("utf-8")

    if username and password:
        user = await auth.authenticate_user(username, password, db)
    else:
        user = None
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "username": username,
                "incorrect_credentials": True,
                "redirect": redirect,
            },
        )

    token = auth.create_access_token(settings.secret_key, user)
    token_value = "Bearer " + quote(token.access_token)
    quoted_token_value = quote(token_value)
    redirect_url = base64.b64decode(redirect).decode("utf-8")
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("Authorization", quoted_token_value)

    return response


@router.get("/proposals", response_class=HTMLResponse)
def proposals(user: User = Depends(get_current_user)) -> Response:
    return HTMLResponse("<h1>Proposals</h1>")


@router.get("/proposals/{proposal_code}", response_class=HTMLResponse)
async def proposal(
    request: Request,
    proposal_code: str,
    semester: Semester = Depends(get_semester),
    user: User = Depends(get_current_user),
    db: Pool = Depends(get_db),
) -> Response:
    block_codes = await block_service.get_block_codes(proposal_code, semester, db)
    return templates.TemplateResponse(
        "proposal.html",
        {
            "request": request,
            "proposal_code": proposal_code,
            "block_codes": block_codes,
        },
    )
