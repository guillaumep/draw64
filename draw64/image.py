from nanoid import generate

from draw64.models import Command, DrawCommand, ClearCanvasCommand

alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Image:
    def __init__(self, image_id: str | None = None):
        self._id = image_id or generate(alphabet=alphabet, size=22)
        self.clear()

    @property
    def id(self):
        return self._id

    def _create_empty_image(self):
        return [[0] * 64] * 64

    def update(self, command: Command):
        if isinstance(command, ClearCanvasCommand):
            self.clear()
        elif isinstance(command, DrawCommand):
            pass

    def clear(self):
        self._data = self._create_empty_image()
