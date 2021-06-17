
from flask import (
    Blueprint, render_template
)

landing_bp = Blueprint('landing_bp', __name__)

@landing_bp.route('/')
def index():
    metadata={"title": "inicio", "description": "descripción de la página en general"}
    return render_template('landing/home.html', meta=metadata)
