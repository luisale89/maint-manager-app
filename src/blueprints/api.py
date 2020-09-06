from flask import Blueprint, url_for, jsonify

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/', methods=['GET'])
def api():
    return jsonify({'hola':'mundo'}), 200