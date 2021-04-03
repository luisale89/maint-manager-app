
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from app.extensions import db
from app.models.auth import (
    User
)
from app.utils.exceptions import APIException
from app.utils.helpers import (
    normalize_names, only_letters
)

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@profile_bp.route('/', methods=['GET'])
@jwt_required()
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
    if user is None:
        raise APIException("user not found", status_code=404)

    data = {'user': user.serialize()}
    return jsonify(data), 200


@profile_bp.route('/update', methods=['PUT'])
@jwt_required()
def update():
    user = User.query.filter_by(email=get_jwt_identity()).first()
    if user is None:
        raise APIException("user not found", status_code=404)

    if not request.is_json:
        raise APIException("JSON request only")

    body = request.get_json(silent=True)
    if body is None:
        raise APIException("not found body in request")

    if 'fname' in body:
        if not only_letters(body['fname'], spaces=True):
            raise APIException("Invalid 'fname' format in request: %r" %body['fname'])

        user.fname = normalize_names(body['fname'], spaces=True)

    if 'lname' in body:
        if not only_letters(body['lname'], spaces=True):
            raise APIException("Invalid 'lname' format in request: %r" %body['lname'])

        user.lname = normalize_names(body['lname'], spaces=True)

    if 'profile_img' in body:
        user.profile_img = body['profile_img']

    db.session.commit()
    
    data = {'user': user.serialize()}
    return jsonify(data), 200