from flask import Blueprint, request, session, render_template
from app.core.capcha_service import make_capcha, check_capcha, capcha_list, CapchaCheckResponse, requires_capcha
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core import db
from app.core.jwt_service import create_access_token, decode_access_token, requires_token

bp = Blueprint('other', __name__, url_prefix="/api/v1/other")
bp_nopref = Blueprint('other_nopref', __name__, url_prefix="/")

@bp_nopref.get("/profile/id/<uid>")
def profile_uid(uid):
    conn, cur = db.get_cursor()
    uname = cur.execute("SELECT name FROM users WHERE id = ?", (uid, )).fetchone()
    if uname:
        return render_template("pages/profile.html", name=uname[0], uid=uid)
    else:
        return render_template("pages/404.html", message=f"Пользователь #{uid} не найден :(")

@bp_nopref.get("/profile/<tag>")
def profile(tag):
    conn, cur = db.get_cursor()
    uname = cur.execute("SELECT name, id FROM users WHERE login = ?", (tag, )).fetchone()
    if uname:
        return render_template("pages/profile.html", name=uname[0], uid=uname[1])
    else:
        return render_template("pages/404.html", message=f"Пользователь @{tag} не найден :(")