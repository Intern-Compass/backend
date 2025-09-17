import time

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_429_TOO_MANY_REQUESTS

from .routers.supervisor_router import router as supervisor_router
from .routers.auth_router import router as auth_router
from .routers.skill_router import router as skill_router
from .routers.intern_router import router as intern_router
from .routers.project_router import router as project_router

from .logger import logger
from .utils import limiter

app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded"},
    )


ORIGINS = ["http://localhost:3000", "https://intern-compass.vercel.app"]
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def measure_response_time(request: Request, call_next):
    """Measures the time to process requests and adds it to the response header."""
    start_time = time.perf_counter()  # Start timer
    response = await call_next(request)  # Process request
    duration = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
    response.headers["X-Process-Time"] = str(duration)
    return response


@app.exception_handler(Exception)
async def custom_exception_handler(_: Request, exc: Exception):
    logger.error(f"{str(exc)}")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An error occured. Check server"},
    )


@app.get("/")
# @limiter.limit("5/minute")
async def greet(request: Request, response: Response):
    return "Hello World"


app.include_router(auth_router)
app.include_router(skill_router)
app.include_router(supervisor_router)
app.include_router(intern_router)
app.include_router(project_router)
