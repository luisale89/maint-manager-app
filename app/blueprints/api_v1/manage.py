from flask import (
    Blueprint
)

from app.models.main import Role, Plan
from app.utils.exceptions import APIException
from app.utils.helpers import JSONResponse
from app.utils.decorators import (json_required, super_user_required)

manage_bp = Blueprint('manage_bp', __name__)


@manage_bp.route('/set-globals', methods=['GET']) #!debug
@json_required()
@super_user_required()
def set_app_globals():

    Role.add_default_roles()
    Plan.add_default_plans()

    resp = JSONResponse("defaults added")
    return resp.to_json()