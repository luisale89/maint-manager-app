from flask import Blueprint
from flask_sqlalchemy.model import Model
from app.extensions import (
    db, admin
)
from flask_admin.contrib.sqla import ModelView

from app.models.main import (
    User, Company
)
from app.models.global_models import (
    TokenBlacklist, Country, Category
)
from app.models.assosiations import (
    WorkRelation
)

db_admin_bp = Blueprint('db_admin_bp', __name__)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(TokenBlacklist, db.session))
admin.add_view(ModelView(WorkRelation, db.session))
admin.add_view(ModelView(Company, db.session))
admin.add_view(ModelView(Country, db.session))
admin.add_view(ModelView(Category, db.session))