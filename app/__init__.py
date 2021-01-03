import os
from flask import Flask, jsonify, request, render_template

from .blueprints.api.v1a import (
    auth, profile
)
from .blueprints.admin import (
    admin_bp
)

from .blueprints.landing import landing

from app.extensions import (
    assets, migrate, jwt, db, cors, admin
)

def handle_api_error(e):
    if request.path.startswith('/api/'):
        return jsonify(error=str(e)), 404
    else:
        return render_template('404.html')

def create_app(test_config=None):
    ''' Application-Factory Pattern '''
    app = Flask(__name__)
    if test_config == None:
        app.config.from_object(os.environ['APP_SETTINGS'])
        app.register_error_handler(404, handle_api_error)
        

    #extensions
    assets.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    admin.init_app(app)

    #blueprints
    app.register_blueprint(landing.bp)
    app.register_blueprint(auth.auth)
    app.register_blueprint(profile.profile)
    app.register_blueprint(admin_bp.bp)

    return app