import random
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import base64
from io import BytesIO
from uuid import uuid4
from typing import List, Dict
from enum import Enum
from functools import wraps
from flask import request, session, Response

DICTIONARY = "ABCDEFGHJKLMNPQRSTUWXY12467890"
SIZE_MIN = 4
SIZE_MAX = 6

WIDTH, HEIGHT = 200, 80


class CaphaInstance:
    def __init__(self):
        self.answer = "".join(
            [random.choice(DICTIONARY)
             for _ in range(random.randint(SIZE_MIN, SIZE_MAX))]
        )
        self.deadline = time.time() + 120
        self.img = self.generate_captcha()

    def _load_font(self, size: int):
        # попробуй TTF, если есть; иначе дефолт
        try:
            # положи сюда свой шрифт, например DejaVuSans.ttf
            return ImageFont.truetype("DejaVuSans.ttf", size=size)
        except Exception:
            return ImageFont.load_default(size=size)

    def generate_captcha(self):
        # базовое изображение
        image = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        font = self._load_font(30)

        # размер текста
        text_width, text_height = draw.textbbox(
            (0, 0), self.answer, font=font)[2:]
        # паддинги
        pad_x, pad_y = 10, 5
        x = (WIDTH - text_width) / 2
        y = (HEIGHT - text_height) / 2

        # лёгкий фоновый шум точками
        for _ in range(300):
            px = random.randint(0, WIDTH - 1)
            py = random.randint(0, HEIGHT - 1)
            gray = random.randint(180, 230)

            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                        image.putpixel((nx, ny), (gray, gray, gray))

        # рисуем посимвольно, чуть двигая по вертикали и вращая
        for ch in self.answer:
            ch_w, ch_h = draw.textbbox((0, 0), ch, font=font)[2:]
            ch_img = Image.new("RGBA", (ch_w, ch_h), (0, 0, 0, 0))
            ch_draw = ImageDraw.Draw(ch_img)
            ch_draw.text((0, 0), ch, font=font, fill=(0, 0, 0, 255))

            # небольшой поворот символа
            angle = random.uniform(-20, 20)
            ch_img = ch_img.rotate(angle, resample=Image.BICUBIC, expand=1)

            # позиция с небольшим вертикальным рандомом
            yy = y + random.uniform(-5, 5)
            image.paste(ch_img, (int(x), int(yy)), ch_img)
            x += ch_w + random.uniform(0, 4)

        # полупрозрачные линии поверх текста
        line_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        line_draw = ImageDraw.Draw(line_overlay)
        for _ in range(16):
            x1 = random.randint(0, WIDTH)
            y1 = random.randint(0, HEIGHT)
            x2 = random.randint(0, WIDTH)
            y2 = random.randint(0, HEIGHT)
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(80, 160),  # прозрачность
            )
            line_draw.line((x1, y1, x2, y2), fill=color, width=2)

        image = Image.alpha_composite(image.convert("RGBA"), line_overlay)

        # лёгкое волновое искажение без чёрных углов
        image = self._wave_distort(image)

        # лёгкий blur, чтобы сгладить углы
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))

        # в base64
        buffered = BytesIO()
        image.convert("RGB").save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

    def _wave_distort(self, image: Image.Image) -> Image.Image:
        """Простая синус‑волна по X/Y без чёрного фона."""
        import math

        src = image
        dst = Image.new("RGBA", src.size, (255, 255, 255, 255))
        pixels_src = src.load()
        pixels_dst = dst.load()

        amp_x = 3  # амплитуда по X
        amp_y = 3  # амплитуда по Y
        freq_x = random.uniform(2.0, 3.5) / WIDTH
        freq_y = random.uniform(2.0, 3.5) / HEIGHT
        phase = random.uniform(0, 2 * math.pi)

        for y in range(HEIGHT):
            for x in range(WIDTH):
                # обратное отображение координат
                offset_x = int(
                    amp_x * math.sin(2 * math.pi * y * freq_x + phase))
                offset_y = int(
                    amp_y * math.sin(2 * math.pi * x * freq_y + phase))
                sx = x + offset_x
                sy = y + offset_y
                if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                    pixels_dst[x, y] = pixels_src[sx, sy]
                else:
                    # фон, чтобы не было чёрных краёв
                    pixels_dst[x, y] = (255, 255, 255, 255)

        return dst


capcha_list: Dict[str, CaphaInstance] = {}


def capcha_cleanup():
    for k in list(capcha_list.keys()):
        if time.time() > capcha_list[k].deadline:
            del capcha_list[k]


def make_capcha() -> str:
    capcha_cleanup()
    UUID = str(uuid4())
    capcha_list[UUID] = CaphaInstance()
    return UUID


class CapchaCheckResponse(Enum):
    CAPCHA_INVALID = -1
    INCORRECT = 0
    CORRECT = 1


def check_capcha(UUID: str, answer: str) -> bool:
    capcha_cleanup()
    instance = capcha_list.get(UUID, None)
    if not instance:
        return CapchaCheckResponse.CAPCHA_INVALID

    def preprocess_answer(ans: str) -> str:
        ans = ans.upper().replace("O", "0").replace("Z", "2").replace("I", "1")
        return ans
    if preprocess_answer(answer) == instance.answer:
        del capcha_list[UUID]
        return CapchaCheckResponse.CORRECT
    else:
        return CapchaCheckResponse.INCORRECT


def requires_capcha(endpoint):
    # def decorator(endpoint):
    @wraps(endpoint)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        capcha = data.get("capcha", None)
        UUID = session.get('capcha_uuid', None)
        if not UUID:
            return {"message": "unknown capcha UUID"}, 400
        if not capcha:
            return {"message": "no capcha answer"}, 400
        resp = check_capcha(UUID, capcha)
        if resp == CapchaCheckResponse.CAPCHA_INVALID:
            return {"message": "Invalid capcha"}, 400
        if resp == CapchaCheckResponse.INCORRECT:
            return {"message": "Incorrect capcha answer", "user_message": "Неверный ответ капчи", "class": "text-red-400"}, 400

        return endpoint(*args, **kwargs)
    return wrapper
    # return decorator
