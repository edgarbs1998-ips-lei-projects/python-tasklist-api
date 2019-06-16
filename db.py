from datetime import datetime

from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, DateTimeField, TextField, IntegerField, \
    BooleanField

import settings

database = SqliteDatabase(settings.DATABASE)


class User(Model):
    name = CharField()
    email = CharField(unique=True)
    username = CharField(unique=True)
    password = CharField()

    class Meta:
        database = database


class Project(Model):
    user = ForeignKeyField(User, backref='projects')
    title = CharField()
    creation_date = DateTimeField(default=datetime.utcnow)
    last_updated = DateTimeField(default=datetime.utcnow)

    class Meta:
        database = database
        indexes = (
            (('user', 'title'), True),
        )


class Task(Model):
    project = ForeignKeyField(Project, backref='tasks')
    title = TextField()
    order = IntegerField()
    creation_date = DateTimeField(default=datetime.utcnow)
    due_date = DateTimeField(null=True)
    completed = BooleanField(default=False)

    class Meta:
        database = database
        indexes = (
            (('project', 'order'), True),
        )


def create_tables():
    with database:
        database.create_tables([User, Project, Task])
