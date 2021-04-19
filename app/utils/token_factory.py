import os
from re import sub
import uuid
from itsdangerous import (
    URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
)

serializer = URLSafeTimedSerializer(os.environ['SECRET_KEY'])


def create_url_token(user_email:str, salt:str) -> dict:
    '''
    Función para crear un token y un recurso temporal para enviar al usuario y realizar validaciones

    Args:
    - user_email: email del usuario que necesita ser validado
    - salt: identificador del parámetro que está siendo encriptado

    Return:
    - dict with token and resource_url to access validation in the frontend
        {"token":url_token, "resource": temp_resource_url}
    '''
    
    token =  serializer.dumps(user_email, salt=salt)
    resource = uuid.uuid4().hex
    return {"token": token, "resource": resource}


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
    except (SignatureExpired, BadTimeSignature):
        return {"valid": False, "msg": "invalid url token"}
    
    return {"valid": True, "id": identity, "msg": "valid url token"}


