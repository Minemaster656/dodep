from flask import Blueprint, request, session
from app.core.capcha_service import make_capcha, check_capcha, capcha_list, CapchaCheckResponse, requires_capcha
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core import db
from app.core.jwt_service import create_access_token, decode_access_token, requires_token
from app.core.returns import error
from app.core.db_wrappers import get_balance


bp = Blueprint('casino', __name__, url_prefix="/api/v1/casino")


@bp.post("/dep")
@requires_token
def deposit():
    data = request.get_json()
    val = data.get("value")
    try:
        val = float(val)
    except:
        return error("invalid value", uclass="text-red-400", umsg=f"Некорректное значение: {val}"), 400

    conn, cur = db.get_cursor()
    uid = request.token_payload["UID"]
    hand, bank, casino, debt = get_balance(uid)

    if hand < val:
        return error("invalid value - hand < val", uclass="text-red-400", umsg=f"Вам не хватает {val-hand} фантиков!"), 400

    hand -= val
    casino += val

    cur.execute("UPDATE users SET balance_hand = ?, balance_casino = ? WHERE id = ?",
                (hand, casino, uid))
    conn.commit()
    return {"hand": hand, "bank": bank, "casino": casino, "debt": debt}, 200
