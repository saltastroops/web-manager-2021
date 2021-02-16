import base64

from fastapi import FastAPI
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse, Response

from app.routers.api import router as api_router
from app.routers.views import router as views_router

app = FastAPI()

app.include_router(api_router)
app.include_router(views_router)


def _is_api_request(request: Request) -> bool:
    """Check whether a request is an API request."""

    return request.url.path.startswith("/api/") or request.url.path.startswith("api/")


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    """
    Error handler for HTTP exceptions.

    For API requests a JSON object with a detail property is returned.

    For web page requests a redirection response (for Authorization exceptions, i.e.
    for exceptions with a status code of 401)
    """
    if _is_api_request(request):
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        redirect = base64.b64encode(str(request.url).encode("utf-8")).decode("utf-8")
        return RedirectResponse(
            url=f"/login?redirect={redirect}", status_code=status.HTTP_303_SEE_OTHER
        )

    return HTMLResponse("<h1>Error</h1>", status_code=exc.status_code)
