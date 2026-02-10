"""
WebSocket Connection Manager for Booksmart.

Manages active WebSocket connections per user, enabling real-time push of:
- Notifications (new appointment, payment, message, etc.)
- Chat messages
- Any event the frontend needs instantly

Usage from anywhere in the backend:
    from app.core.websocket_manager import manager

    # Send to a specific user
    await manager.send_personal(user_id=42, data={"type": "notification", ...})

    # Broadcast to all connected users
    await manager.broadcast(data={"type": "system", "message": "Maintenance in 5 min"})
"""

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Keeps a dict of user_id -> list[WebSocket].
    A single user can have multiple connections (e.g. phone + browser).
    """

    def __init__(self) -> None:
        # user_id -> [websocket, ...]
        self._connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        """Accept a new WebSocket and register it under the user_id."""
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(websocket)
        logger.info("WS connected: user_id=%s  (total connections: %s)", user_id, self.count)

    def disconnect(self, websocket: WebSocket, user_id: int) -> None:
        """Remove a WebSocket when the client disconnects."""
        if user_id in self._connections:
            self._connections[user_id] = [
                ws for ws in self._connections[user_id] if ws is not websocket
            ]
            if not self._connections[user_id]:
                del self._connections[user_id]
        logger.info("WS disconnected: user_id=%s  (total connections: %s)", user_id, self.count)

    def is_connected(self, user_id: int) -> bool:
        """Check if a user has any active WebSocket connections."""
        return user_id in self._connections and len(self._connections[user_id]) > 0

    async def send_personal(self, user_id: int, data: Dict[str, Any]) -> None:
        """Send a JSON message to all connections of a specific user."""
        connections = self._connections.get(user_id, [])
        dead: List[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        # Clean up any broken connections
        for ws in dead:
            self.disconnect(ws, user_id)

    async def send_to_many(self, user_ids: List[int], data: Dict[str, Any]) -> None:
        """Send a JSON message to multiple users."""
        for uid in user_ids:
            await self.send_personal(uid, data)

    async def broadcast(self, data: Dict[str, Any]) -> None:
        """Send a JSON message to ALL connected users."""
        all_user_ids = list(self._connections.keys())
        await self.send_to_many(all_user_ids, data)

    @property
    def count(self) -> int:
        """Total number of active WebSocket connections."""
        return sum(len(conns) for conns in self._connections.values())

    @property
    def connected_users(self) -> List[int]:
        """List of user IDs with active connections."""
        return list(self._connections.keys())


# ── Singleton instance ──────────────────────────────────────────────────────
manager = ConnectionManager()
