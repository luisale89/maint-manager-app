
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
#extensions
from app.extensions import db
from sqlalchemy.exc import (
    IntegrityError, DataError
)
#utils
from app.utils.exceptions import APIException
from app.utils.helpers import (
    normalize_names, get_user
)
from app.utils.validations import (
    only_letters
)
from app.utils.decorators import json_required

profile_bp = Blueprint('profile_bp', __name__)


@profile_bp.route('/', methods=['GET'])
@json_required()
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
        raise APIException("not_found", status_code=404)

    data = {'user': user.serialize(), 'identity': identity}
    return jsonify(data), 200


@profile_bp.route('/update', methods=['PUT'])
@json_required()
@jwt_required() #TODO modifie this endpoint to get all profile as required
def update():
    identity = get_jwt_identity()
    user = get_user(identity)
    if user is None:
        raise APIException('user', status_code=404)

    body = request.get_json(silent=True)
    if 'fname' in body:
        fname = str(body['fname'])
        only_letters(fname, spaces=True)
        if len(fname) > 60:
            raise APIException("to view")
        
        user.fname = normalize_names(fname, spaces=True)

    if 'lname' in body:
        lname = str(body['lname'])
        only_letters(lname, spaces=True)
        if len(lname) > 60:
            raise APIException("to_view")

        user.lname = normalize_names(lname, spaces=True)

    if 'home_address' in body:
        home_address = body['home_address']
        if not isinstance(home_address, dict):
            raise APIException("to view")

        user.home_address = body['home_address']

    if 'profile_img' in body:
        profile_img = str(body['profile_img'])
        if len(profile_img) > 120:
            raise APIException("to_view")

        user.profile_img = profile_img

    if 'personal_phone' in body:
        personal_phone = str(body['personal_phone'])
        if len(personal_phone) > 30:
            raise APIException("to_view")
       
        user.personal_phone = personal_phone

    try:
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        raise APIException(e.orig.args[0]) # integrityError or DataError info
    
    data = {'user': user.serialize()}
    return jsonify(data), 200