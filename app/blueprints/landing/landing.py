
from flask import (
    Blueprint, render_template
)

landing_bp = Blueprint('landing_bp', __name__)

@landing_bp.route('/')
def index():
    context = {
        "title": "Inicio",
        "description": "inicio de la app"
    }
    return render_template('landing/home.html', **context)
