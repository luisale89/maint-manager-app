from flask import Blueprint, url_for, jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from ...models import (
    db, User
)
from ...utils.helpers import APIException

profile = Blueprint('profile', __name__, url_prefix='/api/profile')

@profile.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@profile.route('/', methods=['GET'])
@jwt_required
def get_profile():
    """
    * PRIVATE ENDPOINT *
    Obtiene los datos de perfil de un usuario.
    requerido: {} # header of the request includes JWT wich is linked to the user email
    respuesta: {
        "user": {user_public, user_contact, user_log}, 200
    }
    """
    user = User.query.filter_by(email=get_jwt_identity()).first()
    data = {'user': dict(**user.serialize_public(), **user.serialize_contact(), **user.serialize_log())}
    return jsonify(data), 200