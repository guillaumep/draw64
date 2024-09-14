from draw64.image import Image


class ImageIDAlreadyExistsException(Exception):
    pass


class ImageCollection:
    def __init__(self):
        self._images: dict[str, Image] = {}

    def __len__(self):
        return len(self._images)

    def __iter__(self):
        return iter(self._images)

    def __contains__(self, image_id: str):
        return image_id in self._images

    def __getitem__(self, image_id: str):
        return self._images[image_id]

    def create_image(self, image_id: str | None = None):
        if image_id and image_id in self:
            raise ImageIDAlreadyExistsException(image_id)
        image = Image(image_id)
        self._images[image.id] = image
        return image.id

    def delete_image(self, image_id: str):
        if image_id in self._images:
            del self._images[image_id]
