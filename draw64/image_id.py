from typing import Annotated

from fastapi import Depends, HTTPException, Path, status

from draw64.image_collection import collection


ImageID = Annotated[str, Path(max_length=30, pattern=r"^[a-zA-Z\d-]+$")]


async def validate_image_id(image_id: ImageID):
    if image_id not in collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image ID not found."
        )
    return image_id


ValidatedImageID = Annotated[str, Depends(validate_image_id)]
