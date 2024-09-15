import asyncio
import logging
from typing import cast

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from draw64.image_id import ImageID
from draw64.pubsub import SubscribedQueue
from draw64.state import collection, conn_mananger, pubsub
from draw64.update_image_request import UpdateImageRequest

router = APIRouter()


def handle_websocket_input(input: str, image_id: ImageID):
    try:
        update_request = UpdateImageRequest.model_validate_json(input)
        collection[image_id].update(update_request.command)
        pubsub.broadcast(image_id, update_request)
    except Exception:
        logging.exception(f"Error handling websocket input: {input}")


async def handle_websocket(
    image_id: ImageID, websocket: WebSocket, message_queue: SubscribedQueue
):
    while True:
        done_tasks, pending_tasks = await asyncio.wait(
            [
                asyncio.create_task(websocket.receive_text()),
                asyncio.create_task(message_queue.get()),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for pending in pending_tasks:
            pending.cancel()

        for done in done_tasks:
            result = done.result()
            if isinstance(result, str):
                handle_websocket_input(result, image_id)
            else:
                broadcasted_request = cast(UpdateImageRequest, result)
                await websocket.send_text(broadcasted_request.model_dump_json())


@router.websocket("/ws/{image_id}")
async def websocket_endpoint(image_id: ImageID, websocket: WebSocket):
    # FIXME: might want to ask the caller to properly create its image
    # (and thus type image_id as ValidatedImageID)
    if image_id not in collection:
        collection.create_image(image_id)

    message_queue = pubsub.subscribe(image_id)
    await conn_mananger.connect(websocket)
    try:
        await handle_websocket(image_id, websocket, message_queue)

    except WebSocketDisconnect:
        message_queue.unsubscribe()
        conn_mananger.disconnect(websocket)
