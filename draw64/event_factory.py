from typing import TYPE_CHECKING

from draw64.event import (
    EventMessage,
    ImageCreatedEvent,
    ImageDeletedEvent,
    ImageUpdatedEvent,
    UserConnectedEvent,
    UserCountUpdated,
    UserDisconnectedEvent,
)

# Import types only for type checkers, as to avoid some circular dependencies
if TYPE_CHECKING:
    from draw64.image import Image
    from draw64.image_id import ImageID
    from draw64.update_image_request import Command


def make_image_created_message(image: "Image"):
    return EventMessage(event=ImageCreatedEvent(image_id=image.image_id))


def make_image_deleted_message(image: "Image"):
    return EventMessage(event=ImageDeletedEvent(image_id=image.image_id))


def make_image_updated_message(image_id: "ImageID", command: "Command"):
    return EventMessage(event=ImageUpdatedEvent(image_id=image_id, command=command))


def make_user_connected_message():
    return EventMessage(event=UserConnectedEvent())


def make_user_disconnected_message():
    return EventMessage(event=UserDisconnectedEvent())


def make_user_count_updated_message(user_count: int):
    return EventMessage(event=UserCountUpdated(user_count=user_count))
