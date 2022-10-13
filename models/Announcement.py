import peewee
from .database import BaseModel

class Announcement(BaseModel):
    message = peewee.TextField()