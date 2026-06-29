from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from fastapi import FastAPI

from database import init_database
from routers import room, user
from routers.wordbank import router as wordbank_router
from ws.handlers import router as ws_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_database()
    yield


app = FastAPI(title="Wordle Game API", lifespan=lifespan)

app.include_router(room.router)
app.include_router(user.router)
app.include_router(wordbank_router)
app.include_router(ws_router)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
