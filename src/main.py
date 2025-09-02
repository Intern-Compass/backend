import time

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from routers.general_user_router import router as general_user_router
from routers.intern_auth_router import router as intern_router
from src.logger import logger

app = FastAPI()

ORIGINS =  [
    "*"
]
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
        status_code=500,
        content={"detail": "An error occured. Check server"},
    )

@app.get("/")
async def greet(add_exc: bool = False):
    if add_exc:
        raise Exception
    return "Hello World"

app.include_router(general_user_router)
app.include_router(intern_router)