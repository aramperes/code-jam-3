import os

import responder

api = responder.API()


@api.route("/")
async def index(req, resp):
    resp.media = {
        "version": "0.0.1",
        "about": "This is the game host. It manages the multiplayer feature of the game.",
        "team": "Possible Jeans"
    }


def run():
    api.run(
        address=os.getenv("GAME_HOST", None),
        port=int(os.getenv("GAME_PORT", 5000))
    )
