from fastapi import FastAPI

from draw64.api_router import router as api_router
from draw64.ws_router import router as ws_router

app = FastAPI()
app.include_router(api_router)
app.include_router(ws_router)
