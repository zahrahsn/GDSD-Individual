import io
from PIL import Image
from sightengine.client import SightengineClient


class ImageValidator:
    def __init__(self, image):
        self.image = image

    def check(self, photo):
        client = SightengineClient('265804968', 'kqyZakkeqA6GPRQEqXzE')
        output = client.check('wad').set_file(photo)
        weapon = output['weapon']
        alcohol = output['alcohol']
        drugs = output['drugs']
        if weapon > 0.1:
            return "Weapon"
        if alcohol > 0.1:
            return "Alcohol"
        if drugs > 0.1:
            return "Drugs"
        return None

    def resize(self, max_height=300):
        img = Image.open(self.image)
        width, height = img.size
        resize_ratio = height / max_height
        new_height = int(height // resize_ratio)
        new_width = int(width // resize_ratio)
        resized = img.resize((new_width, new_height), Image.ANTIALIAS)
        if new_width > max_height:
            width_side_crop = int((new_width - max_height) // 2)
            resized = resized.crop((width_side_crop, 0, new_width - width_side_crop, new_height))
        imgByteArr = io.BytesIO()
        format = str(self.image.name.split(".")[-1]).upper()
        if format == 'JPG':
            format = 'JPEG'
        resized.save(imgByteArr, format=format)
        return imgByteArr.getvalue()
