from draw64.event import (
    ImageEventMessage,
    ImageCreatedEvent,
    ImageDeletedEvent,
    ImageUpdatedEvent,
)
from draw64.image import Image
from draw64.image_id import ImageID
from draw64.update_image_request import UpdateImageRequest


def make_image_created_message(image: Image):
    return ImageEventMessage(event=ImageCreatedEvent(image_id=image.image_id))


def make_image_deleted_message(image: Image):
    return ImageEventMessage(event=ImageDeletedEvent(image_id=image.image_id))


def make_image_updated_message(image_id: ImageID, update_request: UpdateImageRequest):
    return ImageEventMessage(
        event=ImageUpdatedEvent(image_id=image_id, command=update_request.command)
    )
