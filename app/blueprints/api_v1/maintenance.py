from flask import Blueprint, jsonify, request
from datetime import datetime
from app.extensions import db
from app.models.global_models import TokenBlacklist
from app.models.main import Location


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


@admin_bp.route('/get-locations-tree', methods=['GET'])
def locations_tree():
    location_id = str(request.args.get('location'))
    location = Location.query.get(location_id)

    return jsonify(location.serialize_tree()), 200
