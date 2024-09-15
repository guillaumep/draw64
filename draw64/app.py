import asyncio
import logging
from typing import Annotated, cast

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Path,
    Response,
    status,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse

from draw64.connection_manager import WSConnectionManager
from draw64.image import Image, ImageData
from draw64.image_collection import ImageCollection, ImageIDAlreadyExistsException
from draw64.update_image_request import UpdateImageRequest
from draw64.pubsub import PubSub

app = FastAPI()
conn_mananger = WSConnectionManager()
collection = ImageCollection()
pubsub = PubSub()


ImageID = Annotated[str, Path(max_length=30, pattern=r"^[a-zA-Z\d]+$")]


async def validate_image_id(image_id: ImageID):
    if image_id not in collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image ID not found."
        )
    return image_id


ValidatedImageID = Annotated[str, Depends(validate_image_id)]

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws/img1");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.get("/images")
async def get_images_list() -> list[Image]:
    return list(collection.values())


@app.post("/images", status_code=status.HTTP_201_CREATED)
async def create_image() -> Image:
    return collection.create_image()


@app.post(
    "/images/{image_id}",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "Image ID already exists."}},
)
async def create_image_with_id(image_id: ImageID) -> Image:
    """
    Create an image, providing an ID.
    """
    try:
        return collection.create_image(image_id)
    except ImageIDAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Image ID already exists."
        )


@app.get(
    "/images/{image_id}.png",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def get_image_as_png(image_id: ValidatedImageID):
    return Response(content=collection[image_id].to_png(), media_type="image/png")


@app.get(
    "/images/{image_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def get_image(image_id: ValidatedImageID) -> Image:
    return collection[image_id]


@app.get(
    "/images/{image_id}/data",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def get_image_data(image_id: ValidatedImageID) -> ImageData:
    return collection[image_id].data


def _update_image(image_id: ValidatedImageID, update_request: UpdateImageRequest):
    collection[image_id].update(update_request.command)
    pubsub.broadcast(image_id, update_request)


@app.put("/images/{image_id}")
async def update_image(image_id: ValidatedImageID, update_request: UpdateImageRequest):
    _update_image(image_id, update_request)


@app.delete(
    "/images/{image_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def delete_image(image_id: ValidatedImageID):
    del collection[image_id]


@app.websocket("/ws/{image_id}")
async def websocket_endpoint(image_id: ImageID, websocket: WebSocket):
    # FIXME: might want to ask the caller to properly create its image
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
                        _update_image(image_id, update_request)
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
