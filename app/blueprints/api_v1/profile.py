
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt
)

from app.extensions import db
from sqlalchemy.exc import (
    IntegrityError, DataError
)
from app.utils.exceptions import APIException
from app.utils.helpers import (
    normalize_names, api_responses, get_user
)
from app.utils.validations import (
    only_letters
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
    identity = get_jwt_identity()
    user = get_user(identity) #get_jwt_indentity get the user id from jwt.
    if user is None:
        raise APIException(api_responses.not_found('user'), status_code=404)

    data = {'user': user.serialize(), 'w_relation': get_jwt()['w_relation'], 'identity': get_jwt()['sub']}
    return jsonify(data), 200


@profile_bp.route('/update', methods=['PUT'])
@jwt_required()
def update():
    identity = get_jwt_identity()
    user = get_user(identity)
    if user is None:
        raise APIException(api_responses.not_found('user'), status_code=404)

    if not request.is_json:
        raise APIException(api_responses.not_json_rq())

    body = request.get_json(silent=True)
    if body is None:
        raise APIException(api_responses.not_json_rq())

    if 'fname' in body:
        fname = str(body['fname'])
        only_letters(fname, spaces=True)
        if len(fname) > 60:
            raise APIException(api_responses.invalid_format('fname', '> 60 char string'))
        
        user.fname = normalize_names(fname, spaces=True)

    if 'lname' in body:
        lname = str(body['lname'])
        only_letters(lname, spaces=True)
        if len(lname) > 60:
            raise APIException(api_responses.invalid_format('lname', '> 60 char string'))

        user.lname = normalize_names(lname, spaces=True)

    if 'home_address' in body:
        home_address = body['home_address']
        if not isinstance(home_address, dict):
            raise APIException(api_responses.invalid_format('home_address', type(home_address).__name__, 'JSON'))

        user.home_address = body['home_address']

    if 'profile_img' in body:
        profile_img = str(body['profile_img'])
        if len(profile_img) > 120:
            raise APIException(api_responses.invalid_format('profile_img','> 120 char string'))

        user.profile_img = profile_img

    if 'personal_phone' in body:
        personal_phone = str(body['personal_phone'])
        if len(personal_phone) > 30:
            raise APIException(api_responses.invalid_format('profile_img', '> 30 char string'))
       
        user.personal_phone = personal_phone

    try:
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        raise APIException(e.orig.args[0]) # integrityError or DataError info
    
    data = {'user': user.serialize()}
    return jsonify(data), 200