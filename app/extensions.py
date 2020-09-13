from flask_assets import Environment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .utils.assets import bundles

assets = Environment()
assets.register(bundles)

db = SQLAlchemy()
migrate = Migrate()