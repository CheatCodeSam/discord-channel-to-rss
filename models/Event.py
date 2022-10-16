import peewee
from .database import BaseModel


class Event(BaseModel):
    discord_id = peewee.BigIntegerField(null=False, unique=True)
    title = peewee.TextField()
    body = peewee.TextField(null=True)
    start = peewee.DateTimeField()
    end = peewee.DateTimeField()
