from flask import Blueprint
from app.extensions import (
    db, admin
)
from flask_admin.contrib.sqla import ModelView
from app.models import (
    User, Suscriptor, Country
)

bp = Blueprint('admin_bp', __name__)

admin.add_view(ModelView(User, db.session, category="user"))
admin.add_view(ModelView(Suscriptor, db.session, category="user"))
admin.add_view(ModelView(Country, db.session))