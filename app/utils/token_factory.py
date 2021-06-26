import os
from itsdangerous import (
    URLSafeTimedSerializer, BadData
)

serializer = URLSafeTimedSerializer(os.environ['SECRET_KEY'])


def create_url_token(identifier:str, salt:str) -> dict:
    '''
    Función para crear un token y un recurso temporal para enviar al usuario y realizar validaciones

    Args:
    - identifier: email del usuario que necesita ser validado
    - salt: identificador del parámetro que está siendo encriptado

    Return:
    - token: str
    '''

    if identifier is None:
        raise ValueError("identifier parameter is missing")
    if salt is None:
        raise ValueError("salt parameter is missing")
    
    token =  serializer.dumps(identifier, salt=salt)
    return token


def validate_url_token(token:str, salt:str, identifier:str=None, age:int=600) -> dict:
    '''
    Función para validar un url_token

    Args:
    - token: url_token que necesita ser validado
    - salt: identificador del parámetro que está siendo validado
    - identifier: identificador del usuario, generalmente es el correo electronico.
    - age: Time in seconds in wich the token is valid. (10minutes by default)

    Return:
    - dict with validation results -> {"valid":bool, "id":token_id, "msg": str}
    '''
    if identifier is None:
        raise ValueError("identifier parameter is missing")
    if salt is None:
        raise ValueError("salt parameter is missing")
    if token is None:
        raise ValueError("token parameter is missing")

    try:
        identity = serializer.loads(token, salt=salt, max_age=age)
    except BadData as e:
        return {"valid": False, "msg": e.message}
    
    if identity != identifier:
        return {"valid": False, "msg": "invalid email in url_token"}

    return {"valid": True, "id": identity}