
from operator import is_
from flask import (
    Blueprint, render_template, request
)
#utils
from app.utils.helpers import (
    get_user
)
from app.utils.validations import (
    validate_pw
)
from app.utils.token_factory import validate_url_token
#extensions
from app.extensions import db
#models
from app.models.users import User
from sqlalchemy.exc import (
    IntegrityError, DataError
)
import os

email_salt = os.environ['EMAIL_VALID_SALT']
pw_salt = os.environ['PW_VALID_SALT']

validations_bp = Blueprint('validations_bp', __name__)

@validations_bp.route('/email-confirmation')
def email_validation():
    
    email = str(request.args.get('email'))
    token = str(request.args.get('token'))

    # if not valid_email(email):
    #     return render_template('landing/404.html')

    result = validate_url_token(token=token, salt=email_salt)
    if not result['valid']:
       return render_template('landing/404.html')

    identifier = result['id']
    if identifier != email:
        return render_template('landing/404.html')

    q_user = get_user(email)
    if q_user is None:
        return render_template('landing/404.html')
    
    try:
        q_user.email_confirm = True
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        return render_template('landing/404.html')

    data={
        "title": "email validation", 
        "description": "validacion de correo electronico", 
        "email": identifier
    }
    return render_template('validations/email-validated.html', meta=data)


# password reset endpoint
@validations_bp.route('/pw-reset', methods=['GET', 'POST'])
def pw_reset():

    if request.method == 'GET':

        email = str(request.args.get('email'))
        token = str(request.args.get('token'))

        result = validate_url_token(token=token, salt=pw_salt)
        if not result['valid']:
            return render_template('landing/404.html', html_msg = "invalid token")

        identifier = result['id']
        if identifier != email:
            data = {"404_msg": "invalid email in url parameter"}
            return render_template('landing/404.html', html_msg = "invalid url parameters")

        data = {
            "title": "Cambio de Contraseña", 
            "description": "Formulario para el cambio de contraseña", 
            "email": identifier
        }

        return render_template(
            'validations/pw-update-form.html', 
            meta=data, 
            url_token = token, 
            user_email = identifier
        )

    pw = request.form.get('password')
    repw = request.form.get('re-password')
    token = request.form.get('url_token')
    validate_pw(pw, is_api = False)

    if pw != repw:
        return render_template('landing/404.html', html_msg = "passwords are different")

    result = validate_url_token(token=token, salt=pw_salt)
    if not result['valid']:
        return render_template('landing/404.html', html_msg = "token not valid")

    q_user = get_user(result['id']) #result['id] = user email
    if q_user is None:
        return render_template('landing/404.html', html_msg = "user not found")

    try:
        q_user.password = pw
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        return render_template('landing/404.html', html_msg = e.orig.args[0])

    data = {
        "title": "Cambio de Contraseña", 
        "description": "Pagina de resultado del cambio de contraseña", 
    }
    return render_template('validations/pw-updated.html', meta=data)