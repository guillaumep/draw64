from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Response, status

from draw64.connection_manager import WSConnectionManager
from draw64.image import Image, ImageData
from draw64.image_collection import ImageCollection, ImageIDAlreadyExistsException
from draw64.update_image_request import UpdateImageRequest

app = FastAPI()
conn_mananger = WSConnectionManager()
collection = ImageCollection()

ImageID = Annotated[str, Path(max_length=30, pattern=r"^[a-zA-Z\d]+$")]


async def validate_image_id(image_id: ImageID):
    if image_id not in collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image ID not found."
        )
    return image_id


ValidatedImageID = Annotated[str, Depends(validate_image_id)]


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


@app.put("/images/{image_id}")
async def update_image(image_id: ValidatedImageID, update_request: UpdateImageRequest):
    collection[image_id].update(update_request.command)


@app.delete(
    "/images/{image_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def delete_image(image_id: ValidatedImageID):
    del collection[image_id]


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
