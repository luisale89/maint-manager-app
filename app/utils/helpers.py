from datetime import datetime
from flask_jwt_extended import decode_token

from app.extensions import db
from app.models.users import (
    TokenBlacklist, User
)
from flask import jsonify

def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc)


def get_user(email):
    '''
    Helper function to get user from db, email parameter is required
    '''
    user = User.query.filter_by(email=email).first()
    return user


def revoke_all_jwt(user_identity:str):
    '''
    Revoke all tokens of an user. Usefull to logout everywhere.
    params:
    user_identity:str
    '''
    tokens = TokenBlacklist.query.filter_by(user_identity=user_identity, revoked=False).all()
    for token in tokens:
        token.revoked = True
        token.revoked_date = datetime.utcnow()
    db.session.commit()

    pass


def add_token_to_database(encoded_token):
    """
    Adds a new token to the database. It is not revoked when it is added.
    :param encoded JWT
    """
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    user_identity = decoded_token['sub']
    expires = _epoch_utc_to_datetime(decoded_token['exp'])
    revoked = False

    db_token = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_identity=user_identity,
        expires=expires,
        revoked=revoked,
    )
    db.session.add(db_token)
    db.session.commit()


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

    def __init__(self, message, app_status="success", payload=None):
        self.app_status = app_status
        self.data = payload
        self.message = message

    def serialize(self):
        rv = {
            "status": self.app_status,
            "data": dict(self.data or ()),
            "message": self.message
        }
        return rv