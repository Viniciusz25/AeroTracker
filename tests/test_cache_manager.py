"""
Testes — Cache Manager
========================
Testa todas as operações do CacheManager:
    - set / get / has
    - expiração por TTL
    - invalidação individual e por namespace
    - purge de entradas expiradas
    - geração de chaves
    - estatísticas
"""

import time

import pytest

from cache.cache_manager import CacheEntry, CacheManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def cache() -> CacheManager:
    """Retorna um CacheManager limpo para cada teste."""
    return CacheManager(persist_dir=None)


# ---------------------------------------------------------------------------
# Testes: CacheEntry
# ---------------------------------------------------------------------------


class TestCacheEntry:
    def test_not_expired_initially(self) -> None:
        entry = CacheEntry(value="test", ttl=60)
        assert not entry.is_expired

    def test_expired_with_zero_ttl(self) -> None:
        entry = CacheEntry(value="test", ttl=0)
        assert entry.is_expired

    def test_remaining_seconds_positive(self) -> None:
        entry = CacheEntry(value="test", ttl=30)
        assert entry.remaining_seconds > 0
        assert entry.remaining_seconds <= 30

    def test_remaining_seconds_zero_when_expired(self) -> None:
        entry = CacheEntry(value="test", ttl=0)
        assert entry.remaining_seconds == 0.0


# ---------------------------------------------------------------------------
# Testes: CacheManager — set e get
# ---------------------------------------------------------------------------


class TestCacheManagerSetGet:
    def test_set_and_get_string(self, cache: CacheManager) -> None:
        cache.set("aircraft", "key1", "valor_teste", ttl=60)
        result = cache.get("aircraft", "key1")
        assert result == "valor_teste"

    def test_set_and_get_dict(self, cache: CacheManager) -> None:
        data = {"lat": -23.5, "lon": -46.6, "count": 42}
        cache.set("weather", "sp_data", data, ttl=300)
        result = cache.get("weather", "sp_data")
        assert result == data

    def test_set_and_get_list(self, cache: CacheManager) -> None:
        data = [1, 2, 3, {"a": "b"}]
        cache.set("iss", "positions", data, ttl=5)
        assert cache.get("iss", "positions") == data

    def test_get_nonexistent_returns_none(self, cache: CacheManager) -> None:
        result = cache.get("aircraft", "nao_existe")
        assert result is None

    def test_get_wrong_namespace_returns_none(self, cache: CacheManager) -> None:
        cache.set("aircraft", "k1", "v1", ttl=60)
        assert cache.get("weather", "k1") is None

    def test_overwrite_existing_key(self, cache: CacheManager) -> None:
        cache.set("ns", "k", "original", ttl=60)
        cache.set("ns", "k", "novo", ttl=60)
        assert cache.get("ns", "k") == "novo"


# ---------------------------------------------------------------------------
# Testes: Expiração por TTL
# ---------------------------------------------------------------------------


class TestCacheExpiry:
    def test_entry_expires_after_ttl(self, cache: CacheManager) -> None:
        cache.set("iss", "pos", {"lat": 0, "lon": 0}, ttl=1)
        assert cache.has("iss", "pos")
        time.sleep(1.1)
        assert not cache.has("iss", "pos")

    def test_get_returns_none_after_expiry(self, cache: CacheManager) -> None:
        cache.set("iss", "pos", "valor", ttl=1)
        time.sleep(1.1)
        assert cache.get("iss", "pos") is None


# ---------------------------------------------------------------------------
# Testes: has
# ---------------------------------------------------------------------------


class TestCacheHas:
    def test_has_returns_true_for_valid_entry(self, cache: CacheManager) -> None:
        cache.set("moon", "phase", "waxing", ttl=3600)
        assert cache.has("moon", "phase") is True

    def test_has_returns_false_for_missing(self, cache: CacheManager) -> None:
        assert cache.has("moon", "missing") is False


# ---------------------------------------------------------------------------
# Testes: Invalidação
# ---------------------------------------------------------------------------


class TestCacheInvalidation:
    def test_invalidate_single_key(self, cache: CacheManager) -> None:
        cache.set("ns", "k1", "v1", ttl=60)
        cache.set("ns", "k2", "v2", ttl=60)
        removed = cache.invalidate("ns", "k1")
        assert removed is True
        assert cache.get("ns", "k1") is None
        assert cache.get("ns", "k2") == "v2"

    def test_invalidate_nonexistent_key_returns_false(self, cache: CacheManager) -> None:
        assert cache.invalidate("ns", "nao_existe") is False

    def test_invalidate_namespace(self, cache: CacheManager) -> None:
        cache.set("aircraft", "a", 1, ttl=60)
        cache.set("aircraft", "b", 2, ttl=60)
        cache.set("weather", "c", 3, ttl=60)
        count = cache.invalidate_namespace("aircraft")
        assert count == 2
        assert cache.get("aircraft", "a") is None
        assert cache.get("aircraft", "b") is None
        assert cache.get("weather", "c") == 3  # outro namespace intacto

    def test_clear_all(self, cache: CacheManager) -> None:
        cache.set("a", "k1", 1, ttl=60)
        cache.set("b", "k2", 2, ttl=60)
        cache.clear_all()
        assert cache.get("a", "k1") is None
        assert cache.get("b", "k2") is None


# ---------------------------------------------------------------------------
# Testes: Purge
# ---------------------------------------------------------------------------


class TestCachePurge:
    def test_purge_removes_expired(self, cache: CacheManager) -> None:
        cache.set("ns", "expired", "v", ttl=1)
        cache.set("ns", "valid", "v2", ttl=60)
        time.sleep(1.1)
        removed = cache.purge_expired()
        assert removed == 1
        assert cache.get("ns", "valid") == "v2"
        assert cache.get("ns", "expired") is None

    def test_purge_returns_zero_when_nothing_expired(self, cache: CacheManager) -> None:
        cache.set("ns", "k", "v", ttl=60)
        assert cache.purge_expired() == 0


# ---------------------------------------------------------------------------
# Testes: Estatísticas
# ---------------------------------------------------------------------------


class TestCacheStats:
    def test_stats_empty(self, cache: CacheManager) -> None:
        stats = cache.stats()
        assert stats["total_entries"] == 0
        assert stats["namespaces"] == {}

    def test_stats_with_entries(self, cache: CacheManager) -> None:
        cache.set("aircraft", "a", 1, ttl=60)
        cache.set("aircraft", "b", 2, ttl=60)
        cache.set("weather", "c", 3, ttl=60)
        stats = cache.stats()
        assert stats["total_entries"] == 3
        assert stats["namespaces"]["aircraft"]["active"] == 2
        assert stats["namespaces"]["weather"]["active"] == 1


# ---------------------------------------------------------------------------
# Testes: Geração de Chave
# ---------------------------------------------------------------------------


class TestCacheMakeKey:
    def test_same_args_same_key(self) -> None:
        k1 = CacheManager.make_key(-23.5, -46.6, 250)
        k2 = CacheManager.make_key(-23.5, -46.6, 250)
        assert k1 == k2

    def test_different_args_different_key(self) -> None:
        k1 = CacheManager.make_key(-23.5, -46.6)
        k2 = CacheManager.make_key(-10.0, -50.0)
        assert k1 != k2

    def test_key_length_is_12(self) -> None:
        key = CacheManager.make_key("test", 123)
        assert len(key) == 12
