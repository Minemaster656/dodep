from flask import Blueprint, request, session
from app.core.capcha_service import make_capcha, check_capcha, capcha_list, CapchaCheckResponse, requires_capcha
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core import db
from app.core.jwt_service import create_access_token, decode_access_token, requires_token

bp = Blueprint('casino', __name__, url_prefix="/api/v1/casino")
