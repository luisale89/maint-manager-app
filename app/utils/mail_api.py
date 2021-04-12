import requests
import os
from requests.exceptions import (
    ConnectionError, HTTPError
)

smpt_url = "https://api.sendinblue.com/v3/smtp/email"
api_key = os.environ['MAIL_API_KEY']
default_sender = {"name": "Luis Alejandro Lucena", "email": "luis.lucena89@gmail.com"}

headers = {
    "Accept": "application/json",
    "Content-type": "application/json",
    "api-key": api_key
}

def send_token_email(recipients:list, params:dict, sender:dict=None, subject=None) -> dict:
    pw_reset_url = "localhost:3000/password-reset/{}?token={}".format(params['temp_url'], params['token'])
    data = {
        "sender": default_sender if sender is None else sender,
        "to": recipients,
        "subject": "Correo de prueba" if subject is None else subject,
        "htmlContent": "<!DOCTYPE html> <html> <body> <h1>Confirm you email</h1> <p>Please confirm your email address by clicking on the link below</p><p>{}</p></body> </html>".format(pw_reset_url)
    }
    try:
        r = requests.post(headers=headers, json=data, url=smpt_url, timeout=5)
        r.raise_for_status()
        if r.status_code == 200 or r.status_code == 201:
            return {"status_code": r.status_code, "msg":r.json(), "sent": True}

    except ConnectionError:
        return {"status_code": 408, "sent": False}
    except HTTPError:
        return {"status_code": r.status_code, "msg": r.json() ,"sent": False}