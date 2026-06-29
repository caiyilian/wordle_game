from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from database import init_database
from routers import user


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_database()
    yield


app = FastAPI(title="Wordle Game API", lifespan=lifespan)

app.include_router(user.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
