from pydantic import BaseModel, Field

from typing import Literal, Union

DrawMode = Literal["override", "blend"]


class DrawCommand(BaseModel):
    command_type: Literal["draw"]
    draw_mode: DrawMode


class ClearCanvasCommand(BaseModel):
    command_type: Literal["clear_canvas"]


Command = Union[DrawCommand, ClearCanvasCommand]


class DrawRequest(BaseModel):
    command: Command = Field(..., discriminator="command_type")
