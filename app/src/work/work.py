import math
from flask import Blueprint, request, session, jsonify
from app.core.capcha_service import make_capcha, check_capcha, capcha_list, CapchaCheckResponse, requires_capcha
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core import db
from app.core.jwt_service import create_access_token, decode_access_token, requires_token
from concurrent.futures import ThreadPoolExecutor
import random
import app.src.work.taskgen.pictures as picturegen
import io
import base64
import time
from typing import final
from app.core.db_wrappers import write_transaction, TransactionTypes

bp = Blueprint('work', __name__, url_prefix="/api/v1/work")
limiter = Limiter(
    key_func=lambda: request.headers.get('Token'),
    default_limits=["3 per minute"]
)

executor = ThreadPoolExecutor(max_workers=32)

# @bp.get("/task/sort/start")
# @requires_token


def start_sort_task():
    num_images = random.randint(8, 32)
    pattern_list = {i: random.choice(picturegen.patterns)
                    for i in range(num_images)}
    futures = []
    images = {}
    futures = [executor.submit(picturegen.generate_texture, 32,
                               True, pattern_list[p], None) for p in range(num_images)]
    results = [f.result() for f in futures]
    images = {i: results[i] for i in range(num_images)}
    base64_images = []
    for p_i in images:
        buffered = io.BytesIO()
        images[p_i].save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        base64_images.append(f"data:image/png;base64,{img_str}")
    return {"images": base64_images}


# UID: (time.time, amount, CPS) array of <= 5 latest
history = {}

AMOUNT_LIMITER: final = 145
PROFIT_MULTIPLIER: final = 0.25


@bp.post("/clicks")
@requires_token
# @limiter.limit("3 per minute")
def post_clicks():
    uid = request.token_payload["UID"]

    hist = history.get(uid)
    if hist is None:
        hist = [((time.time() - 10), 0, 0)]
    if time.time() - hist[-1][0] < 5:
        return 429

    data = request.get_json()
    amount = data.get("amount")
    if not amount:
        return {"message": "No amount:int in body"}, 400

    dt = time.time() - hist[-1][0]
    cps = amount/dt
    amount_limited = min(amount, AMOUNT_LIMITER)
    conn, cur = db.get_cursor()
    autoclicker_mlt = 1
    if amount_limited < amount:
        name = cur.execute(
            "SELECT name, login FROM users WHERE id = ?", (uid, )).fetchone()
        autoclicker_mlt = 0.8/(math.log2(amount-amount_limited)/2)
        
        print(f"{name[0]} (@{name[1]}) suspected in autoclicker: CPS={cps}, clicked {amount} and limited by {amount-amount_limited}. Profit multiplied with {autoclicker_mlt}")
    # print(hist)
    hist.append((time.time(), amount, cps))
    history[uid] = hist[:5]
    # print(history[uid])

    profit = amount_limited * PROFIT_MULTIPLIER * autoclicker_mlt
    cur.execute(
        "UPDATE users SET balance_hand = balance_hand + ? WHERE id = ?", (profit, uid))
    conn.commit()
    bal = cur.execute(
        "SELECT balance_hand FROM users WHERE id = ?", (uid, )).fetchone()
    write_transaction(uid, profit, TransactionTypes.WORK, description=(f"CPS {cps}" if amount < amount_limited else f"CPS {cps} REDUCED"))
    return {"balance_hand": bal[0], "limit": autoclicker_mlt}, 200


@bp.get("/multiplier")
def get_multiplier():
    return {"profit": PROFIT_MULTIPLIER}, 200
