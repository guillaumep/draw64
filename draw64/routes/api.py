from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
    Response,
    status,
)
from fastapi.responses import HTMLResponse

from draw64.image import Image, ImageData
from draw64.image_collection import (
    collection,
    ImageIDAlreadyExistsException,
    TooManyImagesException,
)
from draw64.image_id import ImageID, ValidatedImageID
from draw64.statistics import statistics, Statistics
from draw64.update_image_request import UpdateImageRequest

router = APIRouter()


@router.get("/", include_in_schema=False)
async def get():
    # NOTE: once development is done we could read the file only once
    return HTMLResponse(
        open(Path(__file__).parent.parent.parent / "index.html", "r").read()
    )


@router.get("/images")
async def get_images_list() -> list[Image]:
    return list(collection.values())


@router.post(
    "/images",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"description": "Too many images already created."}
    },
)
async def create_image() -> Image:
    try:
        return collection.create_image()
    except TooManyImagesException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Too many images already created.",
        )


@router.post(
    "/images/{image_id}",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Image ID already exists or too many images already created."
        }
    },
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
    except TooManyImagesException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Too many images already created.",
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


@router.delete(
    "/images/{image_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def delete_image(image_id: ValidatedImageID):
    del collection[image_id]


@router.get("/statistics")
async def get_statistics() -> Statistics:
    return statistics
