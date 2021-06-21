
from operator import is_
from flask import (
    Blueprint, render_template, request
)
#utils
from app.utils.helpers import (
    get_user, revoke_all_jwt
)
from app.utils.validations import (
    validate_pw
)
from app.utils.token_factory import validate_url_token
#extensions
from app.extensions import db
#models
from sqlalchemy.exc import (
    IntegrityError, DataError
)
import os

email_salt = os.environ['EMAIL_VALID_SALT']
pw_salt = os.environ['PW_VALID_SALT']

validation_bp = Blueprint('validation_bp', __name__)

@validation_bp.route('/email-confirmation')
def email_validation():
    
    email = str(request.args.get('email'))
    token = str(request.args.get('token'))

    result = validate_url_token(token=token, salt=email_salt)
    if not result['valid']:
       return render_template('landing/404.html')

    identifier = result['id']
    if identifier != email:
        return render_template('landing/404.html')

    user_q = get_user(email)
    if user_q is None:
        return render_template('landing/404.html')
    
    try:
        user_q.email_confirm = True
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        return render_template('landing/404.html')

    context={
        "title": "Validacion de correo electronico", 
        "description": "validacion de correo electronico", 
        "email": identifier
    }
    return render_template('validations/email-validated.html', **context)


# password reset endpoint
@validation_bp.route('/pw-reset', methods=['GET', 'POST'])
def pw_reset():

    error = {}
    if request.method == 'GET':

        email = str(request.args.get('email'))
        token = str(request.args.get('token'))

        result = validate_url_token(token=token, salt=pw_salt)
        if not result['valid']:
            return render_template('landing/404.html', html_msg = "token no es valido o esta vencido")

        identifier = result['id']
        if identifier != email:
            return render_template('landing/404.html', html_msg = "parametros URL invalidos")
        
        revoke_all_jwt(identifier) #logout user in this point, it's safe
        context = {
            "title": "Cambio de Contraseña", 
            "description": "Formulario para el cambio de contraseña", 
            "email": identifier,
            "url_token": token,
            "error": error
        }

        return render_template('validations/pw-update-form.html', **context) #devuelve el formulario para el cambio de contrasena

    pw = request.form.get('password')
    repw = request.form.get('re-password')
    token = request.form.get('url_token')

    if not validate_pw(pw, is_api = False):
        error['password'] = "formato de contraseña incorrecto"

    if pw != repw:
        error['re_password'] = "Contraseñas no coinciden"

    token_decode = validate_url_token(token=token, salt=pw_salt)
    if not token_decode['valid']:
        return render_template('landing/404.html', html_msg = "token no es valido o esta vencido")
    
    email = token_decode['id']
    user_q = get_user(email) #token_decode['id'] = user email
    if user_q is None:
        return render_template('landing/404.html', html_msg = "Usuario no existe")
    
    if not error:
        try:
            user_q.password = pw
            db.session.commit()
        except (IntegrityError, DataError) as e:
            db.session.rollback()
            return render_template('landing/404.html', html_msg = e.orig.args[0])

        context = {
            "title": "Nueva Contraseña", 
            "description": "Nueva contraseña establecida con exito", 
        }
        return render_template('validations/pw-updated.html', **context)

    context = {
            "title": "Cambio de Contraseña", 
            "description": "Formulario para el cambio de contraseña", 
            "email": user_q.email,
            "url_token": token,
            "error": error
    }
    return render_template('validations/pw-update-form.html', **context)

#! Es necesario revisar "session" para mantener los parametros url entre solicitudes. REVISAR
