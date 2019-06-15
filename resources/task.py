from datetime import datetime

from flask_restful import reqparse
from playhouse.shortcuts import model_to_dict, DoesNotExist, IntegrityError

import db
from resources.base import BaseResource


class TaskList(BaseResource):
    def get(self, project_id):
        tasks = []
        try:
            with db.database.atomic():
                for task in db.Task.select().where(
                        db.Task.project == project_id
                ):
                    task_dict = model_to_dict(task)
                    del task_dict['project']
                    tasks.append(task_dict)
        except DoesNotExist:
            return [], 200

        return tasks, 200

    def post(self, project_id):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('order', type=int, required=True)
        parser.add_argument('due_date', type=datetime, required=False)
        args = parser.parse_args()

        try:
            with db.database.atomic():
                try:
                    project = db.Project.select().where(
                        db.Project.id == project_id
                    ).get()
                except DoesNotExist:
                    return {'message': 'That project does not exists'}, 400

                task = db.Task.create(
                    project=project.id,
                    title=args['title'],
                    order=args['order'],
                    due_date=args['due_date']
                )
        except IntegrityError:
            return {'message': 'There is a conflict with task order value'}, 400

        task_dict = model_to_dict(task)
        del task_dict['project']

        return task_dict, 201


class Task(BaseResource):
    def get(self, project_id, task_id):
        try:
            with db.database.atomic():
                task = db.Task.select().where(
                    db.Task.project == project_id,
                    db.Task.id == task_id
                ).get()
        except DoesNotExist:
            return {'message': 'That task does not exists'}, 400

        task_dict = model_to_dict(task)
        del task_dict['project']

        return task_dict, 200

    def delete(self, project_id, task_id):
        try:
            with db.database.atomic():
                db.Task.delete().where(
                    db.Task.project == project_id,
                    db.Task.id == task_id
                ).execute()
        except DoesNotExist:
            return {'message': 'That task does not exists'}, 400

        return '', 204

    def put(self, project_id, task_id):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('order', type=int, required=True)
        parser.add_argument('due_date', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True)
        parser.add_argument('completed', type=lambda x: x.lower() in ['true', '1'], required=True)
        args = parser.parse_args()

        try:
            with db.database.atomic():
                task = db.Task.select().where(
                    db.Task.project == project_id,
                    db.Task.id == task_id
                ).get()
                task.title = args['title']
                task.order = args['order']
                task.due_date = args['due_date']
                task.completed = args['completed']
                task.save()
        except DoesNotExist:
            return {'message': 'That task does not exists'}, 400
        except IntegrityError:
            return {'message': 'There is a conflict with task order value'}, 400

        task_dict = model_to_dict(task)
        del task_dict['project']

        return task_dict, 200
