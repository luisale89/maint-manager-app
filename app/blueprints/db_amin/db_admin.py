from flask import Blueprint
from flask_sqlalchemy.model import Model
from app.extensions import (
    db, admin
)
from flask_admin.contrib.sqla import ModelView
from app.models.users import (
    User, TokenBlacklist, Company, HumanResources
)

db_admin_bp = Blueprint('db_admin_bp', __name__)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(TokenBlacklist, db.session))
admin.add_view(ModelView(Company, db.session))
admin.add_view(ModelView(HumanResources, db.session))