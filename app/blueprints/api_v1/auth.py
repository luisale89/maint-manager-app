import uuid
import os
from datetime import datetime
from flask import (
    Blueprint, jsonify, request
)
#extensions
from app.extensions import (
    jwt, db
)
#models
from app.models.users import (
    User, TokenBlacklist, Company, WorkRelation
)
#exceptions
from sqlalchemy.exc import (
    IntegrityError, DataError
)
from app.utils.exceptions import APIException
#jwt
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token, jwt_required, 
    get_jwt_identity, decode_token
)
#utils
from app.utils.helpers import (
    normalize_names, add_token_to_database, api_responses, get_user, revoke_all_jwt
)
from app.utils.validations import (
    validate_email, validate_pw, in_request, only_letters
)
from app.utils.email_service import (
    send_validation_mail, send_pwchange_mail
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
        raise APIException(api_responses.not_json_rq())
    
    body = request.get_json(silent=True)
    if body is None:
        raise APIException(api_responses.not_json_rq())

    rq = in_request(body, ('email', 'password', 'fname', 'lname', 'company_name',))
    if not rq['complete']:
        raise APIException(api_responses.missing_args(rq['missing']))

    email, password, fname, lname, company_name = str(body['email']), str(body['password']), str(body['fname']), str(body['lname']), str(body['company_name'])
    #validations -> exceptions
    validate_email(email)
    validate_pw(password)
    only_letters(fname, spaces=True)
    only_letters(lname, spaces=True)

    q_user = get_user(email)

    if q_user:
        raise APIException("User {} already exists".format(q_user.email))

    #?processing
    try:
        new_user = User(
            email=email, 
            password=password, 
            fname=normalize_names(fname, spaces=True),
            lname=normalize_names(lname, spaces=True), 
            public_id=str(uuid.uuid4()),
            email_confirm=False,
            status='active'
        )
        new_company = Company(
            public_id=str(uuid.uuid4()),
            name=normalize_names(company_name, spaces=True)
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
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        raise APIException(e.orig.args[0]) # integrityError or DataError info

    mail = send_validation_mail({"name": fname, "email": email})

    if not mail['sent']:
        raise APIException("fail on sending validation email to user, msg: '{}'".format(mail['msg']), status_code=500)

    #?response
    return jsonify({'success': 'new user created, complete email validation is required'}), 201


@auth_bp.route('/email-query', methods=['GET']) #email validation sent in query params
def email_query():
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
        raise APIException(api_responses.not_json_rq())

    rq = in_request(request.args, ('email',))
    if not rq['complete']:
        raise APIException(api_responses.missing_args(rq['missing']))

    email = str(request.args.get('email'))
    validate_email(email)

    #?processing
    user = get_user(email)
    
    #?response
    if user is None:
        return jsonify({
            'email_exists': False,
            'msg': 'User not found in db'
        }), 200
    return jsonify({
        'email_exists': True,
        'user': dict({'user_status': user.status}, **user.serialize_companies()),
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
        raise APIException(api_responses.not_json_rq())

    body = request.get_json(silent=True)
    if body is None:
        raise APIException(api_responses.not_json_rq())

    rq = in_request(body, ('email', 'password', 'company_id',))
    if not rq['complete']:
        raise APIException(api_responses.missing_args(rq['missing']))

    email, pw, company_id = str(body['email']), str(body['password']), body['company_id']
    validate_email(email)

    if not isinstance(company_id, int):
        raise APIException(api_responses.invalid_format('company_id', type(company_id).__name__ ,'integer')) 

    #?processing
    user = get_user(email)
    if user is None:
        raise APIException(api_responses.not_found('email'), status_code=404)
    if not check_password_hash(user.password_hash, pw):
        raise APIException("wrong password, try again", status_code=404)
    if user.status is None or user.status != 'active':
        raise APIException("user is not active")

    w_relation = WorkRelation.query.filter_by(user=user, company_id=company_id).first()
    if w_relation is None:
        raise APIException("user is not related with company id: {}".format(company_id), status_code=404)
    
    additional_claims = {"w_relation": w_relation.id}

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    add_token_to_database(access_token)

    #?response
    return jsonify({
        "user": user.serialize(),
        "company": w_relation.serialize_company(),
        "access_token": access_token
    }), 200


@auth_bp.route('/logout', methods=['GET']) #logout user
@jwt_required()
def logout():
    """LOGOUT ENDPOINT - PRIVATE 
    PERMITE AL USUARIO DESCONECTARSE DE LA APP, ESE ENDPOINT SE ENCARGA
    DE AGREGAR A LA BLOCKLIST EL O LOS TOKENS DEL USUARIO QUE ESTÁ
    HACIENDO LA PETICIÓN.

    methods:
        GET: si se accede a este endpoint con un GET req. se está solicitando una 
        desconexión en la sesion actual. Si se desea eliminar todas las sesiones
        activas, se debe agregar un parametro a la url en la forma:
            ?close-all=yes
    Raises:
        APIException

    Returns:
        json: information about the transaction.
    """
    if not request.is_json:
        raise APIException(api_responses.not_json_rq())

    user_identity = get_jwt_identity()
    close_all = request.args.get('close-all')

    if close_all:
        revoke_all_jwt(user_identity)
        return jsonify({"success": "user logged-out"}), 200
    else:
        token_info = decode_token(request.headers.get('authorization').replace("Bearer ", ""))
        db_token = TokenBlacklist.query.filter_by(jti=token_info['jti']).first()
        db_token.revoked = True
        db_token.revoked_date = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": "user logged out"}), 200


@auth_bp.route('/password-reset', methods=['GET']) #endpoint to restart password
def pw_reset():
    '''
    PASSWORD RESET ENDPOINT - PUBLIC

    Endpoint utiliza ItsDangerous y send_email para que el usuario pueda reestablecer
    su contraseña o validar el correo electrónico, dependiendo del endpoint.

    métodos aceptados:

    * GET

    En este metodo, la aplicacion debe recibir el correo electrónico del usuario
    dentro de los parametros URL ?'email'='value'

    la aplicación envía un correo electrónico al usuario que solicita el cambio de contraseña
    y devuelve una respuesta json con el mensaje de exito.
    
    '''
    if not request.is_json:
        raise APIException(api_responses.not_json_rq())
    
    rq = in_request(request.args, ('email',))
    if not rq['complete']:
        raise APIException(api_responses.missing_args(rq['missing']))
    
    email = str(request.args.get('email'))
    validate_email(email)

    #?processing
    user = get_user(email)

    #?response
    if user is None:
        raise APIException(api_responses.not_found('user'), status_code=404)

    mail = send_pwchange_mail({"name": user.fname, "email": user.email})

    if not mail['sent']:
        raise APIException("fail on sending email to user, msg: '{}'".format(mail['msg']), status_code=500)
    
    return jsonify({"success": "password change validation sent to user"}), 200


@auth_bp.route('/email-validation', methods=['GET'])
def email_validation():
    '''
    EMAIL VALIDATION ENDPOINT - PUBLIC

    Endpoint utiliza ItsDangerous y send_email para que el usuario pueda 
    validar su correo electrónico al momento de hacer un registro en la app.

    Dos métodos son aceptados:

    * GET

    En este metodo, la aplicacion debe recibir el correo electrónico del usuario
    dentro de los parametros URL ?'email'='value'

    la aplicación envía un correo electrónico al usuario que solicita la validacion del correo
    electronivo y devuelve una respuesta json con el mensaje de exito.
    
    '''
    if not request.is_json:
        raise APIException(api_responses.not_json_rq())

    rq = in_request(request.args, ('email',))
    if not rq['complete']:
        raise APIException(api_responses.missing_args(rq['missing']))
    
    email = str(request.args.get('email'))
    validate_email(email)

    #?processing
    user = get_user(email)

    #?response
    if user is None:
        raise APIException(api_responses.not_found('user'), status_code=404)

    mail = send_validation_mail({"name": user.fname, "email": user.email})

    if not mail['sent']:
        raise APIException("fail on sending email to user, msg: '{}'".format(mail['msg']), status_code=500)
    
    return jsonify({"success": "validation request sent to user"}), 200