from crypt import methods
import datetime
from random import randint

from flask import (
    Blueprint, request
)
#extensions
from app.extensions import (
    db
)
#models
from app.models.main import (
    User
)
from app.models.global_models import (
    TokenBlacklist
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
    get_jwt_identity, decode_token, get_jwt
)
#utils
from app.utils.helpers import (
    normalize_names, add_token_to_database, get_user_by_email, revoke_all_jwt, JSONResponse
)
from app.utils.validations import (
    validate_email, validate_pw, only_letters, validate_inputs
)
from app.utils.email_service import (
    send_verification_email
)
from app.utils.decorators import (
    json_required
)


auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/sign-up', methods=['POST']) #normal signup
@json_required({"email":str, "password":str, "fname":str, "lname":str})
def signup():
    """
    * PUBLIC ENDPOINT *
    Crear un nuevo usuario para la aplicación, tomando en cuenta que este usuario también debe 
    crear una compañía, es decir, todo usuario que complete el formulario de sign-up será un 
    administrador de su propia compañía.
    requerido: {
        "email": str,
        "password": str,
        "fname": str,
        "lname": str
    }
    respuesta: {
        "success":"created", 200
    }

    raised status codes {
        inputs error: 400
        user already exists: 409
        smtp service error: 503
        error in database session: 422
    }
    """

    body = request.get_json(silent=True)
    email, password, fname, lname = body['email'].lower(), body['password'], body['fname'], body['lname']
    validate_inputs({
        'email': validate_email(email),
        'password': validate_pw(password),
        'fname': only_letters(fname, spaces=True),
        'lname': only_letters(lname, spaces=True)
    })

    q_user = get_user_by_email(email)

    if q_user:
        # raise APIException("User {} already exists".format(q_user.email), status_code=409)
        raise APIException(f"User {q_user.email} already exists", status_code=409)

    #?processing
    try:
        new_user = User(
            email=email, 
            password=password, 
            fname=normalize_names(fname, spaces=True),
            lname=normalize_names(lname, spaces=True),
            email_confirmed=False,
            status='active'
        )
        db.session.add(new_user)
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        raise APIException(e.orig.args[0], status_code=422) # integrityError or DataError info

    #?response
    response = JSONResponse(message="New user created, email validation required", status_code=201)
    return response.to_json()


@auth_bp.route('/email-query', methods=['GET']) #email
@json_required({"email":str}, query_params=True) #validate inputs
def email_query():
    """
    * PUBLIC ENDPOINT *
    requerido: query string with email: ?email=xx@xx.com
    respuesta: {
        email_exists: bool === False if email is not found in db
        user: dict, => user info, if email exists
    }
    raised status codes {
        inputs error: 400,
        user not found: 404,
        user exists in app: 200
    }
    """

    email = str(request.args.get('email'))
    validate_inputs({
        'email': validate_email(email)
    })

    #?processing
    user = get_user_by_email(email)
    
    #?response
    if user is None:
        raise APIException(
            "user not found in database", 
            status_code=404,
        )
    response = JSONResponse(message="user exists in database")
    return response.to_json()


@auth_bp.route('/login', methods=['POST']) #normal login
@json_required({"email":str, "password":str})
def login():
    """
    * PUBLIC ENDPOINT *
    requerido: {
        "email": email, <str>
        "password": password, <str>
    }
    respuesta: {
        "access_token": jwt_access_token,
        "user": {
            "fname": string,
            "lname": string,
            "image": url,
            "home_address": dict,
            "personal_phone": string,
        }
    }
    raised status codes {
        invalid inputs: 400
        user not found: 404,
        invalid password: 403,
        user inactive: 402,
        user email not validated: 401
        smtp service error: 503,
    }
    """
    body = request.get_json(silent=True)
    email, pw = body['email'].lower(), body['password']

    validate_inputs({
        'email': validate_email(email),
        'password': validate_pw(pw)
    })

    #?processing
    user = get_user_by_email(email)
    if user is None:
        raise APIException("user email not found in database", status_code=404)

    if user.status is None or user.status != 'active':
        raise APIException("user is not active", status_code=402)

    if not check_password_hash(user.password_hash, pw):
        raise APIException("wrong password", status_code=403)

    if not user.email_confirmed:
        raise APIException("user's email not validated", status_code=401)
    
    # additional_claims = {"w_relation": w_relation.id}
    access_token = create_access_token(identity=email) #additional_claims=additional_claims
    add_token_to_database(access_token)

    #?response
    response = JSONResponse(
        message="user logged in",
        payload={
            "user": user.serialize(),
            "access_token": access_token
        },
        status_code=200
    )

    return response.to_json()


@auth_bp.route('/logout', methods=['GET']) #logout user
@json_required()
@jwt_required()
def logout():
    """
    ! PRIVATE ENDPOINT
    PERMITE AL USUARIO DESCONECTARSE DE LA APP, ESE ENDPOINT SE ENCARGA
    DE AGREGAR A LA BLOCKLIST EL O LOS TOKENS DEL USUARIO QUE ESTÁ
    HACIENDO LA PETICIÓN.

    methods:
        GET: si se accede a este endpoint con un GET req. se está solicitando una 
        desconexión en la sesion actual. Si se desea eliminar todas las sesiones
        activas, se debe agregar un parametro a la url en la forma:
            ?close=all
    Raises:
        APIException

    Returns:
        json: information about the transaction.
    """

    user_identity = get_jwt_identity()
    close = request.args.get('close')

    if close == 'all':
        revoke_all_jwt(user_identity)
        response = JSONResponse("user logged-out of all active sessions")
        return response.to_json()
    else:
        token_info = decode_token(request.headers.get('authorization').replace("Bearer ", ""))
        db_token = TokenBlacklist.query.filter_by(jti=token_info['jti']).first()
        db_token.revoked = True
        db_token.revoked_date = datetime.utcnow()
        db.session.commit()
        response = JSONResponse("user logged-out of current session")
        return response.to_json()


@auth_bp.route('/password-reset', methods=['GET']) #endpoint to restart password
@json_required({"email":str}, query_params=True)
def pw_reset():
    """
    * PUBLIC ENDPOINT *

    Endpoint utiliza ItsDangerous y send_email para que el usuario pueda reestablecer
    su contraseña.

    la aplicacion debe recibir el correo electrónico del usuario
    dentro de los parametros URL ?email=value

    la aplicación envía un correo electrónico al usuario que solicita el cambio de contraseña
    y devuelve una respuesta json con el mensaje de exito.
    
    raised errors {
        inputs error: 400
        user not found in database: 404,
        smtp service error: 503, (raised in function definition)
    }
    """    
    email = str(request.args.get('email'))
    validate_email(email)

    #?processing
    user = get_user_by_email(email)

    #?response
    if user is None:
        raise APIException("user not found in database", status_code=404)

    # send_pwchange_email({"name": user.fname, "email": user.email})
    response = JSONResponse("validation email sent to user")

    return response.to_json()


@auth_bp.route('/verification-code-request', methods=['GET'])
@json_required({'email':str}, query_params=True)
def verification_code_request():
    '''
    Endpoint to request a new verification code to restar the password or to validate a user email.
    '''
    email = str(request.args.get('email'))
    validate_inputs({
        'email': validate_email(email)
    })

    #?processing
    user = get_user_by_email(email)

    #response
    if user is None:
        raise APIException('User not found in database', status_code=404)

    random_code = randint(100000, 999999)
    token_expire_time = datetime.timedelta(days=1)
    token = create_access_token(identity=email, additional_claims={'verification_code': random_code}, expires_delta=token_expire_time)

    send_verification_email(verification_code=random_code, user={'fname': user.fname, 'email': user.email}) #503 error raised in funct definition

    response = JSONResponse(
        'verification code sent to user', 
        payload={
            'user_fname': user.fname,
            'user_lname': user.lname,
            'user_email': user.email,
            'verification_token': token,
            'token_expires': str(token_expire_time)
    })

    return response.to_json()

#!REVISAR Y DEBUGEAR CODIGO
@auth_bp.route('/verification-code-check', methods=['POST'])
@json_required({'code':str})
@jwt_required()
def verification_code_check():

    body = request.get_json(silent=True)
    claims = get_jwt()
    user = get_jwt_identity()

    if (body['code'] != str(claims['verification_code'])):
        raise APIException("invalid verification code")
    
    response = JSONResponse("test", payload={
        "rq_body": body,
        "jwt_claims": claims,
        "user": user
    })
    
    return response.to_json()