from datetime import datetime
import re

from flask_jwt_extended import decode_token

from app.extensions import db
from app.models.users import TokenBlacklist

def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc)


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
    if not spaces:
        return name.replace(" ", "").capitalize()
    else:
        return name.strip().title()


def valid_email(email: str) -> bool:
    """Valida si una cadena de caracteres tiene un formato de correo electronico válido
    Args:
        email (str): email a validar
    Returns:
        bool: indica si el email es válido (True) o inválido (False)
    """
    #Regular expression that checks a valid email
    ereg = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return bool(re.search(ereg, email))


def valid_password(password: str) -> bool:
    """Verifica si una contraseña cumple con los parámetros minimos de seguridad
    definidos para esta aplicación.
    Args:
        password (str): contraseña a validar.
    Returns:
        bool: resultado de la validación.
    """
    #Regular expression that checks a secure password
    preg = preg = '^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$'
    return bool(re.search(preg, password))


def only_letters(string: str, spaces=False) -> bool:
    """Funcion que valida si un String contiene solo letras
    Se incluyen letras con acentos, ñ. Se excluyen caracteres especiales
    y numeros.
    Args:
        string (str): cadena de caracteres a evaluar.
        spaces (bool, optional): Define si la cadena de caracteres lleva o no espacios en blanco. 
        Defaults to False.
    Returns:
        bool: Respuesta de la validación.
    """
    #regular expression that checks only letters string
    sreg = '^[a-zA-ZñáéíóúÑÁÉÍÓÚ]*$'
    #regular expression that check letters and spaces in a string
    sregs = '^[a-zA-Z ñáéíóúÑÁÉÍÓÚ]*$'
    if string == '' or not isinstance(string, str):
        return False
    if not spaces:
        return bool(re.search(sreg, string))
    else:
        return bool(re.search(sregs, string))
