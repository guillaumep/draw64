from io import BytesIO

import numpy as np

from nanoid import generate
from numpydantic import NDArray, Shape
from numpydantic.dtype import UInt8
from PIL import Image as PILImage
from pydantic import BaseModel, Field

from draw64.update_image_request import Command, DrawCommand, ClearCanvasCommand

alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

ImageData = NDArray[Shape["64, 64, 3"], UInt8]  # type: ignore


def create_image_id():
    return generate(alphabet=alphabet, size=22)


def create_image_data():
    return np.zeros((64, 64, 3), np.uint8)


class Image(BaseModel):
    image_id: str = Field(default_factory=create_image_id)
    data: ImageData = Field(default_factory=create_image_data, exclude=True)

    def update(self, command: Command):
        if isinstance(command, ClearCanvasCommand):
            self.clear()
        elif isinstance(command, DrawCommand):
            pass

    def clear(self):
        self.data.fill(255)

    def to_png(self) -> bytes:
        bytesio = BytesIO()
        PILImage.fromarray(self.data, "RGB").save(bytesio, format="PNG")
        return bytesio.getvalue()
