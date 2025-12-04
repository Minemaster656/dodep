import random
from typing import List, Union, Dict, Tuple

import colorama
# TODO: config.json

SYMBOLS = {
    "🍒": (10, 1.0),
    "🍊": (8, 1.05),
    "🍋": (4, 1.4),
    "🍇": (7, 1.075),
    "🍑": (4, 1.1),
    "🍓": (4, 1.2),
    "🍆": (3, 1.3),
    "✨": (1, 1.75)
}
WIN_VALUES = {
    0: 0,
    2: 2,
    3: 10
}


def get_fruit():
    keys = list(SYMBOLS.keys())
    weights = [SYMBOLS[key][0] for key in keys]
    return random.choices(keys, weights=weights, k=1)[0]


def roll(win: float = 0.2, gwin: float = 0.05) -> int:
    return random.choices([0, 2, 3], [1-gwin-win, win, gwin], k=1)[0]


def get_three_weighted_unique() -> Tuple[str, str, str]:
    keys = list(SYMBOLS.keys())
    weights = [SYMBOLS[k][0] for k in keys]

    chosen = []
    for _ in range(3):
        fruit = random.choices(keys, weights=weights, k=1)[0]
        idx = keys.index(fruit)
        chosen.append(fruit)
        # обнуляем вес, чтобы больше не выпадал
        weights[idx] = 0

    return chosen[0], chosen[1], chosen[2]


def get_result(roll_value: int) -> Tuple[float, str, str, str]:
    # 0 — три разных фрукта, тоже взвешенно, множитель 0
    if roll_value == 0:
        a, b, c = get_three_weighted_unique()
        return 0.0, a, b, c

    # 2 — два одинаковых, один другой, все взвешанно
    if roll_value == 2:
        fruit = get_fruit()
        others = [f for f in SYMBOLS.keys() if f != fruit]
        other_weights = [SYMBOLS[f][0] for f in others]
        other_fruit = random.choices(others, weights=other_weights, k=1)[0]

        slots = [fruit, fruit, other_fruit]
        random.shuffle(slots)

        multiplier = WIN_VALUES[2] * SYMBOLS[fruit][1]
        return multiplier, slots[0], slots[1], slots[2]

    # 3 — все три одинаковых, взвешанно
    if roll_value == 3:
        fruit = get_fruit()
        multiplier = WIN_VALUES[3] * SYMBOLS[fruit][1]
        return multiplier, fruit, fruit, fruit

    raise ValueError("roll_value must be 0, 2, or 3")


if __name__ == "__main__":
    o = []
    c = {0: colorama.Fore.RED, 2: colorama.Fore.YELLOW, 3: colorama.Fore.GREEN}
    for i in range(50):
        r = roll()
        res = get_result(r)
        o.append(f"{c[r]}Roll: {r}, Result: {res}{colorama.Style.RESET_ALL}")
    # o.sort()
    print("\n".join(o))
