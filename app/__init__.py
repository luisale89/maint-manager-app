import os
from flask import Flask, jsonify, request, render_template
from app.blueprints import api_v1

from app.blueprints.api_v1 import (
    auth, profile, maintenance
)

from app.blueprints.landing import (
    landing, validations
)

from app.blueprints.db_amin.db_admin import db_admin_bp #!development only

from app.extensions import (
    assets, migrate, jwt, db, cors, admin
)

def handle_not_found(e):
    ''' Función que permite devolver 404 en json para solicitud de 
    API y html para solicitud desde un navegador web '''
    if request.path.startswith('/api'):
        return jsonify(error=str(e)), 404
    else:
        return render_template('landing/404.html'), 404

def handle_not_allowed(e):
    ''' Función que permite devolver 405 en json para solicitud de 
    API y html para solicitud desde un navegador web '''
    if request.path.startswith('/api'):
        return jsonify(error=str(e)), 405
    else:
        return render_template('landing/404.html'), 405 #!desarrollar template para 405

def create_app(test_config=None):
    ''' Application-Factory Pattern '''
    app = Flask(__name__)
    if test_config == None:
        app.config.from_object(os.environ['APP_SETTINGS'])
    
    app.register_error_handler(404, handle_not_found)
    app.register_error_handler(405, handle_not_allowed)
        
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