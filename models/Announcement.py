import peewee
from .database import BaseModel


class Announcement(BaseModel):
    discord_id = peewee.BigIntegerField(null=False, unique=True)
    message = peewee.TextField()
    posted = peewee.DateTimeField()
    author = peewee.TextField()
