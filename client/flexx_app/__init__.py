from flexx import flx

from flexx_app.client import Client
from flexx_app.widgets.base import BaseWidget


def init(ws_url):
    return flx.App(
        BaseWidget,
        ws_url=ws_url,
        title='DeathWatch'
    )
