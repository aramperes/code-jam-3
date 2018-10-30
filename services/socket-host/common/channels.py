from common.namespace import namespaced

CHANNEL_LOBBY_LIST = namespaced("channel:lobby_list")
CHANNEL_TRANSFER = namespaced("channel:transfer")


def lobby_chat(lobby_id):
    return namespaced(f'channel:lobby_chat:{lobby_id}')


def world_init(world_id):
    return namespaced(f'channel:world_init:{world_id}')


def world_terrain(world_id):
    return namespaced(f'channel:world_terrain:{world_id}')


def world_ready(world_id):
    return namespaced(f'channel:world_ready:{world_id}')
