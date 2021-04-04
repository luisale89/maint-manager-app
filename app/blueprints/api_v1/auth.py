import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import (
    IntegrityError
)
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token, jwt_required, 
    get_jwt_identity, decode_token
)
from app.models.users import (
    User, TokenBlacklist, Company, HumanResources
)
from app.extensions import (
    jwt, db
)
from app.utils.exceptions import APIException
from app.utils.helpers import (
    normalize_names, add_token_to_database, 
    prune_database, valid_email, valid_password, only_letters
)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    if token is None:
        return True
    else:
        return token.revoked


auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@auth_bp.route('/sign-up', methods=['POST']) #normal signup
def signup():
    """
    * PUBLIC ENDPOINT *
    Crear un nuevo usuario para la aplicación, tomando en cuenta que este usuario también debe 
    crear una compañía, es decir, todo usuario que complete el formulario de sign-up será un 
    administrador de su propia compañía.
    requerido: {
        "email": email,
        "password": psw,
        "fname": fname,
        "lname": lname,
        "company_name": string,
    }
    respuesta: {
        "success":"created", 200
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

    if 'company_name' not in body:
        raise APIException("'company_name' not found in request")
    company_name = normalize_names(body['company_name'], spaces=True)

    try:
        new_user = User(
            email=body['email'], 
            password=body['password'], 
            fname=fname,
            lname=lname, 
            public_id=str(uuid.uuid4())
        )
        new_company = Company(
            public_id=str(uuid.uuid4()),
            name=company_name
        )
        relation = HumanResources(
            user=new_user,
            company=new_company,
            user_role="Admin"
        )
        db.session.add(new_user)
        db.session.add(new_company)
        db.session.add(relation)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIException("user %r already exists" % body['email']) # la columna email es unica, este error significa solamente que el email ya existe

    return jsonify({'success': 'new user created'}), 200


@auth_bp.route('/email-validation', methods=['GET']) #email validation sent in query params
def user_validation():
    """
    PUBLIC ENDPOINT
    requerido: {email: email}
    respuesta: {
        email: valid,
        user: user_status,
        companies: (if valid) -> [companies]
    }
    """
    if not request.is_json:
        raise APIException("not json request")

    email = request.args.get('email')
    if email is None:
        raise APIException("'email' not found in query params")
    if not valid_email(email):
        raise APIException("invalid 'email' format in query params: %r" %email)

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({
            'email_status': 'unregistered'
        }), 200
    
    return jsonify({
        'email_status': 'registered',
        'user': dict({'user_status': user.status}, **user.serialize_companies())
    }), 200


@auth_bp.route('/login', methods=['POST']) #normal login
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
            "public_id": int,
            "fname": string,
            "lname": string,
            "profile_img": url,
            "home_address": dict,
            "personal_phone": string
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
    elif not valid_email(body['email']):
        raise APIException("invalid 'email' format in request: %r" %body['email'])

    if 'password' not in body:
        raise APIException("'password' not found in request")

    user = User.query.filter_by(email=body['email']).first()
    if user is None:
        raise APIException("user %r not found" %body['email'], status_code=404)

    if user.password_hash is None:
        if user.status is None:
            raise APIException("user must validate credentials", status_code=400)
        raise APIException("user registered with social-api", status_code=400)

    if not check_password_hash(user.password_hash, body['password']):
        raise APIException("wrong password, try again", status_code=404)
    
    access_token = create_access_token(identity=user.email)
    add_token_to_database(access_token)

    return jsonify({
        "user": dict(**user.serialize(), **user.serialize_companies()),
        "access_token": access_token
    }), 200


@auth_bp.route('/logout', methods=['GET', 'DELETE']) #logout everywhere
@jwt_required()
def logout_user():
    """LOGOUT ENDPOINT - PRIVATE 
    PERMITE AL USUARIO DESCONECTARSE DE LA APP, ESE ENDPOINT SE ENCARGA
    DE AGREGAR A LA BLOCKLIST EL O LOS TOKENS DEL USUARIO QUE ESTÁ
    HACIENDO LA PETICIÓN.

    methods:
        DELETE: si se accede a este endpoint con un DELETE req. se está solicitando una
        desconexión únicamente en la sesión actual. El resto de tokens existentes
        se mantendrán activos.

        GET: si se accede a este endpoint con un GET req. se está solicitando una 
        desconexión en todas las sesiones existentes. Todos los tokens existentes estarán en la
        lista negra de la base de datos.

    Raises:
        APIException

    Returns:
        json: information about the transaction.
    """
    if not request.is_json:
        raise APIException("not JSON request")

    user_identity = get_jwt_identity()

    if request.method == 'GET':
        tokens = TokenBlacklist.query.filter_by(user_identity=user_identity, revoked=False).all()
        for token in tokens:
            token.revoked = True
            token.revoked_date = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": "user logged-out"}), 200

    elif request.method == 'DELETE':
        token_info = decode_token(request.headers.get('authorization').replace("Bearer ", ""))
        db_token = TokenBlacklist.query.filter_by(jti=token_info['jti']).first()
        db_token.revoked = True
        db_token.revoked_date = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": "user logged out"}), 200


@auth_bp.route('/prune-db', methods=['GET'])
def prune_db():
    """LIMPIAR TOKENS VENCIDOS - ADMIN ENDPOINT
    Returns:
        json: success msg.
    """
    #TODO: Establecer este endpoint con acceso restringido a usuarios administradores.
    prune_database()
    return jsonify({"success": "db pruned correctly"}), 200


# #TODO: Falta agregar endpoint para reestablecer la contraseña del usuario.