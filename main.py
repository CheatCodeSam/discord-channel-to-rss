from threading import Thread
from flask import Flask, render_template
import discord
import peewee

db = peewee.SqliteDatabase('my_database.db')

class BaseModel(peewee.Model):
    class Meta:
        database = db

app = Flask(__name__)

class Tweet(BaseModel):
    message = peewee.TextField()

def flask_thread(func):
    thread = Thread(target=func)
    thread.daemon = True
    thread.start()

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        Tweet.create(message=message.content)



@app.route("/", methods=["GET"])
def rss():
    messages = [tweet for tweet in Tweet.select().dicts()]
    return render_template('rss.xml', items=messages)


db.connect()
db.create_tables([Tweet])

flask_thread(func=lambda : app.run())

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run("MTAyOTkxMDg4NTU3MDk5MDEzMA.GzgQQ7.xUGsI02u9XKY4d6tSz7756uXqBXYpKx7A2mEC4")