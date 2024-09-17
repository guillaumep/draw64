from contextlib import asynccontextmanager

from fastapi import FastAPI

from draw64.api_router import router as api_router
from draw64.sse_router import router as sse_router
from draw64.ws_router import router as ws_router
from draw64.state import stop_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    # App init (nothing done here)
    # Give control to the application
    yield
    # App shutdown
    stop_event.set()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
app.include_router(sse_router)
app.include_router(ws_router)
