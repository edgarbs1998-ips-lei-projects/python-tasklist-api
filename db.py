from datetime import datetime

from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, DateTimeField, TextField, IntegerField, \
    BooleanField, fn
from playhouse.signals import pre_save

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
            (('project', 'title'), True),
        )


@pre_save(sender=Task)
def on_save_handler(model_class, instance, created):
    # find max value of temp_id in model
    # increment it by one and assign it to model instance object
    next_value = Task.select(fn.Max(Task.order))[0].order + 1
    instance.order = next_value


def create_tables():
    with database:
        database.create_tables([User, Project, Task])
