from flask import Blueprint, request, session
from app.core.capcha_service import make_capcha, check_capcha, capcha_list, CapchaCheckResponse, requires_capcha
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core import db
from app.core.jwt_service import create_access_token, decode_access_token, requires_token
from app.core.returns import error
from app.core.db_wrappers import get_balance
from app.core.db_wrappers import write_transation, TransactionTypes
import datetime

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
    if val < 5:
        return error("Your value is less than your ...", uclass="text-red-500", umsg="Давай без микрододепов"), 400
    if hand < val:
        return error("invalid value - hand < val", uclass="text-red-400", umsg=f"Вам не хватает {val-hand} фантиков!"), 400

    hand -= val
    casino += val

    cur.execute("UPDATE users SET balance_hand = ?, balance_casino = ? WHERE id = ?",
                (hand, casino, uid))
    conn.commit()
    write_transation(uid, val, TransactionTypes.DEP)
    return {"hand": hand, "bank": bank, "casino": casino, "debt": debt}, 200


@bp.post("/bet/slots")
@requires_token
def bet_slots():
    uid = request.token_payload["UID"]
    data = request.get_json()
    val = data.get("value")
    try:
        val = float(val)
    except:
        return error("invalid value", uclass="text-red-400", umsg=f"Некорректное значение: {val}"), 400

    if val < 10:
        return error("invalid value", uclass="text-red-400", umsg=f"Ставка должна быть больше 10 фантиков"), 400

    conn, cur = db.get_cursor()
    # today = datetime.date.today()
    cur.execute("""SELECT COUNT(*) 
                FROM transactions
                WHERE type = 'BET'
                AND created_at >= strftime('%s', 'now', 'start of day')
                AND created_at <  strftime('%s', 'now', 'start of day', '+1 day')
                AND user_id = ?
                """,
            (uid, ))
    bet_count = cur.fetchone()[0]
    print(bet_count)
    return {}, 200
