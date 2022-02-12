import os
from flask import Flask
#blueprints
from app.blueprints.api_v1 import (
    auth, profile, maintenance
)

#extensions
from app.extensions import (
    assets, migrate, jwt, db, cors
)

#utils
from app.utils.exceptions import (
    APIException
)
from app.utils.helpers import JSONResponse

#models
from app.models.global_models import (TokenBlacklist)


def create_app(test_config=None):
    ''' Application-Factory Pattern '''
    app = Flask(__name__)
    if test_config == None:
        app.config.from_object(os.environ['APP_SETTINGS'])
    
    app.register_error_handler(404, handle_not_found)
    app.register_error_handler(405, handle_not_allowed)
    app.register_error_handler(500, handle_internal_error)
    app.register_error_handler(APIException, handle_API_Exception)
    # app.before_request(handle_before_rq)
        
    #extensions
    assets.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})


    #API BLUEPRINTS
    app.register_blueprint(auth.auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(profile.profile_bp, url_prefix='/api/v1/profile')
    app.register_blueprint(maintenance.admin_bp, url_prefix='/api/v1/maintenance')

    return app


def handle_not_found(e):
    ''' Función que permite devolver 404 en json para solicitud de 
    API
    '''
    resp = JSONResponse(message=str(e), app_status='error', status_code=404)
    return resp.to_json()


def handle_not_allowed(e):
    ''' Función que permite devolver 405 en json para solicitud de 
    API  '''
    resp = JSONResponse(message=str(e), app_status='error', status_code=405)
    return resp.to_json()


def handle_internal_error(e):
    ''' Función que permite devolver 405 en json para solicitud de 
    API  '''
    resp = JSONResponse(message=str(e), app_status='error', status_code = 500)
    return resp.to_json()


def handle_API_Exception(exception): #exception == APIException
    return exception.to_json()


#callbacks
@jwt.token_in_blocklist_loader #check if a token is stored in the blocklist db.
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']

    if jwt_payload.get('verification_token') is True:
        return False #verification token will not be stored in database.

    token = TokenBlacklist.query.filter_by(jti=jti).first()
    if token is None:
        return True
    else:
        return token.revoked


@jwt.revoked_token_loader
@jwt.expired_token_loader
def expired_token_msg(jwt_header, jwt_payload):
    rsp = JSONResponse(
        message="token has been revoked or has expired",
        app_status="error",
        payload={"invalid": "jwt"}
    )
    return rsp.to_json()


@jwt.invalid_token_loader
def invalid_token_msg(error):
    rsp = JSONResponse(
        message=error,
        app_status="error",
        payload={"invalid": "jtw"}
    )
    return rsp.to_json()


@jwt.unauthorized_loader
def missing_token_msg(error):
    rsp = JSONResponse(
        message=error,
        app_status="error",
        payload={"invalid": "jwt"}
    )
    return rsp.to_json()