from flask import Blueprint, request, session
from app.core.capcha_service import make_capcha, check_capcha
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

bp = Blueprint('blueprint', __name__, url_prefix="/api/v1/auth")
limiter = Limiter(
    get_remote_address,
    app=bp,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # Handle registration logic here
    return {'message': 'Registration successful'}, 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # Handle registration logic here
    return {'message': 'Login successful'}, 201

@bp.route('/getcapcha', methods=['GET'])
@limiter.limit("2 per minute", error_message="Capcha request spam detected, try later.")
def getcapcha():
    UUID: str = make_capcha()
    session['capcha_uuid'] = UUID
