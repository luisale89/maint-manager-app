

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
#exceptions
from sqlalchemy.exc import (
    IntegrityError, DataError
)
from app.utils.exceptions import APIException
#jwt
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token, get_jwt
)
#utils
from app.utils.helpers import (
    normalize_names, JSONResponse
)
from app.utils.validations import (
    validate_email, validate_pw, only_letters, validate_inputs
)
from app.utils.email_service import (
    send_verification_email
)
from app.utils.decorators import (
    json_required, verification_token_required, verified_token_required, user_required
)
from app.utils.redis_service import add_jwt_to_blocklist
from app.utils.db_operations import get_user_by_email


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

    q_user = User.query.filter_by(email=email).first()

    if q_user:
        raise APIException(f"User {q_user.email} already exists in database", status_code=409)

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
    resp = JSONResponse(message="New user created, email validation required", status_code=201)
    return resp.to_json()


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

    if user.status is None or user.status != 'active':
        raise APIException("user is not active", status_code=402)

    if not user.email_confirmed:
        raise APIException("user's email not validated", status_code=401)

    if not check_password_hash(user.password_hash, pw):
        raise APIException("wrong password", status_code=403)
    
    #*user-access-token
    access_token = create_access_token(
        identity=email, 
        additional_claims={'user_access_token': True}
    )

    #?response
    resp = JSONResponse(
        message="user logged in",
        payload={
            "user": user.serialize(),
            "access_token": access_token
        },
        status_code=200
    )

    return resp.to_json()


@auth_bp.route('/logout', methods=['DELETE']) #logout user
@json_required()
@user_required()
def logout():
    """
    PERMITE AL USUARIO DESCONECTARSE DE LA APP, ESE ENDPOINT SE ENCARGA
    DE AGREGAR A LA BLOCKLIST EL O LOS TOKENS DEL USUARIO QUE ESTÁ
    HACIENDO LA PETICIÓN.

    methods:
        DELETE: si se accede a este endpoint con un GET req. se está solicitando una 
        desconexión en la sesion actual.
    Raises:
        APIException -> 500 in case of connection error to db service.

    Returns:
        json: information about the transaction.
    """

    add_jwt_to_blocklist(get_jwt())
    resp = JSONResponse("user logged-out of current session")
    return resp.to_json()


@auth_bp.route('/email-query', methods=['GET']) #email
@json_required({"email":str}, query_params=True) #validate inputs
def email_query():
    """
    * PUBLIC ENDPOINT *
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
    response = JSONResponse(message=f"email: {user.email} found in database")
    return response.to_json()


@auth_bp.route('/request-verification-code', methods=['GET'])
@json_required({'email':str}, query_params=True)
def request_verification_code():
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
    random_code = randint(100000, 999999)
    token = create_access_token(
        identity=email, 
        additional_claims={
            'verification_code': random_code,
            'verification_token': True
        }
    )

    send_verification_email(verification_code=random_code, user={'fname': user.fname, 'email': user.email}) #503 error raised in funct definition

    response = JSONResponse(
        message='verification code sent to user', 
        payload={
            'user_fname': user.fname,
            'user_lname': user.lname,
            'user_email': user.email,
            'verification_token': token
    })

    return response.to_json()


@auth_bp.route('/check-verification-code', methods=['PUT'])
@json_required({'verification_code':int})
@verification_token_required()
def check_verification_code():
    '''
    endpoint: {{auth_bp}}/check-verification-code
    methods: [PUT]
    description: endpoint to validate user's verification code sent to them by email.

    '''
    # body = request.get_json(silent=True)
    # claims = get_jwt()
    claims = get_jwt()
    code_in_request = request.get_json().get('verification_code')
    code_in_token = claims.get('verification_code')

    if (code_in_request != code_in_token):
        raise APIException("invalid verification code")
    
    add_jwt_to_blocklist(claims) #invalida el uso del token una vez se haya validado del codigo

    verified_user_token = create_access_token(
        identity=claims['sub'], 
        additional_claims={
            'verified_token': True
        }
    )


    resp = JSONResponse("code verification success", payload={'user_verified_token': verified_user_token})
    
    return resp.to_json()


@auth_bp.route("/confirm-user-email", methods=['GET'])
@json_required()
@verified_token_required()
def confirm_user_email():
    '''
    endpoint: {{auth_bp}}/confirm-user-email
    methods: [PUT]
    description: endpoint to confirm user email, verified_token required..

    '''
    claims = get_jwt()
    user = get_user_by_email(claims['sub'])

    user.email_confirmed = True

    try:
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        raise APIException(e.orig.args[0], status_code=422) # integrityError or DataError info
    
    add_jwt_to_blocklist(claims)

    resp = JSONResponse(message="user's email has been confirmed")
    return resp.to_json()


@auth_bp.route("/change-forgotten-password", methods=['PUT'])
@json_required({"new_password":str})
@verified_token_required()
def change_forgotten_password():
    '''
    endpoint: {{auth_bp}}/change-password
    methods: [PUT]
    description: endpoint to change user's password.

    '''
    claims = get_jwt()
    new_password = request.get_json().get('new_password')

    validate_inputs({
        'password': validate_pw(new_password)
    })

    user = get_user_by_email(claims['sub'])
    
    user.password = new_password

    try:
        db.session.commit()
    except (IntegrityError, DataError) as e:
        raise APIException(e.orig.args[0], status_code=422)

    add_jwt_to_blocklist(claims)

    resp = JSONResponse(message="user's password updated")
    return resp.to_json()