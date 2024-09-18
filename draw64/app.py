import asyncio

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
from fastapi.staticfiles import StaticFiles

from draw64.routes.api import router as api_router
from draw64.routes.sse import router as sse_router
from draw64.routes.ws import router as ws_router
from draw64.statistics import (
    update_statistics_from_announcer,
    update_statistics_from_pubsub,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # App init
    loop = asyncio.get_running_loop()
    loop.create_task(update_statistics_from_announcer())
    loop.create_task(update_statistics_from_pubsub())

    # Give control to the application
    yield
    # App shutdown


async def no_cache(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store"


app = FastAPI(lifespan=lifespan, dependencies=[Depends(no_cache)])
app.include_router(api_router)
app.include_router(sse_router)
app.include_router(ws_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
