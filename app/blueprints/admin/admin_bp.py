from flask import Blueprint
from app.extensions import (
    db, admin
)
from flask_admin.contrib.sqla import ModelView
from app.models import (
    User, TokenBlacklist
)

bp = Blueprint('admin_bp', __name__)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(TokenBlacklist, db.session))