from typing import Literal, Union

from pydantic import BaseModel, Field

# Idée à développer?
# DrawMode = Literal["override", "blend"]

# Array of [x, y, r, g, b]
# x, y: pixel coordinates
# r, g, b: image values (red, green, blue)
# FIXME: raises: "Invalid dtype! expected <class 'numpy.uint8'>, got int64" on deserialization
# ImageValues = NDArray[Shape["*, 5"], UInt8]  # type: ignore
ImageValues = list[list[int]]


class DrawCommand(BaseModel):
    command_type: Literal["draw"] = "draw"
    values: ImageValues


class ClearCanvasCommand(BaseModel):
    command_type: Literal["clear_canvas"] = "clear_canvas"


Command = Union[DrawCommand, ClearCanvasCommand]


class UpdateImageRequest(BaseModel):
    command: Command = Field(..., discriminator="command_type")
