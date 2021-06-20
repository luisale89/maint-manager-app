from app.utils.exceptions import APIException
from app.utils.helpers import resp_msg
import re

def validate_email(email: str):
    """Valida si una cadena de caracteres tiene un formato de correo electronico válido
    Args:
        email (str): email a validar
    Returns:
        Exception APIException if email is not valid
        pass if email is valid.
    """
    if not isinstance(email, str):
        raise TypeError("Invalid argument format, str is espected")

    if len(email) > 320:
        raise APIException("invalid email lenght, {} length was passed".format(len(email)))

    #Regular expression that checks a valid email
    ereg = '^[\w]+[\._]?[\w]+[@]\w+[.]\w{2,3}$'

    if not re.search(ereg, email):
        raise APIException(resp_msg.invalid_format('email', email))
    pass


def validate_pw(password: str):
    """Verifica si una contraseña cumple con los parámetros minimos de seguridad
    definidos para esta aplicación.
    Args:
        password (str): contraseña a validar.
    Returns:
        bool: resultado de la validación.
    """
    if not isinstance(password, str):
        raise TypeError("Invalid argument format, str is espected")
    #Regular expression that checks a secure password
    preg = '^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$'
    if not re.search(preg, password):
        raise APIException(resp_msg.invalid_pw())
    pass


def only_letters(string: str, spaces=False):
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
        raise TypeError("Invalid argument format, str is espected")
    if not isinstance(spaces, bool):
        raise TypeError("Invalid argument format, bool is espected")
    
    if spaces:
        if not re.search(sregs, string):
            raise APIException("Only letter is valid in str, {} was passed".format(string))
    else: 
        if not re.search(sreg, string):
            raise APIException("Only letter and no spaces is valid in str, {} was passed".format(string))

    pass


def in_request(request: dict, contains: tuple) -> dict:
    '''
    Función para validar que un request contiene todos los 
    elementos necesarios para completar la solicitud del usuario

    Args:
        * request: dict que contiene todos los elementos enviados por el usuario al endpoint.
        * contains: tuple que contiene el listado de elmentos que debe existir dentro de request
        para poder completar correctamente la solicitud del usuario.

    Returns:
        dict que contiene la siguiente información:
        resp: {'complete': bool, missing: list} => list == lista elementos faltantes en request

    '''
    missing = list()
    complete = False
    if not isinstance(request, dict) or not isinstance(contains, tuple):
        raise TypeError("invalid arguments passed")
    
    for item in contains:
        if request.get(item) is None:
            missing.append(item)
    if len(missing) == 0:
        complete = True
    
    return {'complete': complete, 'missing': missing}