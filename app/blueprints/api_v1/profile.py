
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from app.extensions import db
from app.models.users import (
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
    respuesta: 
        "user": {
            "public_id": int,
            "fname": string,
            "lname": string,
            "profile_img": url,
            "home_address": dict,
            "personal_phone": string,
            "user_since": utc-datetime,
        }
    """
    user = User.query.filter_by(email=get_jwt_identity()).first() #get_jwt_indentity get the user id from jwt.
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
        if len(body['fname']) > 60:
            raise APIException("'fname' string must be 60 characters max")

        user.fname = normalize_names(body['fname'], spaces=True)

    if 'lname' in body:
        if not only_letters(body['lname'], spaces=True):
            raise APIException("Invalid 'lname' format in request: %r" %body['lname'])
        if len(body['lname']) > 60:
            raise APIException("'lname' string must be 60 characters max.")

        user.lname = normalize_names(body['lname'], spaces=True)

    if 'home_address' in body:
        if not type(body['home_address']) is dict:
            raise APIException("Invalid 'home_address' format in request: %r" %body['home_address'])

        user.home_address = body['home_address']

    if 'profile_img' in body:
        if not type(body['profile_img']) is str:
            raise APIException("Invalid 'profile_img' format in request: %r" %body['profile_img'])
        if len(body['profile_img']) > 120:
            raise APIException("'profile_img' string must be 120 characters max.")

        user.profile_img = body['profile_img']

    if 'personal_phone' in body:
        if not type(body['personal_phone']) is str:
            raise APIException("Invalid 'personal_phone' format in request: %r" %body['personal_phone']) 
        if len(body['personal_phone']) > 30:
            raise APIException("'personal_phone' string must be 30 characters max.")
       
        user.personal_phone = body['personal_phone']

    db.session.commit()
    
    data = {'user': user.serialize()}
    return jsonify(data), 200