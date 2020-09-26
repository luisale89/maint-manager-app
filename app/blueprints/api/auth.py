import uuid

from flask import Blueprint, url_for, jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token
)
from datetime import timedelta

from ...models import (
    db, User
)
from ...utils.helpers import APIException, normalize_names

auth = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@auth.route('/sign-up', methods=['POST'])
def sign_up():
    """
    * PUBLIC ENDPOINT *
    Crear un nuevo usuario para la aplicación.
    requerido: {
        "email": email,
        "password": psw,
        "fname": fname,
        "lname": lname
    }
    respuesta: {
        "success":"created", 201
    }
    """
    if not request.is_json:
        raise APIException("json request only")
    
    body = request.get_json()

    if body is None:
        raise APIException("not body in request")

    if 'email' not in body:
        raise APIException("email")

    if 'password' not in body:
        raise APIException("password")

    if 'fname' not in body:
        raise APIException("fname")
    fname = normalize_names(body['fname'])

    if 'lname' not in body:
        raise APIException("lname")
    lname = normalize_names(body['lname'])

    try:
        new_user = User(
            email=body['email'], 
            password=body['password'], 
            fname=fname,
            lname=lname, 
            public_id=str(uuid.uuid4())
        )
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIException("user already exists") # la columna email es unica,por eso este error significa solamente que el email ya existe

    return jsonify({'success': 'created'}), 201


@auth.route('/login', methods=['POST'])
def login():
    """
    PUBLIC ENDPOINT
    requerido: {
        "email": email,
        "password": password
    }
    respuesta: {
        "access_token": jwt_access_token,
        "token_expires: timedelta,
        "refresh_token": jwt_refresh_token,
        "user": {
            "id": id
            "fname": fname,
            "lname": lname,
            "user_picture": url_of_pic
        }
    }
    """
    if not request.is_json:
        raise APIException("not json request")

    body = request.get_json()

    if 'email' not in body:
        raise APIException("email")

    if 'password' not in body:
        raise APIException("password")

    user = User.query.filter_by(email=body['email']).first()
    if user is None:
        raise APIException("user not found", status_code=404)

    if not check_password_hash(user.password_hash, body['password']):
        raise APIException("wrong password", status_code=404)
    
    access_token = create_access_token(identity=user.public_id)

    return jsonify({"user": user.serialize_public(), "access_token": access_token})