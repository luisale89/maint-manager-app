import re
from app.utils.exceptions import APIException

def validate_email(email: str) -> dict:
    """Valida si una cadena de caracteres tiene un formato de correo electronico válido
    Args:
        email (str): email a validar
    Returns:
        Exception APIException if email is not valid
        pass if email is valid.
    """
    if not isinstance(email, str):
        raise TypeError("Invalid argument format, str is expected")

    if len(email) > 320:
        # raise APIException("invalid email lenght, {} length was passed".format(len(email)))
        return {"error": True, "msg": "invalid email length, max is 320 chars"}

    #Regular expression that checks a valid email
    ereg = '^[\w]+[\._]?[\w]+[@]\w+[.]\w{2,3}$'

    if not re.search(ereg, email):
        # raise APIException(api_responses.invalid_format('email', email))
        return {"error":True, "msg": "invalid email format"}
    
    return {"error": False}


def validate_pw(password: str) -> dict:
    """Verifica si una contraseña cumple con los parámetros minimos de seguridad
    definidos para esta aplicación.
    Args:
        password (str): contraseña a validar.
    Returns:
        bool: resultado de la validación.
    """
    if not isinstance(password, str):
        raise TypeError("Invalid argument format, str is expected")
    #Regular expression that checks a secure password
    preg = '^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$'
    # if not re.search(preg, password):
    #     if is_api:
    #         raise APIException(api_responses.invalid_pw())
    #     else:
    #         return True
    # pass
    if not re.search(preg, password):
        return {"error": True, "msg": "password is insecure"}

    return {"error": False}


def only_letters(string: str, spaces=False) -> dict:
    """Funcion que valida si un String contiene solo letras
    Se incluyen letras con acentos, ñ. Se excluyen caracteres especiales
    y numeros.
    Args:
        * string (str): cadena de caracteres a evaluar.
        * spaces (bool, optional): Define si la cadena de caracteres lleva o no espacios en blanco. 
        Defaults to False.
    Returns:
        *bool: Respuesta de la validación.
    """
    #regular expression that checks only letters string
    sreg = '^[a-zA-ZñáéíóúÑÁÉÍÓÚ]*$'
    #regular expression that check letters and spaces in a string
    sregs = '^[a-zA-Z ñáéíóúÑÁÉÍÓÚ]*$'
    if not isinstance(string, str):
        raise TypeError("Invalid argument format, str is expected")
    if not isinstance(spaces, bool):
        raise TypeError("Invalid argument format, bool is expected")
    
    if spaces:
        if not re.search(sregs, string):
            # raise APIException("Only letter is valid in str, {} was passed".format(string))
            return {"error": True, "msg": "String must be only letters"}
    else: 
        if not re.search(sreg, string):
            # raise APIException("Only letter and no spaces is valid in str, {} was passed".format(string))
            return {"error": True, "msg": "String must be only letters and no spaces"}
    return {"error": False}


def check_validations(valid:dict):
    '''function para validar que no existe errores en el diccionario "valid"'''
    error = []
    msg = {}
    if not isinstance(valid, dict):
        raise TypeError("Invalid argument format, dict is expected")
    for r in valid.keys():
        if valid[r]['error']: 
            error.append(r)
            msg[r] = valid[r]['msg']

    if error:
        raise APIException("invalid inputs format", payload={'invalid': error, 'msg': msg})

    pass