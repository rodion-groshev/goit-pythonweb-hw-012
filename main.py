from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from src.api import utils, contacts, auth, users
from fastapi.middleware.cors import CORSMiddleware
import redis
from redis_lru import RedisLRU

app = FastAPI()

origins = ["127.0.0.1:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handles exceptions raised when a rate limit is exceeded.

    This function is triggered when the `RateLimitExceeded` exception occurs,
    returning a JSON response with a 429 status code indicating too many requests.

    Args:
        request (Request): The incoming HTTP request that triggered the exception.
        exc (RateLimitExceeded): The exception instance containing details about the rate limit breach.

    Returns:
        JSONResponse: A response containing an error message and a 429 status code.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )


app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
