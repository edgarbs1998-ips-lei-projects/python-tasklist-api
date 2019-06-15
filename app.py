import os
from functools import wraps

from flask import Flask, session, make_response, jsonify
from flask_restful import Api, abort

import settings
from db import database, create_tables
from resources.project import ProjectList, Project
from resources.task import TaskList, Task
from resources.user import User, UserRegister, UserLogin, UserLogout

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(16)
api = Api(app, prefix='/api')


@app.before_request
def before_request():
    database.connect()


@app.after_request
def after_request(response):
    database.close()
    return response


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(jsonify(data), code)
    resp.headers.extend(headers or {})
    return resp


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('user'):
            abort(401)
        return func(*args, **kwargs)
    return wrapper


@app.route('/')
def index():
    return app.send_static_file('index.html')


# API Routes
api.add_resource(UserRegister, '/user/register/',
                 resource_class_kwargs={'database': database})
api.add_resource(UserLogin, '/user/login/',
                 resource_class_kwargs={'database': database})
api.add_resource(UserLogout, '/user/logout/',
                 resource_class_kwargs={'database': database, 'authenticate': authenticate})
api.add_resource(User, '/user/',
                 resource_class_kwargs={'database': database, 'authenticate': authenticate})
api.add_resource(ProjectList, '/projects/',
                 resource_class_kwargs={'database': database, 'authenticate': authenticate})
api.add_resource(Project, '/projects/<int:project_id>/',
                 resource_class_kwargs={'database': database, 'authenticate': authenticate})
api.add_resource(TaskList, '/projects/<int:project_id>/tasks/',
                 resource_class_kwargs={'database': database, 'authenticate': authenticate})
api.add_resource(Task, '/projects/<int:project_id>/tasks/<int:task_id>/',
                 resource_class_kwargs={'database': database, 'authenticate': authenticate})


create_tables()
app.run(host=settings.API_HOST, port=settings.API_PORT, debug=settings.FLASK_DEBUG)
