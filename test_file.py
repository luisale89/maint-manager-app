class JSONResponse():

    def __init__(self, message, app_status="success", status_code=200, payload=None):
        self.app_status = app_status
        self.status_code = status_code
        self.data = payload
        self.message = message

    def serialize(self):
        rv = {
            "status": self.app_status,
            "data": dict(self.data or ()),
            "message": self.message #for debug in frontend
        }
        return rv

class Tested():

    def __init__(self, code):
        self.code = code

    def to_dict(self):
        rv = {
            "code": self.code #for debug in frontend
        }
        return rv


class Target(JSONResponse, Tested):

    def __init__(self, message, code, app_status="success", status_code=200, payload=None):
        JSONResponse.__init__(self, message, app_status, status_code, payload)
        Tested.__init__(self, code)

    def to_print(self):
        print(self.serialize())

t = Target("super message", 200)
t.to_print()
t.to_dict()