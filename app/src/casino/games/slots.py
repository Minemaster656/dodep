import random
from typing import List, Union, Dict, Tuple
from time import time
import colorama
# TODO: config.json

SYMBOLS = {
    "🍒": (10, 1.0),
    "🍊": (8, 1.05),
    "🍋": (4, 1.4),
    "🍇": (7, 1.075),
    "🍑": (4, 1.1),
    "🍓": (4, 1.2),
    "🍆": (3, 1.5),
    "✨": (1, 2.1),
    "💩": (0.5, -0.5)
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

        # Если где-то есть 💩, меняем её на другой случайный символ
        def reroll_if_poop(x: str) -> str:
            if x != "💩":
                return x
            # берём любые символы, кроме 💩
            others = [k for k in SYMBOLS.keys() if k != "💩"]
            weights = [SYMBOLS[k][0] for k in others]
            return random.choices(others, weights=weights, k=1)[0]

        a = reroll_if_poop(a)
        b = reroll_if_poop(b)
        c = reroll_if_poop(c)

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


def adjusted_roll(rolls_count_today: int, win_adjust: float = 0) -> int:
    if rolls_count_today < 5:
        return roll(win=0.4+win_adjust, gwin=0.025)
    if rolls_count_today < 10:
        return roll(win=0.4+win_adjust, gwin=0.2)
    if rolls_count_today < 20:
        roll(win=0.4+win_adjust, gwin=0.015)
    if rolls_count_today < 100:
        roll(win=0.35+win_adjust, gwin=0.015)
    return roll(win=0.3+win_adjust, gwin=0.015)


if __name__ == "__main__":
    o = []
    c = {0: colorama.Fore.RED, 2: colorama.Fore.YELLOW, 3: colorama.Fore.GREEN}
    # for i in range(50):
    total_win = 0
    i = 0
    l = time()
    while ...:
        i += 1
        r = roll(win=0.35, gwin=0.015)
        res = get_result(r)
        total_win += res[0]
        if i % 1000 == 0:  # and time()-l > 0.5:
            l = time()
            print(
                f"{c[r]}Roll: {r}, Result: {res}{colorama.Style.RESET_ALL} | Avg {total_win/i} i: {i}")
    # o.sort()
    # print("\n".join(o))
