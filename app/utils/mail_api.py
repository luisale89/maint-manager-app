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

def send_email(to_list:list, sender:dict=None, mail_link="https://google.com", subject=None):
    data = {
        "sender": default_sender if sender is None else sender,
        "to": to_list,
        "subject": "Correo de prueba" if subject is None else subject,
        "htmlContent": "<!DOCTYPE html> <html> <body> <h1>Confirm you email</h1> <p>Please confirm your email address by clicking on the link below</p><p>{}</p></body> </html>".format(mail_link)
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