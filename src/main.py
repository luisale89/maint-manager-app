import os
from flask import Flask
from flask_assets import Environment
from blueprints import landing, api
from utils import rules


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
assets = Environment(app)
assets.register(rules.bundles)


app.register_blueprint(landing.bp)
app.add_url_rule('/', endpoint='index')
app.register_blueprint(api.bp)


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT, debug=False)