from cachetools import TTLCache


class MemoryCache:
    def __init__(self, ttl_seconds: int, maxsize: int = 512) -> None:
        self._cache: TTLCache[str, object] = TTLCache(maxsize=maxsize, ttl=ttl_seconds)

    def get(self, key: str) -> object | None:
        return self._cache.get(key)

    def set(self, key: str, value: object) -> None:
        self._cache[key] = value

