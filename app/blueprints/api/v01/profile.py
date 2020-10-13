
from flask import Blueprint, url_for, jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from app.extensions import db
from app.models import (
    User, Country
)
from app.utils.exceptions import APIException
from app.utils.helpers import (
    normalize_names, only_letters
)

profile = Blueprint('profile', __name__, url_prefix='/api/v1/profile')

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
    user = User.query.filter_by(public_id=get_jwt_identity()).first()
    if user is None:
        raise APIException("user not found", status_code=404)

    data = {'user': dict(**user.serialize(), **user.serialize_contact())}
    return jsonify(data), 200


@profile.route('/update', methods=['PUT'])
@jwt_required
def update_profile():
    user = User.query.filter_by(public_id=get_jwt_identity()).first()
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

    if 'user_picture' in body:
        user.profile_picture = body['user_picture']

    if 'user_phone' in body:
        user.phone = body['user_phone']

    if 'country' in body:
        if not isinstance(body['country'], int):
            raise APIException("Expected coutry id in request: %r" %body['country'])

        country_q = Country.query.get(body['country'])
        if country_q is None:
            raise APIException("Country id %r not found" % body['country'], status_code=404)
        user.country = country_q

    db.session.commit()
    
    data = {'user': dict(**user.serialize(), **user.serialize_contact())}
    return jsonify(data), 200