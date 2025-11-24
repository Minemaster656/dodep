from flask import Blueprint, request, session
from app.core.capcha_service import make_capcha, check_capcha, capcha_list, CapchaCheckResponse, requires_capcha
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core import db
from app.core.jwt_service import create_access_token, decode_access_token, requires_token

bp = Blueprint('bank', __name__, url_prefix="/api/v1/bank")

@bp.get("/balance")
@requires_token
def get_balance():
    uid = request.token_payload["UID"]
    conn, cur = db.get_cursor()
    data = cur.execute("SELECT balance_hand, balance_bank, balance_casino, debt FROM users WHERE id = ?", (uid, )).fetchone()
    return {"hand": data[0], "bank": data[1], "casino": data[2], "debt": data[3]}