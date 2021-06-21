from datetime import datetime
from flask_jwt_extended import decode_token

from app.extensions import db
from app.models.users import (
    TokenBlacklist, User
)

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


class api_responses():
    '''
    Clase que contiene todos los mensajes de respuesta al usuario que se repiten con 
    mucha frecuencia en la app.
    '''
    def invalid_format(name:str='input', value:str=None, expected:str=None) -> str:
        '''
        Función que devuelve un mensaje de formato invalido de un input enviado a la app.

        Args:
        * name: nombre del input, default='input'
        * value: valor enviado por el usuario, default=None
        * expected: valor esperado por la app, default=None

        Return:
        * Devuelve string con mensaje de respuesta.

        '''
        str1 = "invalid {} format in request".format(name)
        str2 = ""
        str3 = ""
        if value is not None:
            str2 = ", {} was given".format(value)
        if expected is not None:
            str3 = ", {} is expected".format(expected)
        
        return str1+str2+str3  
    
    def invalid_pw() -> str:
        return "password does not comply with security format"

    def not_found(value="input") -> str:
        return "{} not found in app".format(value)

    def missing_args(args) -> str:
        return "missing args in request: %r" %args

    def not_json_rq() -> str:
        return "invalid json request"


