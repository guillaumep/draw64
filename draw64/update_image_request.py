from pydantic import BaseModel, Field

from typing import Literal, Union

# Idée à développer?
# DrawMode = Literal["override", "blend"]


class DrawCommand(BaseModel):
    command_type: Literal["draw"]


class ClearCanvasCommand(BaseModel):
    command_type: Literal["clear_canvas"]


Command = Union[DrawCommand, ClearCanvasCommand]


class UpdateImageRequest(BaseModel):
    command: Command = Field(..., discriminator="command_type")
