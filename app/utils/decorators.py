import functools
from flask import (
    json, session, redirect, url_for, request, abort, jsonify
)
from flask_jwt_extended import decode_token
from sqlalchemy.orm import query
from app.utils.exceptions import (
    APIException
)


def login_required(func): #login in flask app directly
    ''' Validar si el usuario tiene acceso antes de continuar '''
    @functools.wraps(func)
    def wrapper_login_required(*args, **kwargs):
        if session.get('token') is None:
            return redirect(url_for("landing_bp.login"))
        token = decode_token(session.token)
        if token is None:
            return redirect(url_for("landing_bp.login"))
        
        return func(*args, **kwargs)
    return wrapper_login_required


def json_required(required:dict=None, query_params:bool=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            if not request.is_json:
                raise APIException("Missing header in request" ,payload={"missing":{"content-type":"application-json"}})

            if required is not None:
                _json = request.get_json(silent=True)
                _qparams = request.args

                if query_params:
                    missing = [r for r in required.keys() if r not in _qparams]
                else:             
                    if _json is None:
                        raise APIException("missing all arguments in request body")
                    missing = [r for r in required.keys() if r not in _json]

                if missing:
                    raise APIException("Missing arguments in {}".format("url" if query_params else "request"), payload={"missing": missing})
                
                wrong_types = [r for r in required.keys() if not isinstance(_json[r], required[r])] if _json is not None else None
                if wrong_types:
                    param_types = {k: str(v) for k, v in required.items()}
                    raise APIException("Data types in the request JSON doesn't match the required format", payload={"required": param_types})

            return func(*args, **kwargs)
        return wrapper_func
    return decorator