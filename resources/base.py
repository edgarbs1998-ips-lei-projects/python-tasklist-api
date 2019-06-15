from flask_restful import Resource


class BaseResource(Resource):
    def __init__(self, **kwargs):
        self.database = kwargs['database']

        if 'authenticate' in kwargs:
            self.method_decorators = [kwargs['authenticate']]
