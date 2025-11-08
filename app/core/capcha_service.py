import random
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import base64
from io import BytesIO
from uuid import uuid4
from typing import List, Dict
from enum import Enum

DICTIONARY = "ABCDEFGHJKLMNPQRSTUWXYZ12467890"
SIZE_MIN = 4
SIZE_MAX = 6
class CaphaInstance:
    def __init__(self):
        self.answer = "".join([random.choice(DICTIONARY) for i in range(random.randint(SIZE_MIN, SIZE_MAX))])
        self.deadline = time.time() + 120
        self.img = self.generate_captcha()
        
    def generate_captcha(self):

        # Create image
        width, height = 200, 80
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # Add noise
        for _ in range(1000):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

        # Add text with distortion
        font = ImageFont.load_default()
        text_width, text_height = draw.textsize(self.answer, font=font)
        x = (width - text_width) / 2
        y = (height - text_height) / 2

        for char in self.answer:
            char_width, char_height = draw.textsize(char, font=font)
            draw.text((x, y + random.uniform(-5, 5)), char, font=font, fill=(0, 0, 0))
            x += char_width + random.uniform(-2, 2)

        # Apply distortion
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        image = image.transform(image.size, Image.AFFINE, (1, 0.1, 0, 0.1, 1, 0))

        # Add more noise
        for _ in range(50):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line((x1, y1, x2, y2), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=1)

        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return f'data:image/png;base64,{img_str}'

capcha_list: Dict[str, CaphaInstance] = {}
def capcha_cleanup():
    for k in capcha_list:
        if time.time() > capcha_list[k].deadline:
            del capcha_list[k]
def make_capcha()->str:
    capcha_cleanup()
    UUID = str(uuid4())
    capcha_list[UUID] = CaphaInstance()
    return UUID

class CapchaCheckResponse(Enum):
    CAPCHA_INVALID = -1
    INCORRECT = 0
    CORRECT = 1
def check_capcha(UUID: str, answer: str)->bool:
    capcha_cleanup()
    instance = capcha_list.get(UUID, None)
    if not instance:
        return CapchaCheckResponse.CAPCHA_INVALID
    if answer == instance.answer:
        del capcha_list[UUID]
        return CapchaCheckResponse.CORRECT
    else:
        return CapchaCheckResponse.INCORRECT