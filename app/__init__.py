import os
from flask import Flask

from .blueprints.landing import landing
from .blueprints.api.v01 import (
    auth, profile, preset
)

from app.extensions import (
    assets, migrate, jwt, db, cors
)

def create_app(test_config=None):
    ''' Application-Factory Pattern '''
    app = Flask(__name__)
    if test_config == None:
        app.config.from_object(os.environ['APP_SETTINGS'])

    #extensions
    assets.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    #blueprints
    app.register_blueprint(landing.bp)
    app.register_blueprint(auth.auth)
    app.register_blueprint(profile.profile)
    app.register_blueprint(preset.preset)

    return app