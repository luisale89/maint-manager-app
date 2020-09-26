from flask_assets import Environment
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from .utils.assets import bundles

assets = Environment()
assets.register(bundles)

migrate = Migrate()

jwt = JWTManager()