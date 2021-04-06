from flask import Blueprint, request, jsonify
from datetime import datetime
from app.extensions import db
from app.models.users import TokenBlacklist
# from flask_jwt_extended import (
#     create_access_token, jwt_required, 
#     get_jwt_identity, decode_token
# )


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