from flask import (
    Blueprint
)

from app.models.main import Role
from app.utils.redis_service import redis_client
from app.utils.exceptions import APIException
from app.utils.helpers import JSONResponse

status_bp = Blueprint('status_bp', __name__)

@status_bp.route('/', methods=['GET'])
def api_status_ckeck():

    try:
        Role.query.get(1)
    except Exception:
        raise APIException(message="main database service is down", app_status="error", status_code=500)

    try:
        r = redis_client()
        r.keys()

    except Exception:
        raise APIException(message="redis service is down", app_status="error", status_code=500)

    resp = JSONResponse("app online", app_status="success")
    return resp.to_json()