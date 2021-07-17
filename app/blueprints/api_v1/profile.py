
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
    normalize_names, get_user, JSONResponse
)
from app.utils.validations import (
    check_validations,
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

    rsp = JSONResponse(message="user profile", payload={
        "user": user.serialize(), "identity": identity
    })
    return jsonify(rsp.serialize()), 200


@profile_bp.route('/update', methods=['PUT'])
@json_required({"fname":str, "lname":str, "home_address":dict, "profile_img":str, "personal_phone":str})
@jwt_required()
def update():
    identity = get_jwt_identity()
    user = get_user(identity)
    if user is None:
        raise APIException('user', status_code=404)

    body = request.get_json(silent=True)
    fname, lname, home_address, profile_img, personal_phone = \
    body['fname'], body['lname'], body['home_address'], body['profile_img'], body['personal_phone']
    
    check_validations({
        'fname': only_letters(fname, spaces=True, max_length=128),
        'lname': only_letters(lname, spaces=True, max_length=128)
    })

    if len(profile_img) > 255: #especial validation, find out if you needo to do more validations on urls
        raise APIException(message="profile img url is too long")
    
    user.fname = normalize_names(fname, spaces=True)
    user.lname = normalize_names(lname, spaces=True)
    user.home_address = home_address
    user.profile_img = profile_img
    user.personal_phone = personal_phone

    try:
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        raise APIException(e.orig.args[0], status_code=422) # integrityError or DataError info
    
    rsp = JSONResponse(message="user's profile updated", payload={"user": user.serialize()})
    return jsonify(rsp.serialize()), 200