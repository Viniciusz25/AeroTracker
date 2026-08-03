"""
AeroTracker Core — WebSocket Connection Manager
================================================
Gerencia conexões WebSocket agrupadas por canal.

Cada canal representa um domínio de dados em tempo real:
    - "aircraft"  → posições de aeronaves
    - "iss"       → posição da ISS
    - "system"    → eventos de sistema (errors, health)

Uso:
    from backend.websocket.manager import ws_manager

    # Em um endpoint WebSocket:
    await ws_manager.connect(websocket, channel="aircraft")

    # Para broadcast de um evento:
    await ws_manager.broadcast("aircraft", {"event": "aircraft.updated", "data": ...})
"""

import json
import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Gerencia o pool de conexões WebSocket organizadas por canal.

    Thread-safe para múltiplas conexões simultâneas.
    Remove automaticamente conexões fechadas durante broadcast.
    """

    def __init__(self) -> None:
        # Dicionário channel → lista de WebSockets ativos
        self._channels: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        """
        Aceita uma nova conexão WebSocket e adiciona ao canal.

        Args:
            websocket: Conexão WebSocket recebida pelo endpoint.
            channel: Nome do canal (ex: "aircraft", "iss").
        """
        await websocket.accept()
        self._channels[channel].append(websocket)
        count = len(self._channels[channel])
        logger.info("[WS] Nova conexão no canal '%s'. Total: %d", channel, count)

    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        """
        Remove uma conexão WebSocket do canal.

        Args:
            websocket: Conexão a ser removida.
            channel: Nome do canal.
        """
        try:
            self._channels[channel].remove(websocket)
            count = len(self._channels[channel])
            logger.info("[WS] Conexão removida do canal '%s'. Restam: %d", channel, count)
        except ValueError:
            pass  # Já foi removida

    async def broadcast(self, channel: str, payload: dict) -> None:
        """
        Envia payload JSON para todos os clientes conectados no canal.

        Remove automaticamente conexões mortas durante a iteração.

        Args:
            channel: Nome do canal alvo.
            payload: Dicionário Python que será serializado como JSON.
        """
        message = json.dumps(payload, default=str)
        dead: list[WebSocket] = []

        for websocket in list(self._channels[channel]):
            try:
                await websocket.send_text(message)
            except Exception:
                # Conexão fechada inesperadamente
                dead.append(websocket)

        # Limpar conexões mortas
        for ws in dead:
            self.disconnect(ws, channel)

    async def broadcast_all(self, payload: dict) -> None:
        """
        Envia payload para todos os canais (eventos de sistema global).

        Args:
            payload: Dicionário Python que será serializado como JSON.
        """
        for channel in list(self._channels.keys()):
            await self.broadcast(channel, payload)

    def channel_count(self, channel: str) -> int:
        """Retorna o número de conexões ativas em um canal."""
        return len(self._channels.get(channel, []))

    def total_connections(self) -> int:
        """Retorna o total de conexões WebSocket ativas."""
        return sum(len(ws_list) for ws_list in self._channels.values())

    def stats(self) -> dict:
        """Retorna estatísticas de conexões por canal."""
        return {
            "total_connections": self.total_connections(),
            "channels": {
                channel: len(ws_list)
                for channel, ws_list in self._channels.items()
            },
        }


# Singleton global — importar este objeto nos routers e na bridge
ws_manager = ConnectionManager()
