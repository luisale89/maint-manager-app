
from flask import Blueprint, url_for, jsonify, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from ...extensions import db
from ...models import (
    Country
)
from ...utils.exceptions import APIException
from ...utils.helpers import normalize_names

admin = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@admin.route('/country', methods=['GET'])
@jwt_required
def all_countries():
    countries = Country.query.all()
    