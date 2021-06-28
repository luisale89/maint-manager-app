
from flask import (
    Blueprint, render_template
)
from app.utils.decorators import (
    login_required
)

landing_bp = Blueprint('landing_bp', __name__)

@landing_bp.route('/')
def index():
    context = {
        "title": "Inicio",
        "description": "inicio de la app"
    }
    return render_template('landing/home.html', **context)


@landing_bp.route('/login')
def login():
    error = {}
    context={
        "title": "Login", 
        "description": "Formulario de inicio de sesion",
        "error": error
    }
    return render_template('landing/login.html', **context)


@landing_bp.route('/sobre-mi')
@login_required #protected view
def about():
    context={
        "title": "Sobre mi", 
        "description": "Descripcion de mi carrera profesional", 
        "active_page": "about"
    }
    return render_template('landing/about.html', **context)