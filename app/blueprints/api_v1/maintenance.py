from flask import Blueprint, jsonify, request
from datetime import datetime
from app.extensions import db
from app.models.global_models import TokenBlacklist
from app.utils.decorators import (
    json_required
)
from app.utils.helpers import JSONResponse


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

    response = JSONResponse("db pruned correctly")
    return response.to_json()