from flask import Blueprint, request, session
from app.core.capcha_service import make_capcha, check_capcha, capcha_list, CapchaCheckResponse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core.jwt_service import hash_password
from app.core import models
from app.core import db

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
def login():
    data = request.get_json()
    capcha = data.get("capcha", None)
    UUID = session.get('capcha_uuid', None)
    if not UUID:
        return {"message": "unknown capcha UUID"}, 400
    if not capcha:
        return {"message": "no capcha answer"}, 400
    resp = check_capcha(UUID, capcha)
    if resp == CapchaCheckResponse.CAPCHA_INVALID:
        return {"message": "Invalid capcha"}, 400
    if resp == CapchaCheckResponse.INCORRECT:
        return {"message": "Incorrect capcha answer", "user_message": "Неверный ответ капчи", "class": "text-red-400"}, 400

    name = data.get("name", None)
    login = request.headers.get("login", None)
    password = request.headers.get("password", None)

    if not password or password == "":
        return {"message": "Password is null", "user_message": "Пустой пароль - слишком плохая идея.", "class": "text-red-400"}, 400

    sha256password = hash_password(password)

    login_user = db.session.query(models.User).filter(
        models.User.login == login).first()
    if not login_user:
        if not name:
            return {"message": "User not found", "user_message": "Пользователь с таким логином не найден! Попробуйте регистрацию!", "class": "text-amber-400"}, 404
        else:
            # registration logic here
            pass
    if login_user.password_hash != sha256password:
        return {"message": "User not found", "user_message": "Неверный пароль!!!", "class": "text-red-500"}, 403

    # login logic here

    return {'message': 'Login successful'}, 201


@bp.route('/getcapcha', methods=['GET'])
@limiter.limit("2 per minute", error_message="Capcha request spam detected, try later.")
def getcapcha():
    UUID: str = make_capcha()
    session['capcha_uuid'] = UUID
    return {"UUID": UUID, "img": capcha_list[UUID].img}, 200
