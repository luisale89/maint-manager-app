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
mail_mode = os.environ['MAIL_MODE']
api_key = os.environ['SMTP_API_KEY']
default_sender = {"name": "Luis from MyApp", "email": "luis.lucena89@gmail.com"}
default_content = "<!DOCTYPE html><html><body><h1>Email de prueba</h1><p>development mode</p></body></html>"
default_subject = "this is a test"


class Email_api_service():

    '''
    SMTP Service via API
    '''

    def __init__(self, recipient, content=default_content, sender=default_sender, subject=default_subject) -> None:
        self.content = content
        self.sender = sender
        self.recipient = recipient
        self.subject = subject

    def header(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": api_key
        }

    def body(self):
        return {
            "sender": self.sender,
            "to": self.recipient,
            "subject": self.subject,
            "htmlContent": self.content
        }

    def send_request(self):
        '''
        SMTP API request function
        '''

        if mail_mode == 'development':
            print(self.content)
            return None

        try:
            r = requests.post(headers=self.header(), json=self.body(), url=smtp_api_url, timeout=3)
            r.raise_for_status()

        except ConnectionError:
            raise APIException("Connection error to smtp server", status_code=503)

        except HTTPError:
            # return {"msg": r.json(), "sent": False}
            raise APIException("HTTP Error", status_code=503)

        pass


def send_verification_email(verification_code, user:dict=None):
    '''
    Funcion para enviar un codigo de verificacion al correo electronico, el cual sera ingresado por el usuario a la app
    '''
    user_name, user_email = user.get('fname'), user.get('email')

    if user_name is None or user_email is None:
        raise APIException("Missing parameters in verification function", status_code=503)

    email = Email_api_service(
        user_email, 
        content=render_template("mail/user-validation.html", params = {"code":verification_code, "user_name": user_name}),
        subject="[My App] - Código de Verificación"
    )

    email.send_request()

    pass


# def send_validation_email(user:dict=None):
#     '''
#     función para enviar a través de una solicitud http a la api del servidor smtp un correo
#     electrónico de validacion. Estos son los parámetros requeridos:

#     - email: Correo electronico que debe ser validado por el usuario.

#     '''
#     name = user.get('name')
#     email = user.get('email')

#     if name is None or email is None:
#         return {"status_code": 400, "msg": "bad request", "sent": False}

#     token = create_url_token(identifier=email, salt=email_salt)
#     url_params = f"?email={email}&token={token}"
#     validation_url = main_frontend_url + url_for('validations_bp.email_validation') + url_params

#     data = {
#         "sender": default_sender,
#         "to": [{ "name": name, "email": email }],
#         "subject": "Valida tu correo electronico",
#         "htmlContent": render_template("mail/user-validation.html", params = {"link":validation_url})
#     }
#     rsp = smtp_api_request(data=data, debug={"link": validation_url})
#     if not rsp['sent']:
#         raise APIException(f"fail on sending validation email to user, provider msg: {rsp['msg']}", status_code=503)

#     pass


# def send_pwchange_email(user:dict=None):
#     '''
#     función para enviar a través de una solicitud http a la api del servidor smtp un correo
#     electrónico de validacion. Estos son los parámetros requeridos:

#     - email: Correo electronico que debe ser validado por el usuario.

#     '''
#     name = user.get('name')
#     email = user.get('email')

#     if name is None or email is None:
#         return {"status_code": 400, "msg": "bad request", "sent": False}

#     token = create_url_token(identifier=email, salt=pw_salt)
#     url_params = "?email={}&token={}".format(email, token)
#     validation_url = main_frontend_url + url_for('validations_bp.pw_reset') + url_params

#     data = {
#         "sender": default_sender,
#         "to": [{ "name": name, "email": email }],
#         "subject": "Reestablece tu contraseña",
#         "htmlContent": render_template("mail/password-reset.html", params = {"link":validation_url}),
#     }

#     rsp = smtp_api_request(data=data, debug={"link":validation_url})
#     if not rsp['sent']:
#         raise APIException(f"fail on sending validation email to user, provider msg: {rsp['msg']}", status_code=503)

#     pass
