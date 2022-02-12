from datetime import datetime
from flask_jwt_extended import decode_token

from app.extensions import db
from app.models.main import (
    User
)
# from app.models.global_models import (
#     TokenBlacklist
# )
from flask import jsonify


def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc)


def get_user_by_email(email):
    '''
    Helper function to get user from db, email parameter is required
    '''
    user = User.query.filter_by(email=email).first()
    return user


def normalize_names(name: str, spaces=False) -> str:
    """Normaliza una cadena de caracteres a palabras con Mayúsculas y sin/con espacios.
    Args:
        name (str): Cadena de caracteres a normalizar.
        spaces (bool, optional): Indica si la cadena de caracteres incluye o no espacios. 
        Defaults to False.
    Returns:
        str: Candena de caracteres normalizada.
    """
    if not isinstance(name, str):
        raise TypeError("Invalid name argument, string is expected")
    if not isinstance(spaces, bool):
        raise TypeError("Invalid spaces argunment, bool is expected")

    if not spaces:
        return name.replace(" ", "").capitalize()
    else:
        return name.strip().title()


class JSONResponse():

    '''
    Class
    Genera mensaje de respuesta a las solicitudes JSON. los parametros son:

    - message: Mesanje a mostrar al usuario.
    - app_status = "success", "error"
    - status_code = http status code
    - payload = dict con cualquier informacion que se necesite enviar al usuario.

    methods:

    - serialize() -> return dict
    - to_json() -> http JSON response

    '''

    def __init__(self, message, app_status="success", status_code=200, payload=None):
        self.app_status = app_status
        self.status_code = status_code
        self.data = payload
        self.message = message

    def serialize(self):
        rv = {
            "result": self.app_status,
            "data": dict(self.data or ()),
            "message": self.message
        }
        return rv

    def to_json(self):
        return jsonify(self.serialize()), self.status_code