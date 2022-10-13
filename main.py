from threading import Thread
from flask import Flask, render_template
import discord
import sqlalchemy

app = Flask(__name__)

messages = []

def flask_thread(func):
    thread = Thread(target=func)
    thread.daemon = True
    thread.start()

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        messages.append({"message": message.content})
        print(f'Message from {message.author}: {message.content}')


@app.route("/", methods=["GET"])
def rss():
    return render_template('rss.xml', items=messages)

flask_thread(func=lambda : app.run())

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run("MTAyOTkxMDg4NTU3MDk5MDEzMA.GzgQQ7.xUGsI02u9XKY4d6tSz7756uXqBXYpKx7A2mEC4")