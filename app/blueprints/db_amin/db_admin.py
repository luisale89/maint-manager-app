from flask import Blueprint
from app.extensions import (
    db, admin
)
from flask_admin.contrib.sqla import ModelView

from app.models.main import (
    User, Company
)
from app.models.associations import (
    WorkRelation
)

db_admin_bp = Blueprint('db_admin_bp', __name__)

admin.add_view(ModelView(WorkRelation, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Company, db.session))