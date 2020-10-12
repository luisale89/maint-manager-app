import uuid, re

from flask import Blueprint, url_for, jsonify, request, current_app
from sqlalchemy.exc import (
    IntegrityError
)
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, decode_token
)
from ...models import (
    User, TokenBlacklist
)
from ...extensions import jwt, db
from ...utils.exceptions import APIException
from ...utils.helpers import (
    normalize_names, add_token_to_database, 
    prune_database, valid_email, valid_password, only_letters 
)

auth = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    jti = decoded_token['jti']
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    if token is None:
        return True
    else:
        return token.revoked


@auth.route('/sign-up', methods=['POST']) #normal signup
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
    
    body = request.get_json(silent=True)
    if body is None:
        raise APIException("not body in request")

    if 'email' not in body:
        raise APIException("'email' not found in request")
    elif not valid_email(body['email']):
        raise APIException("invalid 'email' format in request: %r" % body['email'])

    if 'password' not in body:
        raise APIException("'password' not found in request")
    elif not valid_password(body['password']):
        raise APIException("insecure 'password' in request: %r" % body['password'])

    if 'fname' not in body:
        raise APIException("'fname' not found in request")
    if not only_letters(body['fname'], spaces=True):
        raise APIException("invalid 'fname' parameter in request: %r" % body['fname'])
    fname = normalize_names(body['fname'], spaces=True)

    if 'lname' not in body:
        raise APIException("'lname' not found in request")
    if not only_letters(body['lname'], spaces=True):
        raise APIException("invalid 'lname' parameter in request %r" % body['lname'])
    lname = normalize_names(body['lname'], spaces=True)

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
        raise APIException("user %r already exists" % body['email']) # la columna email es unica,por eso este error significa solamente que el email ya existe

    return jsonify({'success': 'new user created'}), 201


@auth.route('/login', methods=['POST']) #normal login
def login():
    """
    PUBLIC ENDPOINT
    requerido: {
        "email": email,
        "password": password
    }
    respuesta: {
        "access_token": jwt_access_token,
        "user": {
            "id": id
            "fname": fname,
            "lname": lname,
            "user_picture": url_of_pic,
            "notifications": []
        }
    }
    """
    if not request.is_json:
        raise APIException("not json request")

    body = request.get_json(silent=True)
    if body is None:
        raise APIException("not json request")

    if 'email' not in body:
        raise APIException("'email' not found in request")

    if 'password' not in body:
        raise APIException("'password' not found in request")

    user = User.query.filter_by(email=body['email']).first()
    if user is None:
        raise APIException("user %r not found" %body['email'], status_code=404)

    if user.password_hash is None:
        raise APIException("user registered with social-api", status_code=401)

    if not check_password_hash(user.password_hash, body['password']):
        raise APIException("wrong password", status_code=404)
    
    access_token = create_access_token(identity=user.public_id)
    add_token_to_database(access_token, current_app.config['JWT_IDENTITY_CLAIM'])

    return jsonify({
        "user": user.serialize(), 
        "access_token": access_token, 
        "notifications": user.serialize_notifications(), 
        "activity": user.serialize_relations()
    })


@auth.route('/logout', methods=['GET', 'PUT']) #logout everywhere
@jwt_required
def logout_user():
    if not request.is_json:
        raise APIException("not JSON request")

    user_identity = get_jwt_identity()

    if request.method == 'GET':
        tokens = TokenBlacklist.query.filter_by(user_identity=user_identity, revoked=False).all()
        for token in tokens:
            token.revoked = True
        db.session.commit()
        return jsonify({"success": "user logged-out"}), 200

    elif request.method == 'PUT':
        token_info = decode_token(request.headers.get('Authorization').replace("Bearer ", ""))
        db_token = TokenBlacklist.query.filter_by(jti=token_info['jti']).first()
        db_token.revoked = True
        db.session.commit()
        return jsonify({"success": "user logged out"}), 200


@auth.route('/prune-db', methods=['GET']) #This must be a admin only endpoint.
def prune_db():
    prune_database()
    return jsonify({"success": "db pruned correctly"}), 200


@auth.route('/tokens', methods=['GET']) #Development endpoint only--- delete for production
@jwt_required
def get_all_tokens():

    if not request.is_json:
        raise APIException("not JSON request")

    user_identity = get_jwt_identity()
    tokens = TokenBlacklist.query.filter_by(user_identity=user_identity).all()
    response = list(map(lambda x: x.serialize(), tokens))

    return jsonify({"user_tokens": response}), 200


# Falta agregar endpoint para re establecer la contraseña del usuario.