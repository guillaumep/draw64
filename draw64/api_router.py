from fastapi import (
    APIRouter,
    HTTPException,
    Response,
    status,
)
from fastapi.responses import HTMLResponse

from draw64.image import Image, ImageData
from draw64.image_collection import ImageIDAlreadyExistsException
from draw64.image_id import ImageID, ValidatedImageID
from draw64.state import pubsub, collection
from draw64.update_image_request import UpdateImageRequest
from draw64.event_factory import (
    make_image_created_message,
    make_image_deleted_message,
    make_image_updated_message,
)

router = APIRouter()


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


@router.get("/")
async def get():
    return HTMLResponse(html)


@router.get("/images")
async def get_images_list() -> list[Image]:
    return list(collection.values())


@router.post("/images", status_code=status.HTTP_201_CREATED)
async def create_image() -> Image:
    image = collection.create_image()
    pubsub.broadcast_all(make_image_created_message(image))
    return image


@router.post(
    "/images/{image_id}",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "Image ID already exists."}},
)
async def create_image_with_id(image_id: ImageID) -> Image:
    """
    Create an image, providing an ID.
    """
    try:
        image = collection.create_image(image_id)
        pubsub.broadcast_all(make_image_created_message(image))
        return image
    except ImageIDAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Image ID already exists."
        )


@router.get(
    "/images/{image_id}.png",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def get_image_as_png(image_id: ValidatedImageID):
    return Response(content=collection[image_id].to_png(), media_type="image/png")


@router.get(
    "/images/{image_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def get_image(image_id: ValidatedImageID) -> Image:
    return collection[image_id]


@router.get(
    "/images/{image_id}/data",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def get_image_data(image_id: ValidatedImageID) -> ImageData:
    return collection[image_id].data


@router.put("/images/{image_id}")
async def update_image(image_id: ValidatedImageID, update_request: UpdateImageRequest):
    collection[image_id].update(update_request.command)
    pubsub.broadcast(image_id, make_image_updated_message(image_id, update_request))


@router.delete(
    "/images/{image_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def delete_image(image_id: ValidatedImageID):
    pubsub.broadcast_all(make_image_deleted_message(collection[image_id]))
    del collection[image_id]
