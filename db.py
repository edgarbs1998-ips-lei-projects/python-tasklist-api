from datetime import datetime

from peewee import SqliteDatabase, CharField, ForeignKeyField, DateTimeField, TextField, IntegerField, \
    BooleanField, fn
from playhouse.signals import Model, pre_save

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
    if instance.order == 0:
        value = Task.select(fn.MAX(Task.order)).scalar()
        if value is not None:
            instance.order = value + 1
        else:
            instance.order = 1


def create_tables():
    with database:
        database.create_tables([User, Project, Task])
