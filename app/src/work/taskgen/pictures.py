import math
import random
from typing import List, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont
from opensimplex import seed as opensimplex_seed, noise2
from perlin_noise import PerlinNoise

import time

Color = Tuple[int, int, int]


def _text_size(font: ImageFont.FreeTypeFont, text: str) -> tuple[int, int]:
    # Универсальная обёртка под Pillow 10+ через getbbox. [web:39][web:44]
    left, top, right, bottom = font.getbbox(text)
    return right - left, bottom - top


# --- Палитры: colorblind‑friendly / читаемые --- #
# Основу берёт из Okabe–Ito, слегка адаптируя под фоны. [web:23][web:27][web:31]
OKABE_ITO_COLORS: List[Color] = [
    (0, 0, 0),          # black
    (230, 159, 0),      # orange
    (86, 180, 233),     # sky blue
    (0, 158, 115),      # bluish green
    (240, 228, 66),     # yellow
    (0, 114, 178),      # blue
    (213, 94, 0),       # vermillion
    (204, 121, 167),    # reddish purple
]


def _lerp_color(a: Color, b: Color, t: float) -> Color:
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def _choose_palette(rng: random.Random, use_colors: bool):
    """
    Возвращает (bg, accents) — фон и список акцентных цветов. [web:23][web:25][web:30]
    """
    if not use_colors:
        # Чистая яркостная схема: безопасно для любых типов дальтонизма. [web:30]
        bg = (240, 240, 240)
        accents = [
            (60, 60, 60),
            (30, 30, 30),
            (200, 200, 200),
        ]
        return bg, accents

    # Набор заранее подобранных комбинаций, обеспечивающих приличный контраст. [web:23][web:25][web:34]
    palettes = [
        {
            "bg": (250, 250, 250),
            "accents": [
                (0, 114, 178),    # синий
                (213, 94, 0),     # тёплый контрастный
                (204, 121, 167),  # акцентный
            ],
        },
        {
            "bg": (245, 245, 245),
            "accents": [
                (86, 180, 233),   # небесный
                (0, 158, 115),    # зелёно-синий
                (0, 0, 0),        # чёткий тёмный
            ],
        },
        {
            "bg": (30, 30, 30),
            "accents": [
                (240, 228, 66),   # яркий жёлтый (но не чисто белый)
                (86, 180, 233),
                (230, 159, 0),
            ],
        },
    ]
    p = rng.choice(palettes)
    return p["bg"], p["accents"]


# --- Узоры --- #

def _pattern_straight_stripes(img: Image.Image, bg: Color, accents: List[Color], rng: random.Random):
    """
    Прямые диагональные полосы разной толщины с небольшими разрывами. [web:25][web:26]
    """
    w, h = img.size
    draw = ImageDraw.Draw(img)

    n_stripes = rng.randint(3, 8)
    angle = rng.uniform(math.radians(20), math.radians(70))
    dx = math.cos(angle)
    dy = math.sin(angle)
    length = math.hypot(w, h) * 2

    min_thick = max(2, w // 20)
    max_thick = max(min_thick + 1, w // 6)

    for i in range(n_stripes):
        offset = (i - n_stripes / 2) * \
            rng.uniform(min_thick * 1.2, max_thick * 1.5)
        nx, ny = -dy, dx
        cx = w / 2 + nx * offset
        cy = h / 2 + ny * offset

        x0 = cx - dx * length
        y0 = cy - dy * length
        x1 = cx + dx * length
        y1 = cy + dy * length

        thickness = rng.randint(min_thick, max_thick)
        color = accents[i % len(accents)]

        # Разбиваем линию на сегменты => «надрывы». [web:25][web:26]
        segments = rng.randint(3, 5)
        gap_factor = rng.uniform(0.1, 0.3)
        for s in range(segments):
            t0 = s / segments
            t1 = (s + (1.0 - gap_factor)) / segments
            sx0 = x0 + (x1 - x0) * t0
            sy0 = y0 + (y1 - y0) * t0
            sx1 = x0 + (x1 - x0) * t1
            sy1 = y0 + (y1 - y0) * t1
            draw.line((sx0, sy0, sx1, sy1), fill=color, width=thickness)


def _pattern_wavy_stripes(img: Image.Image, bg: Color, accents: List[Color], rng: random.Random):
    """
    Волнистые полосы‑синусоиды. [web:19]
    """
    w, h = img.size
    pixels = img.load()

    n_stripes = rng.randint(3, 5)
    base_width = w / (n_stripes * 1.5)
    amplitude = w * 0.12
    period = rng.uniform(w * 0.8, w * 1.4)

    for y in range(h):
        phase = rng.uniform(0, math.tau)
        offset = amplitude * math.sin((y / period) * math.tau + phase)
        for x in range(w):
            x_shifted = x + offset
            stripe_idx = int(x_shifted / base_width)
            if 0 <= stripe_idx < n_stripes:
                color = accents[stripe_idx % len(accents)]
                pixels[x, y] = color


def _pattern_dots(img: Image.Image, bg: Color, accents: List[Color], rng: random.Random):
    """
    Разбросанные круги разного размера, возможны пересечения. [web:25][web:26]
    """
    w, h = img.size
    draw = ImageDraw.Draw(img)

    n_dots = rng.randint(20, 60)
    for _ in range(n_dots):
        r = rng.uniform(w * 0.04, w * 0.18)
        cx = rng.uniform(-r, w + r)
        cy = rng.uniform(-r, h + r)
        color = rng.choice(accents)
        bbox = (cx - r, cy - r, cx + r, cy + r)
        draw.ellipse(bbox, fill=color)


def _pattern_nested_squares(img: Image.Image, bg: Color, accents: List[Color], rng: random.Random):
    """
    Вложенные квадраты. [web:25][web:26]
    """
    w, h = img.size
    draw = ImageDraw.Draw(img)
    n = rng.randint(3, 6)
    margin = w * 0.08
    for i in range(n):
        t = i / max(1, n - 1)
        inset = margin + t * (w / 2 - margin)
        color = accents[i % len(accents)]
        draw.rectangle(
            (inset, inset, w - inset, h - inset),
            outline=color,
            width=max(1, int(w * 0.02)),
        )


def _pattern_nested_circles(img: Image.Image, bg: Color, accents: List[Color], rng: random.Random):
    """
    Вложенные окружности. [web:25][web:26]
    """
    w, h = img.size
    draw = ImageDraw.Draw(img)
    n = rng.randint(3, 6)
    margin = w * 0.08
    for i in range(n):
        t = i / max(1, n - 1)
        inset = margin + t * (w / 2 - margin)
        color = accents[i % len(accents)]
        draw.ellipse(
            (inset, inset, w - inset, h - inset),
            outline=color,
            width=max(1, int(w * 0.02)),
        )


def _pattern_triangle_mosaic(img: Image.Image, bg: Color, accents: List[Color], rng: random.Random):
    """
    Мозаика из треугольников. [web:25][web:26]
    """
    w, h = img.size
    draw = ImageDraw.Draw(img)
    cell = max(4, w // 8)

    for y in range(0, h, cell):
        for x in range(0, w, cell):
            x1 = min(x + cell, w)
            y1 = min(y + cell, h)
            if rng.random() < 0.5:
                tri1 = [(x, y), (x1, y), (x1, y1)]
                tri2 = [(x, y), (x, y1), (x1, y1)]
            else:
                tri1 = [(x, y), (x1, y), (x, y1)]
                tri2 = [(x1, y), (x, y1), (x1, y1)]
            draw.polygon(tri1, fill=rng.choice(accents))
            draw.polygon(tri2, fill=rng.choice(accents))


def _pattern_perlin_noise(img: Image.Image, bg: Color, accents: List[Color], rng: random.Random):
    """
    Шум Перлина с 2 октавами; карта высот перекрашивается между bg и accent. [web:9][web:15][web:19]
    """
    w, h = img.size
    pixels = img.load()

    noise = PerlinNoise(octaves=2, seed=rng.randint(0, 10_000_000))
    accent = accents[0]

    scale = 8.0
    for y in range(h):
        for x in range(w):
            v = noise([x / scale, y / scale])
            t = (v + 1.0) * 0.5  # [-1,1] -> [0,1]
            t = max(0.0, min(1.0, t))
            pixels[x, y] = _lerp_color(bg, accent, t)


def _pattern_voronoi(img: Image.Image, bg: Color, accents: List[Color], rng: random.Random):
    """
    Простой Voronoi‑шум по ближайшим точкам. [web:18]
    """
    w, h = img.size
    pixels = img.load()

    n_sites = rng.randint(8, 16)
    sites = []
    for _ in range(n_sites):
        sx = rng.uniform(0, w)
        sy = rng.uniform(0, h)
        color = rng.choice(accents)
        sites.append((sx, sy, color))

    for y in range(h):
        for x in range(w):
            best_d2 = float("inf")
            best_color = bg
            for sx, sy, color in sites:
                dx = x - sx
                dy = y - sy
                d2 = dx * dx + dy * dy
                if d2 < best_d2:
                    best_d2 = d2
                    best_color = color
            pixels[x, y] = best_color


def _pattern_none(img: Image.Image, bg: Color, accents: List[Color], rng: random.Random):
    """
    Отсутствие узора: просто фон, и дальше только искажения. [web:30]
    """
    pass


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def _get_font(rng: random.Random, size: int) -> ImageFont.FreeTypeFont:
    """
    Пытается взять системный моноширинный шрифт, иначе падает на встроенный. [web:4]
    """
    try:
        # Часто есть в Linux‑системах. [web:4]
        return ImageFont.truetype("DejaVuSansMono.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _pattern_random_chars(img: Image.Image, bg: Color, accents: List[Color], rng: random.Random):
    """
    Случайные буквы/цифры разных размеров, позиций и поворотов. [web:25][web:26]
    """
    w, h = img.size
    base_layer = img
    draw = ImageDraw.Draw(base_layer)

    n_chars = rng.randint(6, 12)
    for _ in range(n_chars):
        ch = rng.choice(ALPHABET)
        font_size = rng.randint(w // 4, w // 2)
        font = _get_font(rng, font_size)
        color = rng.choice(accents)

        # tw, th = font.getsize(ch)   # БЫЛО — ломается в Pillow ≥10. [web:39][web:43]
        # СТАЛО — кросс‑версионно. [web:41][web:44]
        tw, th = _text_size(font, ch)

        char_img = Image.new("RGBA", (tw * 2, th * 2), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(char_img)
        cdraw.text((tw / 2, th / 2), ch, font=font, fill=color)

        angle = rng.uniform(-40, 40)
        char_img = char_img.rotate(
            angle,
            resample=Image.Resampling.BILINEAR,
            expand=True,
        )

        cx = rng.randint(-w // 4, w)
        cy = rng.randint(-h // 4, h)
        base_layer.paste(char_img, (cx, cy), char_img)


# --- Искажения --- #

def _apply_opensimplex_warp(img: Image.Image, rng: random.Random,
                            amount: float = 1.5, scale: float = 24.0) -> Image.Image:
    """
    Лёгкое геометрическое искажение на OpenSimplex без чёрных углов. [web:10][web:20]
    """
    w, h = img.size
    src = img
    src_px = src.load()
    dst = Image.new("RGB", (w, h))
    dst_px = dst.load()

    opensimplex_seed(rng.randint(0, 10_000_000))

    for y in range(h):
        for x in range(w):
            nx = x / scale
            ny = y / scale
            dx = noise2(nx, ny) * amount
            dy = noise2(nx + 100.0, ny + 100.0) * amount
            sx = int(max(0, min(w - 1, x + dx)))
            sy = int(max(0, min(h - 1, y + dy)))
            dst_px[x, y] = src_px[sx, sy]

    return dst


def _apply_perlin_intensity_noise(img: Image.Image, rng: random.Random,
                                  amount: float = 12.0, octaves: int = 1) -> Image.Image:
    """
    Лёгкий Perlin‑шум по яркости, 1–2 октавы. [web:9][web:15][web:19]
    """
    w, h = img.size
    pixels = img.load()
    noise = PerlinNoise(octaves=octaves, seed=rng.randint(0, 10_000_000))
    scale = 10.0

    for y in range(h):
        for x in range(w):
            v = noise([x / scale, y / scale])  # [-1, 1]
            delta = int(v * amount)
            r, g, b = pixels[x, y]
            r = max(0, min(255, r + delta))
            g = max(0, min(255, g + delta))
            b = max(0, min(255, b + delta))
            pixels[x, y] = (r, g, b)

    return img


def _apply_white_noise(img: Image.Image, rng: random.Random, amount: int = 10) -> Image.Image:
    """
    Лёгкий белый шум по каналам, добавляемый поверх (как полупрозрачный слой). [web:30]
    """
    w, h = img.size
    pixels = img.load()

    for y in range(h):
        for x in range(w):
            n = rng.randint(-amount, amount)
            r, g, b = pixels[x, y]
            r = max(0, min(255, r + n))
            g = max(0, min(255, g + n))
            b = max(0, min(255, b + n))
            pixels[x, y] = (r, g, b)

    return img


# --- Основной генератор --- #

def generate_texture(
    size: int = 64,
    use_colors: bool = True,
    pattern: Optional[str] = None,
    seed: Optional[int] = None,
) -> Image.Image:
    """
    Генерирует квадратную текстуру с узором и искажениями и возвращает PIL.Image.Image. [web:4][web:10]
    """
    rng = random.Random(seed)

    bg, accents = _choose_palette(rng, use_colors)

    img = Image.new("RGB", (size, size), bg)

    patterns = {
        "straight_stripes": _pattern_straight_stripes,
        "wavy_stripes": _pattern_wavy_stripes,
        "dots": _pattern_dots,
        "nested_squares": _pattern_nested_squares,
        "nested_circles": _pattern_nested_circles,
        "triangle_mosaic": _pattern_triangle_mosaic,
        "perlin": _pattern_perlin_noise,
        "voronoi": _pattern_voronoi,
        "none": _pattern_none,
        "chars": _pattern_random_chars,
    }

    if pattern is None:
        pattern = rng.choice(list(patterns.keys()))

    if pattern not in patterns:
        raise ValueError(f"Unknown pattern: {pattern}")

    # Рисуем базовый узор. [web:25][web:26]
    patterns[pattern](img, bg, accents, rng)

    # Лёгкое геометрическое искажение + перлин по яркости + белый шум. [web:10][web:15][web:19][web:30]
    img = _apply_opensimplex_warp(img, rng, amount=1.3, scale=24.0)
    img = _apply_perlin_intensity_noise(img, rng, amount=8.0, octaves=1)
    img = _apply_white_noise(img, rng, amount=6)

    return img


patterns = [
    "straight_stripes",
    "wavy_stripes",
    "dots",
    "nested_squares",
    "nested_circles",
    "triangle_mosaic",
    "perlin",
    "voronoi",
    "none",
    "chars",
]

# пример батча
# images = [generate_texture(size=64, use_colors=True) for _ in range(16)]

# Concatenate images into a 4x4 atlas and save as file


def create_atlas(images: List[Image.Image], output_path: str = "atlas.png") -> None:
    if len(images) != 16:
        raise ValueError("Exactly 16 images are required for a 4x4 atlas")

    size = images[0].size
    atlas_width = size[0] * 4
    atlas_height = size[1] * 4
    atlas = Image.new("RGB", (atlas_width, atlas_height))

    for i, img in enumerate(images):
        row = i // 4
        col = i % 4
        x = col * size[0]
        y = row * size[1]
        atlas.paste(img, (x, y))

    atlas.save(output_path)

# Example usage
# create_atlas(images)
# speeds = ""
# for p in patterns:
#     start = time.time()
#     images = [generate_texture(size=64, use_colors=True, pattern=p) for _ in range(16)]
#     create_atlas(images, output_path=p+".png")
#     end = time.time()
#     speeds+=p + ": "
#     speeds+=str(end-start) + "s\n"
# with open("speeds.txt", mode="w") as f:
#     f.writelines(speeds)
