"""Tests for cache behavior — TTLCache size and time eviction."""

import threading
import time

from cachetools import TTLCache


class TestTTLCacheBehavior:
    def test_evicts_by_size(self):
        cache: TTLCache = TTLCache(maxsize=3, ttl=300)
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3
        cache["d"] = 4  # should evict oldest
        assert "a" not in cache
        assert "d" in cache
        assert len(cache) == 3

    def test_evicts_by_ttl(self):
        cache: TTLCache = TTLCache(maxsize=100, ttl=0.1)
        cache["key"] = "value"
        assert "key" in cache
        time.sleep(0.15)
        assert "key" not in cache

    def test_thread_safe_with_lock(self):
        """Concurrent writes with a lock should not corrupt the cache."""
        cache: TTLCache = TTLCache(maxsize=1000, ttl=300)
        lock = threading.Lock()
        errors: list = []

        def writer(n):
            try:
                for i in range(50):
                    with lock:
                        cache[f"{n}_{i}"] = i
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(t,)) for t in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread safety errors: {errors}"
