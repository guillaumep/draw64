import asyncio
import logging
from typing import cast

from fastapi import APIRouter, WebSocket

from draw64.event import EventMessage
from draw64.event_factory import (
    make_user_connected_message,
    make_user_disconnected_message,
)
from draw64.image_collection import collection
from draw64.image_id import ImageID
from draw64.pubsub import announcer, pubsub, SubscribedQueue
from draw64.update_image_request import UpdateImageRequest

router = APIRouter()


def handle_websocket_input(input: str, image_id: ImageID):
    try:
        update_request = UpdateImageRequest.model_validate_json(input)
        collection[image_id].update(update_request.command)
    except Exception:
        logging.exception(f"Error handling websocket input: {input}")


async def handle_websocket(
    image_id: ImageID, websocket: WebSocket, message_queue: SubscribedQueue
):
    while True:
        done_tasks, pending_tasks = await asyncio.wait(
            [
                asyncio.create_task(websocket.receive_text(), name="receive_text"),
                asyncio.create_task(message_queue.get(), name="get_from_pubsub"),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for pending in pending_tasks:
            pending.cancel()

        for done in done_tasks:
            result = done.result()
            if done.get_name() == "receive_text":
                handle_websocket_input(result, image_id)
            else:
                event_message = cast(EventMessage, result)
                await websocket.send_text(event_message.model_dump_json())


@router.websocket("/ws/images/{image_id}")
async def websocket_image_endpoint(image_id: ImageID, websocket: WebSocket):
    await websocket.accept()
    announcer.broadcast(make_user_connected_message())
    message_queue = pubsub.subscribe(image_id)

    # Automatically create images when using the websocket API
    if image_id not in collection:
        collection.create_image(image_id, force=True)

    try:
        await handle_websocket(image_id, websocket, message_queue)
    except Exception:
        message_queue.unsubscribe()
        announcer.broadcast(make_user_disconnected_message())
