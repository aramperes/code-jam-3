import os

from flask import Flask, render_template

flask = Flask(__name__)


@flask.route("/")
def index():
    return render_template("_flexx_output.html")


def run():
    flask.run(
        host=os.getenv("FLASK_HOST", None),
        port=int(os.getenv("FLASK_PORT", 5000))
    )
