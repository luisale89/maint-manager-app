from datetime import datetime
import re

from flask_jwt_extended import decode_token

from ..extensions import db
from .exceptions import TokenNotFound
from ..models import TokenBlacklist

def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc)


def add_token_to_database(encoded_token, identity_claim):
    """
    Adds a new token to the database. It is not revoked when it is added.
    :param identity_claim:
    """
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    user_identity = decoded_token[identity_claim]
    expires = _epoch_utc_to_datetime(decoded_token['exp'])
    revoked = False

    db_token = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_identity=user_identity,
        expires=expires,
        revoked=revoked,
    )
    db.session.add(db_token)
    db.session.commit()


def prune_database():
    """
    Delete tokens that have expired from the database.
    How (and if) you call this is entirely up you. You could expose it to an
    endpoint that only administrators could call, you could run it as a cron,
    set it up with flask cli, etc.
    """
    now = datetime.now()
    expired = TokenBlacklist.query.filter(TokenBlacklist.expires < now).all()
    for token in expired:
        db.session.delete(token)
    db.session.commit()


def normalize_names(name, spaces=False):
    '''Capitalize and delete white spaces in a string'''
    if not spaces:
        return name.replace(" ", "").capitalize()
    else:
        return name.strip().title()

def valid_email(email):
    '''
    check for a valid email format, return True or False.
    '''
    #Regular expression that checks a valid email
    ereg = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return bool(re.search(ereg, email))

def valid_password(password):
    '''
    check for a valid password format, return True or False.
    '''
    #Regular expression that checks a secure password
    preg = preg = '^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$'
    return bool(re.search(preg, password))

def only_letters(string, spaces=False):
    '''
    Check for special characters in a string. return True or False
    '''
    #regular expression that checks only letters string
    sreg = '^[a-zA-ZñáéíóúÑÁÉÍÓÚ]*$'
    #regular expression that check letters and spaces in a string
    sregs = '^[a-zA-Z ñáéíóúÑÁÉÍÓÚ]*$'
    if string == '' or not isinstance(string, str):
        return False
    if not spaces:
        return bool(re.search(sreg, string))
    else:
        return bool(re.search(sregs, string))
