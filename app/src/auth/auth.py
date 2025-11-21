from flask import Blueprint, request, session
from app.core.capcha_service import make_capcha, check_capcha, capcha_list, CapchaCheckResponse, requires_capcha
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core.jwt_service import hash_password
from app.core import models
from app.core import db
from app.core.jwt_service import create_access_token, decode_access_token

bp = Blueprint('blueprint', __name__, url_prefix="/api/v1/auth")
limiter = Limiter(
    get_remote_address,
    # app=bp,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


# @bp.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     capcha =
#     return {'message': 'Registration successful'}, 201

@bp.route('/auth', methods=['POST'])
@requires_capcha
def login():
    data = request.get_json()

    name = data.get("name", None)
    login = data.get("login", None)
    password = data.get("password", None)

    if not password or password == "":
        return {"message": "Password is null", "user_message": "Пустой пароль - слишком плохая идея.", "class": "text-red-400"}, 400

    sha256password = hash_password(password)

    conn = db.get_db()
    cur = conn.cursor()

    user_data = cur.execute(
        "SELECT id, login, password_hash FROM users WHERE login = ?", (login, )).fetchone()
    if not user_data:
        if not name:
            return {"message": "User not found", "user_message": "Пользователь с таким логином не найден! Попробуйте регистрацию!", "class": "text-amber-400"}, 404
        else:
            cur.execute("""INSERT INTO users
                    (name, login, password_hash) VALUES (?, ?, ?)
                    """,
                        (name, login, sha256password))
            conn.commit()
            uid = cur.execute(
                "SELECT DISTINCT id FROM users WHERE login = ?", (login, )).fetchone()[0]
            return {"token": create_access_token({"UID": uid}), "UID": uid}, 200
    else:
        if user_data[2] != sha256password:
            return {"message": "Wrong password", "user_message": "Неверный пароль!!!", "class": "text-red-500"}, 403
        else:
            return {"token": create_access_token({"UID": user_data[0]}), "UID": user_data[0]}, 200


@bp.route('/getcapcha', methods=['GET'])
@limiter.limit("2 per minute", error_message="Capcha request spam detected, try later.")
def getcapcha():
    UUID: str = make_capcha()
    session['capcha_uuid'] = UUID
    return {"UUID": UUID, "img": capcha_list[UUID].img}, 200

@bp.route("/fetchuser")
def fetchuser():
    UID = request.headers.get("UID")
    if not UID: return {"message": "No UID :(", "user_message": "А где UID?", "class": "text-red-500"}, 400