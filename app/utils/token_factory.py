import os
from itsdangerous import (
    URLSafeTimedSerializer, BadData
)

serializer = URLSafeTimedSerializer(os.environ['SECRET_KEY'])


def create_url_token(user_email:str, salt:str) -> dict:
    '''
    Función para crear un token y un recurso temporal para enviar al usuario y realizar validaciones

    Args:
    - user_email: email del usuario que necesita ser validado
    - salt: identificador del parámetro que está siendo encriptado

    Return:
    - token: str
    '''
    
    token =  serializer.dumps(user_email, salt=salt)
    return token


def validate_url_token(token:str, salt:str) -> dict:
    '''
    Función para validar un url_token

    Args:
    - token: url_token que necesita ser validado
    - salt: identificador del parámetro que está siendo validado

    Return:
    - dict with validation results -> {"valid":bool, "id":token_id, "msg": str}
    '''
    try:
        identity = serializer.loads(token, salt=salt, max_age=600) #token lives for 10 minutes
    except BadData as e:
        return {"valid": False, "msg": e.message}
    
    return {"valid": True, "id": identity}


