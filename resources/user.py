import hashlib

from flask import session
from flask_restful import reqparse
from peewee import IntegrityError, DoesNotExist
from playhouse.shortcuts import model_to_dict

import db
from resources.base import BaseResource


class UserRegister(BaseResource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        try:
            with db.database.atomic():
                user = db.User.create(
                    name=args['name'],
                    email=args['email'],
                    username=args['username'],
                    password=hashlib.sha256(args['password'].encode()).hexdigest()
                )
        except IntegrityError:
            return {'message': 'That username/email is already taken'}, 400

        user_dict = model_to_dict(user)
        del user_dict['password']

        return user_dict, 201


class UserLogin(BaseResource):
    def post(self):
        if session.get('user'):
            return {'message': 'User is already logged in, please logout first.'}, 400

        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        try:
            with db.database.atomic():
                user = db.User.select().where(db.User.username == args['username']).get()
        except DoesNotExist:
            return {'message': 'That username does not exists'}, 400

        password = hashlib.sha256(args['password'].encode()).hexdigest()

        if user.password == password:
            user_dict = model_to_dict(user)
            del user_dict['password']
            session['user'] = user_dict
            return user_dict, 200
        else:
            return {'message': 'Incorrect password!'}, 403


class UserLogout(BaseResource):
    def post(self):
        session.clear()
        return '', 204


class User(BaseResource):
    def get(self):
        return session['user'], 200

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        args = parser.parse_args()

        try:
            with db.database.atomic():
                user = db.User.select().where(
                    db.User.id == session['user']['id']
                ).get()
                user.name = args['name']
                user.email = args['email']
                user.save()
        except DoesNotExist:
            return {'message': 'That user does not exists'}, 400
        except IntegrityError:
            return {'message': 'That username/email is already taken'}, 400

        user_dict = model_to_dict(user)
        del user_dict['password']
        session['user'] = user_dict
        return user_dict, 200
