import requests
import os
from requests.exceptions import (
    ConnectionError, HTTPError
)

smtp_server = os.environ['SMTP_API_URL']
api_key = os.environ['SMTP_API_KEY']
mail_mode = os.environ['MAIL_MODE']
default_sender = {"name": "Luis from MyApp", "email": "luis.lucena89@gmail.com"}
default_recipients = [{"name": "Luis Alejandro", "email": "luis.multicaja@gmail.com"}]
default_content = "<!DOCTYPE html><html><body><h1>Email de prueba</h1><p>development mode</p></body></html>"

headers = {
    "Accept": "application/json",
    "Content-type": "application/json",
    "api-key": api_key
}

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
    if mail_mode == "development":
        print(params['template_params'])
        return {"status_code": 200, "msg": "success", "sent": True}

    data = {
        "sender": default_sender if sender is None else sender,
        "to": default_recipients if recipients is None else recipients,
        "subject": "Correo de prueba" if subject is None else subject,
        "htmlContent": default_content if params.get("html_content") is None else params['html_content']
    }
    if params.get("templateID") is not None:
        data["templateID"] = params['templateID']
        data["params"] = "null" if params.get("template_params") is None else params['template_params']

    try:
        r = requests.post(headers=headers, json=data, url=smtp_server, timeout=3)
        r.raise_for_status()
        return {"status_code": r.status_code, "msg":r.json(), "sent": True}

    except ConnectionError:
        return {"msg": "connection error to smtp server", "sent": False}

    except HTTPError:
        return {"msg": r.json(), "sent": False}