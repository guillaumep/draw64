from typing import Annotated

from fastapi import FastAPI, Path, Response, status

from draw64.connection_manager import WSConnectionManager
from draw64.image_collection import ImageCollection, ImageIDAlreadyExistsException
from draw64.models import DrawRequest

app = FastAPI()
conn_mananger = WSConnectionManager()
collection = ImageCollection()

# FIXME: la validation sur le regex ne semble pas se faire
ImageID = Annotated[str, Path(pattern=r"[\da-z]+")]


@app.post("/images", status_code=status.HTTP_201_CREATED)
async def create_image() -> str:
    """
    Create an image and return its ID.
    """
    return collection.create_image()


@app.post(
    "/images/{image_id}",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "Image ID already exists."}},
)
async def create_image_with_id(image_id: ImageID) -> str:
    """
    Create an image, providing an ID.
    """
    try:
        return collection.create_image(image_id)
    except ImageIDAlreadyExistsException:
        return Response(status_code=status.HTTP_409_CONFLICT)


# TODO
@app.get("/images/{image_id}")
async def get_image(image_id: ImageID):
    pass


@app.put("/images/{image_id}")
async def update_image(image_id: ImageID, draw_request: DrawRequest):
    # TODO: use a dependency to remove code duplication
    if image_id not in collection:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    collection[image_id].update(draw_request.command)


@app.delete(
    "/images/{image_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def delete_image(image_id: ImageID):
    if image_id not in collection:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    collection.delete_image(image_id)
    return f"Image {image_id} deleted."


# @app.websocket("/ws/{image_id}")
# async def websocket_endpoint(image_id: ImageID, websocket: WebSocket):
#     client_id = hash(websocket)
#     await conn_mananger.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await conn_mananger.send_personal_message(f"You wrote: {data}", websocket)
#             await conn_mananger.broadcast(f"Client #{client_id} says: {data}")
#     except WebSocketDisconnect:
#         conn_mananger.disconnect(websocket)
#         await conn_mananger.broadcast(f"Client #{client_id} left the chat")
