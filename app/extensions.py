from flask_assets import Environment
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from .utils.assets import bundles

assets = Environment()
assets.register(bundles)

migrate = Migrate()

db = SQLAlchemy()

jwt = JWTManager()