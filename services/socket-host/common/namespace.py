_REDIS_NAMESPACE = "deathwatch"


def namespaced(key):
    return f"{_REDIS_NAMESPACE}:{key}"
