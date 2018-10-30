from common.namespace import namespaced

CHANNEL_LOBBY_LIST = namespaced("channel:lobby_list")
CHANNEL_TRANSFER = namespaced("channel:transfer")


def lobby_chat(lobby_id):
    return namespaced(f'channel:lobby_chat:{lobby_id}')
