from typing import TYPE_CHECKING

from draw64.event import (
    ImageEventMessage,
    ImageCreatedEvent,
    ImageDeletedEvent,
    ImageUpdatedEvent,
)

# Import types only for type checkers, as to avoid some circular dependencies
if TYPE_CHECKING:
    from draw64.image import Image
    from draw64.image_id import ImageID
    from draw64.update_image_request import Command


def make_image_created_message(image: "Image"):
    return ImageEventMessage(event=ImageCreatedEvent(image_id=image.image_id))


def make_image_deleted_message(image: "Image"):
    return ImageEventMessage(event=ImageDeletedEvent(image_id=image.image_id))


def make_image_updated_message(image_id: "ImageID", command: "Command"):
    return ImageEventMessage(
        event=ImageUpdatedEvent(image_id=image_id, command=command)
    )
