from threading import Thread
from flask import Flask, render_template
import discord
from models import db, Announcement
from discord_client import client

app = Flask(__name__)

db.connect()
db.create_tables([Announcement])


def flask_thread(func):
    thread = Thread(target=func)
    thread.daemon = True
    thread.start()


@app.route("/", methods=["GET"])
def rss():
    messages = [announcement for announcement in Announcement.select().dicts()]
    return render_template("rss.xml", items=messages)


flask_thread(func=lambda: app.run())


client.run("MTAyOTkxMDg4NTU3MDk5MDEzMA.GzgQQ7.xUGsI02u9XKY4d6tSz7756uXqBXYpKx7A2mEC4")
