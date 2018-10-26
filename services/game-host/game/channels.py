from game.namespace import namespaced

CHANNEL_LOBBY_LIST = namespaced("channel:lobby_list")


def lobby_chat(lobby_id):
    return namespaced(f'channel:lobby_chat:{lobby_id}')
