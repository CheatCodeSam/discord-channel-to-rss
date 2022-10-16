import peewee
from .database import BaseModel


class Announcement(BaseModel):
    guid = peewee.BigIntegerField(null=False, unique=True)
    title = peewee.TextField()
    pubDate = peewee.DateTimeField()
    author = peewee.TextField()
