from flask import Blueprint, request

bp = Blueprint('blueprint', __name__, url_prefix="/api/v1/auth")

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