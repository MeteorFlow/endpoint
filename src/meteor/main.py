import time
import logging
from os import path
from uuid import uuid1

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from starlette.routing import compile_path

from .logging import configure_logging

from .api import api_router

# we configure the logging level and format
log = logging.getLogger(__name__)
configure_logging()

#
async def not_found(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": [{"msg": "Not Found."}]}
    )
exception_handlers = {404: not_found}


# we create the ASGI for the app
app = FastAPI(exception_handlers=exception_handlers, openapi_url="")
app.state.limiter = Limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def get_path_params_from_request(request: Request) -> str:
    path_params = {}
    for r in APIRouter.routes:
        path_regex, path_format, param_converters = compile_path(r.path)
        path = request["path"].removeprefix("/api/v1")  # remove the /api/v1 for matching
        match = path_regex.match(path)
        if match:
            path_params = match.groupdict()
    return path_params


def get_path_template(request: Request) -> str:
    if hasattr(request, "path"):
        return ",".join(request.path.split("/")[1:])
    return ".".join(request.url.path.split("/")[1:])

api = FastAPI(
    title="meteorDB API",
    description="API for meteorDB",
    root_path="/api/v1",
    docs_url=None,
    openapi_url="/docs/openapi.json",
    redoc_url="/docs",
)

# we add all API routes to the Web API framework
api.include_router(api_router)

app.mount("/api/v1", app=api)