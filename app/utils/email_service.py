import requests
import os, json
from requests.exceptions import (
    ConnectionError, HTTPError
)
from flask import (
    render_template, url_for
)
from app.utils.token_factory import (
    create_url_token
)
from app.utils.exceptions import APIException

# constantes para la configuracion del correo
smtp_api_url = os.environ['SMTP_API_URL']
api_key = os.environ['SMTP_API_KEY']
mail_mode = os.environ['MAIL_MODE']
email_salt = os.environ['EMAIL_VALID_SALT']
pw_salt = os.environ['PW_VALID_SALT']
main_frontend_url = os.environ['MAIN_FRONTEND_URL']

default_sender = {"name": "Luis from MyApp", "email": "luis.lucena89@gmail.com"}
default_recipients = [{"name": "Luis Alejandro", "email": "luis.multicaja@gmail.com"}]
default_content = "<!DOCTYPE html><html><body><h1>Email de prueba</h1><p>development mode</p></body></html>"
headers = {
    "Accept": "application/json",
    "Content-type": "application/json",
    "api-key": api_key
}

def smtp_api_request(data:dict, debug:dict) -> dict:
    if mail_mode == "development":
        print(json.dumps(debug))
        return {"status_code": 200, "msg": "success", "sent": True}

    try:
        r = requests.post(headers=headers, json=data, url=smtp_api_url, timeout=3)
        r.raise_for_status()
        return {"status_code": r.status_code, "msg":r.json(), "sent": True}

    except ConnectionError:
        return {"msg": "connection error to smtp server", "sent": False}

    except HTTPError:
        return {"msg": r.json(), "sent": False}

def send_transactional_email(params:dict={}, recipients:list=None, sender:dict=None, subject:str=None) -> dict:
    '''
    función para enviar a través de una solicitud http a la api del servidor smtp un correo
    electrónico transaccional. Estos son los parámetros requeridos:

    - params:{
        {"html_content": html_code} -> contenido html a enviar
        {"templateID": ID} -> id del template a enviar desde el servidor smtp
        {"template_params": {params}} -> parámetros para completar el template en el servidor.
    }

    - recipients:list -> lista con todos los destinatarios del correo electrónico: 
        [{"name":string, "email": valid-email-format}, ...]

    - sender:dict -> diccionario con los datos del usuario que envía el correo.
        {"name": str, "email": valid-email-format}
    
    - subject: str -> Asunto del correo electrónico.

    '''

    data = {
        "sender": default_sender if sender is None else sender,
        "to": default_recipients if recipients is None else recipients,
        "subject": "Correo de prueba" if subject is None else subject,
        "htmlContent": default_content if params.get("html_content") is None else params['html_content']
    }
    if params.get("templateID") is not None:
        data["templateID"] = params['templateID']
        data["params"] = "null" if params.get("template_params") is None else params['template_params']

    return smtp_api_request(data)


def send_validation_mail(user:dict=None):
    '''
    función para enviar a través de una solicitud http a la api del servidor smtp un correo
    electrónico de validacion. Estos son los parámetros requeridos:

    - email: Correo electronico que debe ser validado por el usuario.

    '''
    name = user.get('name')
    email = user.get('email')

    if name is None or email is None:
        return {"status_code": 400, "msg": "bad request", "sent": False}

    token = create_url_token(identifier=email, salt=email_salt)
    url_params = f"?email={email}&token={token}"
    validation_url = main_frontend_url + url_for('validations_bp.email_validation') + url_params

    data = {
        "sender": default_sender,
        "to": [{ "name": name, "email": email }],
        "subject": "Valida tu correo electronico",
        "htmlContent": render_template("mail/user-validation.html", params = {"link":validation_url})
    }
    rsp = smtp_api_request(data=data, debug={"link": validation_url})
    if not rsp['sent']:
        raise APIException("fail on sending validation email to user, msg: '{}'".format(rsp['msg']), status_code=503)

    pass


def send_pwchange_mail(user:dict=None):
    '''
    función para enviar a través de una solicitud http a la api del servidor smtp un correo
    electrónico de validacion. Estos son los parámetros requeridos:

    - email: Correo electronico que debe ser validado por el usuario.

    '''
    name = user.get('name')
    email = user.get('email')

    if name is None or email is None:
        return {"status_code": 400, "msg": "bad request", "sent": False}

    token = create_url_token(identifier=email, salt=pw_salt)
    url_params = "?email={}&token={}".format(email, token)
    validation_url = main_frontend_url + url_for('validations_bp.pw_reset') + url_params

    data = {
        "sender": default_sender,
        "to": [{ "name": name, "email": email }],
        "subject": "Reestablece tu contraseña",
        "htmlContent": render_template("mail/password-reset.html", params = {"link":validation_url}),
    }

    rsp = smtp_api_request(data=data, debug={"link":validation_url})
    if not rsp['sent']:
        raise APIException("fail on sending validation email to user, msg: '{}'".format(rsp['msg']), status_code=503)

    pass
