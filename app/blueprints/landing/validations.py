
from flask.helpers import url_for
from app.utils.helpers import (
    valid_email, valid_password
)
from flask import (
    Blueprint, render_template, request, redirect
)
from app.utils.token_factory import validate_url_token
from app.extensions import db
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

    if not valid_email(email):
        return render_template('landing/404.html')

    result = validate_url_token(token=token, salt=email_salt)
    if not result['valid']:
        return render_template('landing/404.html')

    identifier = result['id']
    try:
        user = User.query.filter_by(email=identifier).first()
        user.email_confirm = True
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

        if not valid_email(email):
            return render_template('landing/404.html')

        result = validate_url_token(token=token, salt=pw_salt)
        if not result['valid']:
            return render_template('landing/404.html')

        identifier = result['id']

        data = {
            "title": "Cambio de Contraseña", 
            "description": "Formulario para el cambio de contraseña", 
            "email": identifier
        }

        return render_template('validations/pw-update-form.html', meta=data)

    pw = request.form.get('password')
    re_pw = request.form.get('re-password')

    if not valid_password(pw) or pw != re_pw:
        return redirect(url_for('landing_bp.pw_reset'))

    data = {
        "title": "Cambio de Contraseña", 
        "description": "Pagina de resultado del cambio de contraseña", 
    }
    return render_template('validations/pw-updated.html', meta=data)