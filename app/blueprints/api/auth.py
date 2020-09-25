from flask import Blueprint, url_for, jsonify, request, redirect
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from ...models import (
    db, User
)
from ...utils.helpers import APIException

auth = Blueprint('auth', __name__, url_prefix='/api')

@auth.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@auth.route('/sign-up', methods=['POST'])
def sign_up():
    """
    * PUBLIC ENDPOINT *
    Crear un nuevo usuario para la aplicación.
    requerido: {
        "email":"email@any.com",
        "password":"password",
        "fname": "first_name",
        "lname": "last_name"
    }
    respuesta: {
        "success":"new user created", 201
    }
    """
    if not request.is_json:
        raise APIException("api request only")

    email = request.json.get('email', None)
    password = request.json.get('password', None)
    fname = request.json.get('fname', None)
    lname = request.json.get('lname', None)

    if email is None:
        raise APIException("email required")

    if password is None:
        raise APIException("password required")

    if fname is None:
        raise APIException("fname required")
    fname = fname.replace(" ", "").capitalize()

    if lname is None:
        raise APIException("lname required")
    lname = lname.replace(" ", "").capitalize()

    try:
        new_user = User(email=email, password=password, fname=fname, lname=lname)
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIException("user already exists")

    return jsonify({'new user created': '201'}), 201


@auth.route('/login', methods=['POST'])
def login():
    """
    PUBLIC ENDPOINT
    envía datos de usuario para hacer login a la app.
    requerido: {
        "email": email,
        "password": password
    }
    respuesta: {
        "api_token": jwt_hash_token
    }
    """
    if not request.is_json:
        raise APIException("not json request")

    email = request.json.get('email', None)
    if email is None:
        raise APIException("email required")

    password = request.json.get('password', None)
    if password is None:
        raise APIException("password required")

    user = User.query.filter_by(email=email).first()
    if user is None:
        raise APIException("user not found", status_code=404)

    if not check_password_hash(user.password_hash, password):
        raise APIException("wrong password", status_code=404)

    return jsonify({"user": user.serialize_public()})