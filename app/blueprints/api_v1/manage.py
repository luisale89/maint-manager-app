from flask import (
    Blueprint
)

from app.models.main import Role, Plan
from app.utils.exceptions import APIException
from app.utils.helpers import JSONResponse
from app.utils.decorators import (json_required, user_required)
from flask_jwt_extended import get_jwt_identity

manage_bp = Blueprint('manage_bp', __name__)


@manage_bp.route('/set-globals', methods=['GET']) #!debug
@json_required()
@user_required()
def set_app_globals():

    user = get_jwt_identity()
    if user != 'luis.lucena89@gmail.com': #* super usuario de la app, se debe ajustar variable de entorno

        raise APIException(message="unautorized user", status_code=401)

    Role.add_default_roles()
    Plan.add_default_plans()

    resp = JSONResponse("defaults added")
    return resp.to_json()
