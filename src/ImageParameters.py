import json


class ImageParameters:
    def __init__(self):
        self.images = []

    def add(self, image_type_id, image):
        image = {
            "image_type_id": image_type_id,
            "image": image,
        }
        self.images.append(image)

    def get_params(self):
        return self.images
