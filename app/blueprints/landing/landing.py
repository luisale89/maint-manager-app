from app.utils.helpers import valid_email
from flask import Blueprint, render_template, request
from app.utils.token_factory import validate_url_token
from app.extensions import db
from app.models.users import User
from sqlalchemy.exc import (
    IntegrityError, DataError
)
import os

email_salt = os.environ['EMAIL_VALID_SALT']
pw_salt = os.environ['PW_VALID_SALT']

landing_bp = Blueprint('landing_bp', __name__)

@landing_bp.route('/')
def index():
    metadata={"title": "inicio", "description": "descripción de la página en general"}
    return render_template('landing/home.html', meta=metadata)

# email validation endpoint
@landing_bp.route('/validations/email')
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

    metadata={"title": "email validation", "description": "validacion de correo electronico", "email": identifier}
    return render_template('validations/email-validation.html', meta=metadata)


# password reset endpoint