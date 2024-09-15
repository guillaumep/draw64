import asyncio
import logging
from typing import cast

from fastapi import (
    APIRouter,
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)

from draw64.update_image_request import UpdateImageRequest
from draw64.api_router import router as api_router
from draw64.state import collection, conn_mananger, pubsub
from draw64.image_id import ImageID

router = APIRouter()

app = FastAPI()
app.include_router(api_router)


@app.websocket("/ws/{image_id}")
async def websocket_endpoint(image_id: ImageID, websocket: WebSocket):
    # FIXME: might want to ask the caller to properly create its image
    # (and thus type image_id as ValidatedImageID)
    if image_id not in collection:
        collection.create_image(image_id)

    message_queue = pubsub.subscribe(image_id)
    await conn_mananger.connect(websocket)
    try:
        while True:
            done_tasks, pending_tasks = await asyncio.wait(
                [
                    asyncio.create_task(websocket.receive_text()),
                    asyncio.create_task(message_queue.get()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for done in done_tasks:
                result = done.result()
                if isinstance(result, str):
                    try:
                        update_request = UpdateImageRequest.model_validate_json(result)
                        collection[image_id].update(update_request.command)
                        pubsub.broadcast(image_id, update_request)
                    except Exception:
                        logging.exception(f"Error handling websocket input: {result}")
                else:
                    broadcasted_request = cast(UpdateImageRequest, result)
                    await websocket.send_text(broadcasted_request.model_dump_json())
            for pending in pending_tasks:
                pending.cancel()

    except WebSocketDisconnect:
        message_queue.unsubscribe()
        conn_mananger.disconnect(websocket)
