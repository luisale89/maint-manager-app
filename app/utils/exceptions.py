
class APIException(Exception):
    status_code = 400

    def __init__(self, message, app_status="error", status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.data = payload
        self.app_status = app_status

    def to_dict(self):
        rv = {
            "status": self.app_status,
            "data": dict(self.data or ()),
            "message": self.message
        }
        return rv


class TokenNotFound(Exception):
    """
    Indicates that a token could not be found in the database
    """
    pass 