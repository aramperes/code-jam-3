import random


class RedisChannelReceipt:
    def __init__(self, func):
        self.func = func
        self.func_id = random.getrandbits(64)

    def call(self, *args, **kwargs):
        self.func(*args, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.func_id == other.func_id

    def __hash__(self):
        return self.func_id
