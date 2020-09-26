import os
from flask import Flask

from .blueprints.landing import landing
from .blueprints.api import auth, profile

from .extensions import assets, migrate, jwt, db

def create_app(test_config=None):
    ''' Application-Factory Pattern '''
    app = Flask(__name__)
    if test_config == None:
        app.config.from_object(os.environ['APP_SETTINGS'])

    assets.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(landing.bp)
    app.register_blueprint(auth.auth)
    app.register_blueprint(profile.profile)

    return app