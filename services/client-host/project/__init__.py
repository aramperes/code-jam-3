import os

from flask import Flask, render_template

flask = Flask(__name__)


@flask.route("/")
def index():
    return render_template("index.html")


def run():
    flask.run(
        host=os.getenv("FLASK_HOST", None),
        port=int(os.getenv("FLASK_PORT", 5000))
    )
