import re

_USERNAME_PATTERN = re.compile(r"^[\w]{2,15}$")

_LOBBY_NAME_PATTERN = re.compile(r"^[\w\s'#-]{2,35}$")


def username_valid(username: str) -> bool:
    return bool(_USERNAME_PATTERN.fullmatch(username))


def lobby_name_valid(lobby_name: str) -> bool:
    return bool(_LOBBY_NAME_PATTERN.fullmatch(lobby_name))
