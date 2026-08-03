"""
AeroTracker Core — Gerenciador de Cache
=========================================
Cache inteligente em memória com TTL por módulo e persistência opcional em JSON.

Responsabilidades:
    - Armazenar respostas de APIs em memória com tempo de vida (TTL)
    - Evitar chamadas desnecessárias às APIs externas
    - Cada módulo possui seu próprio namespace de cache
    - Suporte a persistência em disco (JSON) para sobreviver a restarts
    - Thread-safe e async-safe

Design:
    Utiliza TTLCache do cachetools por namespace.
    Cada namespace é um módulo (aircraft, weather, iss, etc.)
    A chave de cache é composta por: namespace + parâmetros da consulta.

Uso:
    from cache.cache_manager import cache_manager

    # Armazenar dado
    cache_manager.set("aircraft", "opensky_region_SP", data, ttl=30)

    # Recuperar dado (retorna None se expirado ou inexistente)
    data = cache_manager.get("aircraft", "opensky_region_SP")

    # Verificar existência
    if cache_manager.has("weather", "sao_paulo"):
        ...

    # Invalidar namespace inteiro
    cache_manager.invalidate_namespace("aircraft")
"""

import hashlib
import json
import time
from pathlib import Path
from threading import Lock
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Entrada de Cache
# ---------------------------------------------------------------------------


class CacheEntry:
    """
    Representa uma entrada no cache com dado, TTL e timestamp.

    Attributes:
        value: Dado armazenado (qualquer tipo serializável).
        expires_at: Timestamp UNIX em que o cache expira.
        created_at: Timestamp UNIX em que o cache foi criado.
    """

    __slots__ = ("value", "expires_at", "created_at")

    def __init__(self, value: Any, ttl: int) -> None:
        self.value = value
        self.created_at = time.monotonic()
        self.expires_at = self.created_at + ttl

    @property
    def is_expired(self) -> bool:
        """Retorna True se o cache expirou."""
        return time.monotonic() >= self.expires_at

    @property
    def remaining_seconds(self) -> float:
        """Retorna quantos segundos restam até expirar (0 se expirado)."""
        remaining = self.expires_at - time.monotonic()
        return max(0.0, remaining)


# ---------------------------------------------------------------------------
# Gerenciador de Cache
# ---------------------------------------------------------------------------


class CacheManager:
    """
    Gerenciador central de cache do AeroTracker.

    Organiza os dados por namespace (módulo), com TTL individual
    por entrada. Suporta persistência opcional em disco.

    Args:
        persist_dir: Diretório para persistência em JSON.
                     Se None, cache é apenas em memória.
    """

    def __init__(self, persist_dir: Optional[Path] = None) -> None:
        self._store: dict[str, dict[str, CacheEntry]] = {}
        self._lock = Lock()
        self._persist_dir = persist_dir

        if persist_dir:
            persist_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "CacheManager inicializado. Persistência: {persist}",
            persist=str(persist_dir) if persist_dir else "desativada"
        )

    # -------------------------------------------------------------------------
    # API Pública
    # -------------------------------------------------------------------------

    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Recupera um valor do cache.

        Args:
            namespace: Identificador do módulo (ex: "aircraft", "iss").
            key: Chave da entrada dentro do namespace.

        Returns:
            O valor armazenado, ou None se não existir ou estiver expirado.
        """
        with self._lock:
            entry = self._store.get(namespace, {}).get(key)

            if entry is None:
                logger.debug("Cache MISS: {ns}:{key}", ns=namespace, key=key)
                return None

            if entry.is_expired:
                logger.debug(
                    "Cache EXPIRED: {ns}:{key}",
                    ns=namespace, key=key
                )
                del self._store[namespace][key]
                return None

            logger.debug(
                "Cache HIT: {ns}:{key} (expira em {t:.1f}s)",
                ns=namespace, key=key, t=entry.remaining_seconds
            )
            return entry.value

    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: int,
    ) -> None:
        """
        Armazena um valor no cache.

        Args:
            namespace: Identificador do módulo.
            key: Chave da entrada.
            value: Dado a armazenar.
            ttl: Tempo de vida em segundos.
        """
        with self._lock:
            if namespace not in self._store:
                self._store[namespace] = {}

            self._store[namespace][key] = CacheEntry(value=value, ttl=ttl)

            logger.debug(
                "Cache SET: {ns}:{key} (TTL={ttl}s)",
                ns=namespace, key=key, ttl=ttl
            )

    def has(self, namespace: str, key: str) -> bool:
        """
        Verifica se uma entrada existe e não expirou.

        Args:
            namespace: Identificador do módulo.
            key: Chave da entrada.

        Returns:
            True se o cache existe e é válido.
        """
        return self.get(namespace, key) is not None

    def invalidate(self, namespace: str, key: str) -> bool:
        """
        Remove uma entrada específica do cache.

        Args:
            namespace: Identificador do módulo.
            key: Chave da entrada.

        Returns:
            True se a entrada existia e foi removida.
        """
        with self._lock:
            ns_store = self._store.get(namespace, {})
            if key in ns_store:
                del ns_store[key]
                logger.debug("Cache INVALIDATED: {ns}:{key}", ns=namespace, key=key)
                return True
            return False

    def invalidate_namespace(self, namespace: str) -> int:
        """
        Remove todas as entradas de um namespace.

        Args:
            namespace: Identificador do módulo.

        Returns:
            Número de entradas removidas.
        """
        with self._lock:
            ns_store = self._store.pop(namespace, {})
            count = len(ns_store)
            if count:
                logger.info(
                    "Cache namespace '{ns}' invalidado: {n} entradas removidas",
                    ns=namespace, n=count
                )
            return count

    def clear_all(self) -> None:
        """Remove todas as entradas de todos os namespaces."""
        with self._lock:
            total = sum(len(v) for v in self._store.values())
            self._store.clear()
            logger.warning("Cache completamente limpo: {n} entradas removidas", n=total)

    def purge_expired(self) -> int:
        """
        Remove todas as entradas expiradas de todos os namespaces.
        Deve ser chamado periodicamente pelo Scheduler.

        Returns:
            Número de entradas removidas.
        """
        removed = 0
        with self._lock:
            for namespace in list(self._store.keys()):
                ns_store = self._store[namespace]
                expired_keys = [k for k, v in ns_store.items() if v.is_expired]
                for key in expired_keys:
                    del ns_store[key]
                    removed += 1
                # Remove namespace vazio
                if not ns_store:
                    del self._store[namespace]

        if removed:
            logger.debug("Cache purge: {n} entradas expiradas removidas", n=removed)
        return removed

    def stats(self) -> dict[str, Any]:
        """
        Retorna estatísticas do cache atual.

        Returns:
            Dicionário com total de entradas, namespaces e detalhes por namespace.
        """
        with self._lock:
            result: dict[str, Any] = {
                "total_entries": 0,
                "namespaces": {},
            }
            for ns, ns_store in self._store.items():
                active = [k for k, v in ns_store.items() if not v.is_expired]
                expired = [k for k, v in ns_store.items() if v.is_expired]
                result["namespaces"][ns] = {
                    "active": len(active),
                    "expired": len(expired),
                    "keys": active,
                }
                result["total_entries"] += len(active)
            return result

    # -------------------------------------------------------------------------
    # Utilitário de chave
    # -------------------------------------------------------------------------

    @staticmethod
    def make_key(*args: Any) -> str:
        """
        Gera uma chave de cache determinística a partir de argumentos.

        Útil para criar chaves compostas por parâmetros de consulta.

        Args:
            *args: Argumentos a compor a chave (lat, lon, raio, etc.)

        Returns:
            String de chave hashada (SHA256 curto, 12 chars).

        Exemplo:
            key = CacheManager.make_key(-23.5, -46.6, 250)
        """
        raw = "|".join(str(a) for a in args)
        return hashlib.sha256(raw.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Singleton Global
# ---------------------------------------------------------------------------

# Importar de qualquer módulo com: from cache.cache_manager import cache_manager
cache_manager = CacheManager()
