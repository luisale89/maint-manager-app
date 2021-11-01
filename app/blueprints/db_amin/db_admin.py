from flask import Blueprint
from app.extensions import (
    db, admin
)
from flask_admin.contrib.sqla import ModelView

from app.models.main import (
    User, WorkOrder, Provider, Company, Spare
)
from app.models.associations import (
    WorkRelation, AssocProviderWorkorder, AssocProviderSpare
)
from app.models.global_models import (
    Category
)

db_admin_bp = Blueprint('db_admin_bp', __name__)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(WorkRelation, db.session))
# admin.add_view(ModelView(AssocProviderWorkorder, db.session))
# admin.add_view(ModelView(AssocProviderSpare, db.session))
# admin.add_view(ModelView(WorkOrder, db.session))
# admin.add_view(ModelView(Provider, db.session))
admin.add_view(ModelView(Company, db.session))
# admin.add_view(ModelView(Spare, db.session))
admin.add_view(ModelView(Category, db.session))