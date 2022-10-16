import peewee
from .database import BaseModel


class Event(BaseModel):
    title = peewee.TextField()
    description = peewee.TextField(null=True)
    start = peewee.DateTimeField()
    end = peewee.DateTimeField()
