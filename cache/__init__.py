"""
AeroTracker Core — Pacote de Cache
=====================================
Exporta o gerenciador de cache global.
"""

from cache.cache_manager import CacheEntry, CacheManager, cache_manager

__all__ = [
    "cache_manager",
    "CacheManager",
    "CacheEntry",
]
