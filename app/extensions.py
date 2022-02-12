from flask_assets import Environment
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# from flask_admin import Admin

from .utils.assets import bundles

assets = Environment()
assets.register(bundles)

migrate = Migrate()
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
# admin = Admin(name="auth-uService", template_mode="bootstrap4")