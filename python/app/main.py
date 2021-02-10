from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema=False)
def home(request: Request) -> Response:
    return templates.TemplateResponse("home.html", {"request": request})
