from typing import Tuple, List, Dict, Union
from app.core.db import get_cursor


def get_balance(uid) -> Union[Tuple[float, float, float, float], None]:
    """Returns balance: hand, bank, casino, debt"""
    conn, cur = get_cursor()
    val = cur.execute(
        "SELECT balance_hand, balance_bank, balance_casino, debt FROM users WHERE id = ?", (uid, )).fetchone()
    if val:
        return tuple(val)
    return None
