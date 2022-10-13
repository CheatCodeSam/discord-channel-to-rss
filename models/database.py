import peewee

db = peewee.SqliteDatabase('my_database.db')

class BaseModel(peewee.Model):
    class Meta:
        database = db
