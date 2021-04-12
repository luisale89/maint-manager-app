import uuid
import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from itsdangerous import (
    URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
)
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
from app.utils.mail_api import (
    send_email
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

serializer = URLSafeTimedSerializer(os.environ['SECRET_KEY'])

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
        raise APIException(resp_msg.not_json_rq())
    
    body = request.get_json(silent=True)
    if body is None:
        raise APIException(resp_msg.not_json_rq())

    rq = in_request(body, ('email', 'password', 'fname', 'lname', 'company_name',))
    if not rq['complete']:
        raise APIException(resp_msg.missing_args(rq['missing']))

    email, password, fname, lname, company_name = str(body['email']), str(body['password']), str(body['fname']), str(body['lname']), str(body['company_name'])

    if not valid_email(email):
        raise APIException(resp_msg.invalid_format('email', email))

    if not valid_password(password):
        raise APIException(resp_msg.invalid_pw())

    if not only_letters(fname, spaces=True):
        raise APIException(resp_msg.invalid_format('fname', fname))

    if not only_letters(lname, spaces=True):
        raise APIException(resp_msg.invalid_format('lname', lname))
        
    #?processing
    try:
        new_user = User(
            email=body['email'], 
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
    except IntegrityError:
        db.session.rollback()
        raise APIException("user %r already exists in app" % body['email']) # la columna email es unica, este error significa solamente que el email ya existe

    #?response
    return jsonify({'success': 'new user created'}), 201


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
        raise APIException(resp_msg.not_json_rq())

    rq = in_request(request.args, ('email',))
    if not rq['complete']:
        raise APIException(resp_msg.missing_args(rq['missing']))

    email = str(request.args.get('email'))

    if not valid_email(email):
        raise APIException(resp_msg.invalid_format('email', email))

    #?processing
    user = User.query.filter_by(email=email).first()
    
    #?response
    if user is None:
        return jsonify({
            'email_exists': False,
            'msg': 'User not found in db'
        }), 200
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

    rq = in_request(body, ('email', 'password', 'company_id',))
    if not rq['complete']:
        raise APIException(resp_msg.missing_args(rq['missing']))

    email, pw, company_id = str(body['email']), str(body['password']), body['company_id']

    if not valid_email(email):
        raise APIException(resp_msg.invalid_format('email', email))

    if not isinstance(company_id, int):
        raise APIException(resp_msg.invalid_format('company_id', type(company_id).__name__ ,'integer')) 

    #?processing
    user = User.query.filter_by(email=email).first()
    if user is None:
        raise APIException(resp_msg.not_found('email'), status_code=404)
    if not check_password_hash(user.password_hash, pw):
        raise APIException("wrong password, try again", status_code=404)
    if user.status is None or user.status != 'active':
        return jsonify({"invalid": "user is not active"}), 400

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


@auth_bp.route('/password-reset', methods=['GET', 'PUT'])
def reset_password():
    '''
    PASSWORD RESET ENDPOINT - PUBLIC

    Endpoint utiliza ItsDangerous y send_email para que el usuario pueda reestablecer
    su contraseña en caso de olvidarla.

    Dos métodos son aceptados:

    * GET

    En este metodo, la aplicacion debe recibir el correo del usuario que quiere
    reestablecer su contraseña dentro de los parametros URL ?'email'='value'

    la aplicación envía un correo electrónico al usuario que solicita el cambio de contraseña
    y devuelve una respuesta json con el mensaje de exito.

    * PUT

    En este metodo, la aplicacion debe recibir dentro del cuerpo del request json:
    - token: Token enviado al correo electrónico del usuario.
    - password: Nueva contraseña del usario, validada previamente en el front-end

    la aplicación envía un mensaje de exito si pudo realizar la actualización de la contraseña.
    
    '''
    if not request.is_json:
        raise APIException(resp_msg.not_json_rq())
    
    if request.method == 'GET':
        rq = in_request(request.args, ('email',))
        if not rq['complete']:
            raise APIException(resp_msg.missing_args(rq['missing']))
        
        email = str(request.args.get('email'))

        if not valid_email(email):
            raise APIException(resp_msg.invalid_format('email', email))

        #?processing
        user = User.query.filter_by(email=email).first()

        #?response
        if user is None:
            raise APIException(resp_msg.not_found('user'), status_code=404)

        token =  serializer.dumps(email, salt='password-reset')
        msg = send_email(
            to_list=[{"name": user.fname, "email": user.email}],
            mail_link=token,
            subject="Reestablecer contraseña"
        )
        if not msg['sent']:
            raise APIException("email not sent to user, msg: '{}'".format(msg['msg']), status_code=500)
        
        return jsonify({"msg": "email was sent to user"}), 200

    if request.method == 'PUT':
        body = request.get_json(silent=True)
        if body is None:
            raise APIException(resp_msg.not_json_rq())
        
        rq = in_request(body, ('token', 'password',))
        if not rq['complete']:
            raise APIException(resp_msg.missing_args(rq['missing']))
        
        token = str(body['token'])
        password = str(body['password'])

        if not valid_password(password):
            raise APIException(resp_msg.invalid_pw())

        try:
            email_loaded = serializer.loads(token, salt='password-reset', max_age=300) #token tiene una duración de 5 minutos
            user = User.query.filter_by(email=email_loaded).first()
            user.password = password
            db.session.commit()
        
        except SignatureExpired:
            raise APIException('token has expired', status_code=401)
        
        except BadTimeSignature:
            raise APIException('invalid token has been detected', status_code=401)

        return jsonify({"msg": "password updated"}), 200


#TODO: Crear endpoint para validar el correo electrónico de un usuario.
#TODO: 