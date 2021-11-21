from flask import Blueprint
from app.extensions import (
    db, admin
)
from flask_admin.contrib.sqla import ModelView

from app.models.main import (
    User, Company, SparePart, MaintenanceActivity, Asset
)
from app.models.associations import (
    CompanyUser, AssetSparePart
)

from app.models.global_models import (
    Category
)

db_admin_bp = Blueprint('db_admin_bp', __name__)

admin.add_view(ModelView(CompanyUser, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Company, db.session))
admin.add_view(ModelView(SparePart, db.session))
admin.add_view(ModelView(Asset, db.session))
admin.add_view(ModelView(MaintenanceActivity, db.session))
admin.add_view(ModelView(AssetSparePart, db.session))
admin.add_view(ModelView(Category, db.session))