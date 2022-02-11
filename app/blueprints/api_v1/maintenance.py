from flask import Blueprint, jsonify, request
from datetime import datetime
from app.extensions import db
from app.models.global_models import TokenBlacklist
from app.models.main import Location
from app.utils.decorators import (
    json_required
)


admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.route('/prune-db', methods=['GET'])
def prune_db():
    """LIMPIAR TOKENS VENCIDOS - ADMIN ENDPOINT
    Returns:
        json: success msg.
    """
    now = datetime.now()
    expired = TokenBlacklist.query.filter(TokenBlacklist.expires < now).all()
    for token in expired:
        db.session.delete(token)
    db.session.commit()
    return jsonify({"success": "db pruned correctly"}), 200

#!TEST
@admin_bp.route('/get-locations', methods=['GET'])
@json_required()
def locations_tree():
    location_id = str(request.args.get('location'))
    location = Location.query.get(location_id)

    return jsonify({**location.serialize(), **location.serialize_children()}), 200


# @admin_bp.route('/create-location', methods=['POST'])
# @json_required()
# def create_location():
#     body = request.get_json(silent=True)
