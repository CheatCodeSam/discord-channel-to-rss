import json
from threading import Thread
from flask import Flask, render_template
from loguru import logger
from models import Event, db, Announcement
from discord_client import client
from waitress import serve
from flask_cors import CORS




app = Flask(__name__)
CORS(app)
logger.start(
    "log.log",
    level="DEBUG",
    format="{time} {level} {message}",
    backtrace=True,
    rotation="25 MB",
)
db.connect()
db.create_tables([Announcement, Event])


def flask_thread(func):
    thread = Thread(target=func)
    thread.daemon = True
    thread.start()


@app.route("/feed/", methods=["GET"])
def rss():
    messages = [announcement for announcement in Announcement.select().dicts()][-10:]
    return render_template("rss.xml", items=messages)


@app.route("/events", methods=["GET"])
def events():
    events = [announcement for announcement in Event.select().dicts()]
    return json.dumps(events, indent=4, sort_keys=True, default=str)


flask_thread(func=lambda: serve(app, host="0.0.0.0", port=8888))


client.run("MTAyOTkxMDg4NTU3MDk5MDEzMA.GzgQQ7.xUGsI02u9XKY4d6tSz7756uXqBXYpKx7A2mEC4")
