from datetime import datetime

from flask import session
from flask_restful import reqparse
from peewee import DoesNotExist, IntegrityError
from playhouse.shortcuts import model_to_dict

import db
from resources.base import BaseResource


class ProjectList(BaseResource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, required=False)
        parser.add_argument('limit', type=int, required=False)
        args = parser.parse_args()

        projects = []
        try:
            with db.database.atomic():
                query = db.Project.select().where(
                    db.Project.user == session['user']['id']
                ).order_by(db.Project.last_updated.desc())
                total = query.count()
                if args['page'] is not None and args['limit'] is not None:
                    query = query.paginate(args['page'], args['limit'])
                with db.database.atomic():
                    for project in query:
                        project_dict = model_to_dict(project)
                        del project_dict['user']
                        projects.append(project_dict)
        except DoesNotExist:
            return {'total': 0, 'data': []}, 200

        return {'total': total, 'data': projects}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        args = parser.parse_args()

        try:
            with db.database.atomic():
                project = db.Project.create(
                    user=session['user']['id'],
                    title=args['title']
                )
        except IntegrityError:
            return {'message': 'You are already using that project title'}, 400

        project_dict = model_to_dict(project)
        del project_dict['user']

        return project_dict, 201


class Project(BaseResource):
    def get(self, project_id):
        try:
            with db.database.atomic():
                project = db.Project.select().where(
                    db.Project.user == session['user']['id'],
                    db.Project.id == project_id
                ).get()
        except DoesNotExist:
            return {'message': 'That project does not exists'}, 404

        project_dict = model_to_dict(project)
        del project_dict['user']

        return project_dict, 200

    def delete(self, project_id):
        try:
            with db.database.atomic():
                db.Task.delete().where(
                    db.Task.project == project_id
                ).execute()
                db.Project.delete().where(
                    db.Project.user == session['user']['id'],
                    db.Project.id == project_id
                ).execute()
        except DoesNotExist:
            return {'message': 'That project does not exists'}, 404

        return '', 204

    def put(self, project_id):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        args = parser.parse_args()

        try:
            with db.database.atomic():
                project = db.Project.select().where(
                    db.Project.user == session['user']['id'],
                    db.Project.id == project_id
                ).get()
                project.title = args['title']
                project.last_updated = datetime.utcnow()
                project.save()
        except DoesNotExist:
            return {'message': 'That project does not exists'}, 404
        except IntegrityError:
            return {'message': 'You are already using that project title'}, 400

        project_dict = model_to_dict(project)
        del project_dict['user']

        return project_dict, 200
