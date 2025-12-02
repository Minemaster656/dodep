from typing import Tuple, List, Dict, Union
from app.core.db import get_cursor
from enum import Enum


def get_balance(uid) -> Union[Tuple[float, float, float, float], None]:
    """Returns balance: hand, bank, casino, debt"""
    conn, cur = get_cursor()
    val = cur.execute(
        "SELECT balance_hand, balance_bank, balance_casino, debt FROM users WHERE id = ?", (uid, )).fetchone()
    if val:
        return tuple(val)
    return None


class TransactionTypes(Enum):
    WORK = "WORK"
    DODEP = "DODEP"
    DEP = "DEP"
    WIN = "WIN"
    GRANDWIN = "GWIN"


def write_transation(uid: int, amount: float, type: TransactionTypes, description: str = ""):
    cur.execute("INSERT ")
    conn, cur = get_cursor()
    cur.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                (uid, amount, type.value, description))
    conn.commit()