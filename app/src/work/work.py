from flask import Blueprint, request, session
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
bp = Blueprint('work', __name__, url_prefix="/api/v1/work")
executor = ThreadPoolExecutor(max_workers=32)

@bp.get("/task/sort/start")
# @requires_token
def start_sort_task():
    num_images = random.randint(8, 32)
    pattern_list = {i: random.choice(picturegen.patterns) for i in range(num_images)}
    futures = []
    images = {}
    futures = [executor.submit(picturegen.generate_texture, 32, True, pattern_list[p], None) for p in range(num_images)]
    results = [f.result() for f in futures]
    images = {i: results[i] for i in range(num_images)}
    base64_images = []
    for p_i in images:
        buffered = io.BytesIO()
        images[p_i].save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        base64_images.append(f"data:image/png;base64,{img_str}")
    return {"images": base64_images}