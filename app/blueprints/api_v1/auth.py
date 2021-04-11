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
    User, TokenBlacklist, Company, WorkRelation
)
from app.extensions import (
    jwt, db
)
from app.utils.exceptions import APIException
from app.utils.helpers import (
    normalize_names, add_token_to_database,
    valid_email, valid_password, only_letters, in_request, resp_msg
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
    #?validations
    if not request.is_json:
        raise APIException("json request only")
    
    body = request.get_json(silent=True)
    if body is None:
        raise APIException("not body in request")

    rq = in_request(body, tuple(['email', 'password', 'fname', 'lname', 'company_name']))
    if not rq['complete']:
        raise APIException(resp_msg.missing_args(rq['missing']))

    if not valid_email(body['email']):
        raise APIException(resp_msg.invalid_format('email', body['email']))

    if not valid_password(body['password']):
        raise APIException(resp_msg.invalid_pw())

    if not only_letters(body['fname'], spaces=True):
        raise APIException(resp_msg.invalid_format('fname', body['fname']))

    if not only_letters(body['lname'], spaces=True):
        raise APIException(resp_msg.invalid_format('lname', body['lname']))

    #?processing
    try:
        new_user = User(
            email=body['email'], 
            password=body['password'], 
            fname=normalize_names(body['fname'], spaces=True),
            lname=normalize_names(body['lname'], spaces=True), 
            public_id=str(uuid.uuid4())
        )
        new_company = Company(
            public_id=str(uuid.uuid4()),
            name=normalize_names(body['company_name'], spaces=True)
        )
        relation = WorkRelation(
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
        raise APIException("user %r already exists in app" % body['email']) # la columna email es unica, este error significa solamente que el email ya existe

    #?response
    return jsonify({'success': 'new user created'}), 201


@auth_bp.route('/email-validation', methods=['GET']) #email validation sent in query params
def email_validation():
    """
    PUBLIC ENDPOINT
    requerido: query string with email: ?email=xx@xx.com
    respuesta: {
        email_exists: bool === False if email is not found in db
        user: dict, => user info, if email exists
    }
    """
    #?validations
    if not request.is_json:
        raise APIException(resp_msg.not_json_rq())

    rq = in_request(request.args, tuple(['email']))
    if not rq['complete']:
        raise APIException(resp_msg.missing_args(rq['missing']))

    email = request.args.get('email')

    if not valid_email(email):
        raise APIException(resp_msg.invalid_format('email', email))

    #?processing
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({
            'email_exists': False,
            'msg': 'User not found in db'
        }), 200

    #?response
    return jsonify({
        'email_exists': True,
        'user': dict({'user_status': user.status}, **user.serialize_companies())
    }), 200


@auth_bp.route('/login', methods=['POST']) #normal login
def login():
    """
    PUBLIC ENDPOINT
    requerido: {
        "email": email, <str>
        "password": password, <str>
        "company_id": id <int>
    }
    respuesta: {
        "access_token": jwt_access_token,
        "user": {
            "public_id": int,
            "fname": string,
            "lname": string,
            "profile_img": url,
            "home_address": dict,
            "personal_phone": string,
            "company_profile": dict
        }
    }
    """
    
    #?validations
    if not request.is_json:
        raise APIException(resp_msg.not_json_rq())

    body = request.get_json(silent=True)
    if body is None:
        raise APIException(resp_msg.not_json_rq())

    rq = in_request(body, tuple(['email', 'password', 'company_id']))
    if not rq['complete']:
        raise APIException(resp_msg.missing_args(rq['missing']))

    email = body['email']
    pw = body['password']
    company_id = body['company_id']

    if not valid_email(email):
        raise APIException(resp_msg.invalid_format('email', email))

    if not type(company_id)==int:
        raise APIException(resp_msg.invalid_format('company_id', value=type(company_id).__name__ ,expected='integer')) 

    #?processing
    user = User.query.filter_by(email=email).first()
    if user is None:
        raise APIException(resp_msg.not_found('email'), status_code=404)
    if user.password_hash is None:
        if user.status is None:
            raise APIException("user must validate credentials")
        raise APIException("user registered with social-api")
    if not check_password_hash(user.password_hash, pw):
        raise APIException("wrong password, try again", status_code=404)

    w_relation = WorkRelation.query.filter_by(user=user, company_id=company_id).first()
    if w_relation is None:
        raise APIException("user is not related with company id: {}".format(company_id), status_code=404)
    
    access_token = create_access_token(identity=user.email) #TODO: add workrelation_id to jwt
    add_token_to_database(access_token)

    #?response
    return jsonify({
        "user": user.serialize(),
        "company": w_relation.serialize_company(),
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
        raise APIException(resp_msg.not_json_rq())

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


# #TODO: Falta agregar endpoint para reestablecer la contraseña del usuario.