from typing import Literal, Union

from pydantic import BaseModel, Field

from draw64.update_image_request import Command


class BaseImageEvent(BaseModel):
    image_id: str


class ImageCreatedEvent(BaseImageEvent):
    event_type: Literal["image_created"] = "image_created"


class ImageUpdatedEvent(BaseImageEvent):
    event_type: Literal["image_updated"] = "image_updated"
    command: Command = Field(..., discriminator="command_type")


class ImageDeletedEvent(BaseImageEvent):
    event_type: Literal["image_deleted"] = "image_deleted"


class UserConnectedEvent(BaseModel):
    event_type: Literal["user_connected"] = "user_connected"


class UserDisconnectedEvent(BaseModel):
    event_type: Literal["user_disconnected"] = "user_disconnected"


class UserCountUpdated(BaseModel):
    event_type: Literal["user_count_updated"] = "user_count_updated"
    user_count: int


Event = Union[
    ImageCreatedEvent,
    ImageDeletedEvent,
    ImageUpdatedEvent,
    UserConnectedEvent,
    UserCountUpdated,
    UserDisconnectedEvent,
]


class EventMessage(BaseModel):
    event: Event = Field(..., discriminator="event_type")
