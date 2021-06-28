
from flask import (
    Blueprint, render_template, request, session, flash
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

validations_bp = Blueprint('validations_bp', __name__)

@validations_bp.route('/email-validation', methods=['GET'])
def email_validation():
    
    email = str(request.args.get('email', ''))
    token = str(request.args.get('token', ''))

    result = validate_url_token(token=token, salt=email_salt, identifier=email)
    if not result['valid']:
        flash('invalid token')
        return render_template('landing/404.html')

    user_q = get_user(email)
    if user_q is None:
        flash('username not found')
        return render_template('landing/404.html')
    
    try:
        user_q.email_confirm = True
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        flash(e.orig.args[0])
        return render_template('landing/404.html')

    context={
        "title": "Validacion de correo electronico", 
        "description": "validacion de correo electronico", 
        "email": email
    }
    return render_template('validations/email-validated.html', **context)


# password reset endpoint
@validations_bp.route('/pw-reset', methods=['GET', 'POST'])
def pw_reset():

    error = {}
    if request.method == 'GET':
        #data from url_parameters
        email = str(request.args.get('email', ''))
        token = str(request.args.get('token', ''))

        result = validate_url_token(token=token, salt=pw_salt, identifier=email)
        if not result['valid']:
            flash(result.get('msg', ''))
            return render_template('landing/404.html')

        identifier = result['id']
        revoke_all_jwt(identifier) #logout user when this point is reached

        context = {
            "title": "Cambio de Contraseña", 
            "description": "Formulario para el cambio de contraseña", 
            "email": identifier,
            "error": error
        }
        session['url_token'] = token #store url_token in session (coockie)
        session['username'] = email #store email in session (coockie)
        return render_template('validations/pw-update-form.html', **context) #devuelve el formulario para el cambio de contrasena

    pw = request.form.get('password', '')
    repw = request.form.get('re-password', '')
    token = session.get('url_token', '') #url token stored in cookie
    email = session.get('username', '') #email token stored in coockie
    
    token_decode = validate_url_token(token=token, salt=pw_salt, identifier=email)
    if not token_decode['valid']:
        flash(token_decode.get('msg', ''))
        return render_template('landing/404.html')

    pw_valid = validate_pw(pw)
    if pw_valid['error']:
        error['password'] = "formato de contraseña incorrecto"

    if pw != repw:
        error['re_password'] = "Contraseñas no coinciden"
    
    user_q = get_user(email)
    if user_q is None:
        flash("Usuario {} no existe en la base de datos".format(email))
        return render_template('landing/404.html')
    
    if not error:
        try:
            user_q.password = pw
            db.session.commit()
        except (IntegrityError, DataError) as e:
            db.session.rollback()
            flash(e.orig.args[0])
            return render_template('landing/404.html')

        context = {
            "title": "Nueva Contraseña", 
            "description": "Nueva contraseña establecida con exito", 
        }
        session.pop('url_token')
        session.pop('username')
        return render_template('validations/pw-updated.html', **context)

    context = {
            "title": "Cambio de Contraseña", 
            "description": "Formulario para el cambio de contraseña", 
            "email": user_q.email,
            "error": error
    }
    return render_template('validations/pw-update-form.html', **context)