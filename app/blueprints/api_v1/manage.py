from flask import (
    Blueprint
)

from app.models.main import Role, Plan
from app.utils.exceptions import APIException
from app.utils.helpers import JSONResponse

manage_bp = Blueprint('manage_bp', __name__)


@manage_bp.route('/set-globals', methods=['GET']) #!debug
def set_app_globals():
    Role.add_default_roles()
    Plan.add_default_plans()

    resp = JSONResponse("defaults added")
    return resp.to_json()