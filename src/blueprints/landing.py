from flask import Blueprint, url_for, render_template

bp = Blueprint('landing', __name__)

@bp.route('/')
def index():
    metadata={"title": "inicio", "description": "descripción de la página en general"}
    return render_template('landing/home.html', meta=metadata)

