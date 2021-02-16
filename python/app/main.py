from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.routers.api import router as api_router
from app.routers.views import router as views_router

app = FastAPI()

app.include_router(api_router)
app.include_router(views_router)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse({"detail": str(exc.detail)}, status_code=exc.status_code)
