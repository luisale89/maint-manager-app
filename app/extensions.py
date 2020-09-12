from flask_assets import Environment
from .utils.rules import bundles

assets = Environment()
assets.register(bundles)
