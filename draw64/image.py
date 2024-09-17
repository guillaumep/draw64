from io import BytesIO

import numpy as np

from numpydantic import NDArray, Shape
from numpydantic.dtype import UInt8
from PIL import Image as PILImage
from pydantic import BaseModel, Field

from draw64.event_factory import make_image_updated_message
from draw64.pubsub import pubsub
from draw64.update_image_request import (
    ClearCanvasCommand,
    Command,
    DrawCommand,
    ImageValues,
)


ImageData = NDArray[Shape["64, 64, 3"], UInt8]  # type: ignore


def create_image_data():
    # Create a white image of dimension 64x64
    return np.full((64, 64, 3), 255, np.uint8)


class Image(BaseModel):
    image_id: str
    data: ImageData = Field(default_factory=create_image_data, exclude=True)

    def update(self, command: Command):
        if isinstance(command, ClearCanvasCommand):
            self.clear()
        elif isinstance(command, DrawCommand):
            self.update_values(command.values)

        pubsub.broadcast(
            self.image_id, make_image_updated_message(self.image_id, command)
        )

    def update_values(self, values_array: ImageValues):
        for values in values_array:
            x = values[0]
            y = values[1]
            if x >= 0 and x < 64 and y >= 0 and y < 64:
                self.data[x][y] = values[2:5]

    def clear(self):
        self.data.fill(255)

    def to_png(self) -> bytes:
        bytesio = BytesIO()
        PILImage.fromarray(np.swapaxes(self.data, 0, 1), "RGB").save(
            bytesio, format="PNG"
        )
        return bytesio.getvalue()
