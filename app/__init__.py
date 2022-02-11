import os
from flask import Flask, jsonify, request, render_template, flash
#blueprints
from app.blueprints.api_v1 import (
    auth, profile, maintenance
)
from app.blueprints.landing import (
    landing, validations
)
from app.blueprints.db_amin.db_admin import db_admin_bp #!development only

#extensions
from app.extensions import (
    assets, migrate, jwt, db, cors, admin
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
    app.register_error_handler(APIException, handle_API_Exception)
        
    #extensions
    assets.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    admin.init_app(app)

    #blueprints
    app.register_blueprint(landing.landing_bp)
    app.register_blueprint(validations.validations_bp, url_prefix='/validations')
    app.register_blueprint(db_admin_bp, url_prefix='/administer') #development only
    #API BLUEPRINTS
    app.register_blueprint(auth.auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(profile.profile_bp, url_prefix='/api/v1/profile')
    app.register_blueprint(maintenance.admin_bp, url_prefix='/api/v1/maintenance')

    return app


def handle_not_found(e):
    ''' Función que permite devolver 404 en json para solicitud de 
    API y html para solicitud desde un navegador web '''
    if request.path.startswith("/api"):
        return jsonify(error=str(e)), 404
    else:
        flash(str(e))
        return render_template('landing/404.html'), 404

def handle_not_allowed(e):
    ''' Función que permite devolver 405 en json para solicitud de 
    API y html para solicitud desde un navegador web '''
    if request.path.startswith("/api"):
        return jsonify(error=str(e)), 405
    else:
        flash(str(e))
        return render_template('landing/404.html'), 405 #!desarrollar template para 405

def handle_API_Exception(exception):
    # return jsonify(error.to_dict()), error.status_code
    return exception.to_json()


#callbacks
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
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
        payload={"invalid": "token revoked"}
    )
    return jsonify(rsp.serialize()), 403

@jwt.invalid_token_loader
def invalid_token_msg(error):
    rsp = JSONResponse(
        message=error,
        app_status="error",
        payload={"invalid": ["jwt"]}
    )
    return jsonify(rsp.serialize()), 400

@jwt.unauthorized_loader
def missing_token_msg(error):
    rsp = JSONResponse(
        message=error,
        app_status="error",
        payload={"missing": ["jwt"]}
    )
    return jsonify(rsp.serialize()), 400