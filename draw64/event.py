from typing import Literal, Union

from pydantic import BaseModel, Field

from draw64.image_id import ImageID
from draw64.update_image_request import Command


class BaseImageEvent(BaseModel):
    image_id: ImageID


class ImageCreatedEvent(BaseImageEvent):
    event_type: Literal["image_created"] = "image_created"


class ImageUpdatedEvent(BaseImageEvent):
    event_type: Literal["image_updated"] = "image_updated"
    command: Command = Field(..., discriminator="command_type")


class ImageDeletedEvent(BaseImageEvent):
    event_type: Literal["image_deleted"] = "image_deleted"


ImageEvent = Union[ImageCreatedEvent, ImageUpdatedEvent, ImageDeletedEvent]


class ImageEventMessage(BaseModel):
    event: ImageEvent = Field(..., discriminator="event_type")
