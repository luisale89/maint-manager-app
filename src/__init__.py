import os
from flask import Flask

from .blueprints import landing, api

from .extensions import assets

def create_app(test_config=None):
    app = Flask(__name__)
    if test_config == None:
        app.config.from_object(os.environ['APP_SETTINGS'])

    assets.init_app(app)

    app.register_blueprint(landing.bp)
    app.register_blueprint(api.bp)

    return app