import functools
from flask import request
from app.utils.exceptions import (
    APIException
)


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
                    raise APIException(f"Missing arguments in {'url' if query_params is True else 'query params'}", payload={"missing": missing})
                
                wrong_types = [r for r in required.keys() if not isinstance(_json[r], required[r])] if _json is not None else None
                if wrong_types:
                    param_types = {k: str(v) for k, v in required.items()}
                    raise APIException("Data types in the request JSON doesn't match the required format", payload={"required": param_types})

            return func(*args, **kwargs)
        return wrapper_func
    return decorator