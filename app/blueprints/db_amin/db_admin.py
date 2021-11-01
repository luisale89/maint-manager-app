from flask import Blueprint
from app.extensions import (
    db, admin
)
from flask_admin.contrib.sqla import ModelView

from app.models.main import (
    User, Company, Spare, MaintenanceActivity, Asset
)
from app.models.associations import (
    WorkRelation, AssocActivityAsset, AssocSpareAsset
)

db_admin_bp = Blueprint('db_admin_bp', __name__)

# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(WorkRelation, db.session))
admin.add_view(ModelView(Company, db.session))
admin.add_view(ModelView(Spare, db.session))
admin.add_view(ModelView(Asset, db.session))
admin.add_view(ModelView(MaintenanceActivity, db.session))
admin.add_view(ModelView(AssocSpareAsset, db.session))
admin.add_view(ModelView(AssocActivityAsset, db.session))