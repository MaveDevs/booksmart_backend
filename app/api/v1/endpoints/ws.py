"""
WebSocket endpoint for real-time communication.

Clients connect with their JWT token as a query parameter:
    ws://host/api/v1/ws?token=<JWT_TOKEN>

Protocol (JSON messages):
  Server -> Client:
    {"type": "notification", "data": { ... notification fields ... }}
    {"type": "message",      "data": { ... message fields ... }}
    {"type": "appointment",  "data": { ... appointment fields ... }}
    {"type": "ping"}

  Client -> Server:
    {"type": "ping"}                       -> server replies {"type": "pong"}
    {"type": "mark_read", "id": 123}       -> mark notification as read

Flutter Example:
    final channel = WebSocketChannel.connect(
      Uri.parse('wss://your-domain.com/api/v1/ws?token=$jwt'),
    );
    channel.stream.listen((event) {
      final data = jsonDecode(event);
      if (data['type'] == 'notification') { ... }
    });

React Example:
    const ws = new WebSocket(`wss://your-domain.com/api/v1/ws?token=${jwt}`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'notification') { ... }
    };
"""

import json
import logging
import os

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY
from app.core.websocket_manager import manager
from app.crud import crud_users, crud_notifications
from app.db.session import SessionLocal
from app.schemas.notifications import NotificationUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_db() -> Session:
    """Create a plain DB session (not a generator/Depends — WebSockets are different)."""
    return SessionLocal()


def _authenticate_ws_token(token: str) -> int | None:
    """
    Validate a JWT token and return the user_id, or None if invalid.
    """
    try:
        if os.getenv("JWT_AUTH_DISABLED", "false").lower() == "true":
            return int(os.getenv("JWT_BYPASS_USER_ID", "1"))

        if not token:
            return None

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            return None
        return int(subject)
    except (JWTError, ValueError):
        return None


def _is_jwt_auth_disabled() -> bool:
    return os.getenv("JWT_AUTH_DISABLED", "false").lower() == "true"


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str | None = Query(None),
):
    """
    Main WebSocket endpoint.
    Authenticates via JWT token in query param, then keeps connection alive.
    """
    # ── Authenticate ────────────────────────────────────────────────────
    user_id = _authenticate_ws_token(token)
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    if not _is_jwt_auth_disabled():
        # Verify user exists and is active
        db = _get_db()
        try:
            user = crud_users.get_user(db, user_id=user_id)
            if not user or not bool(user.activo):
                await websocket.close(code=4001, reason="User not found or inactive")
                return
        finally:
            db.close()

    # ── Connect ─────────────────────────────────────────────────────────
    await manager.connect(websocket, user_id)

    try:
        while True:
            # Wait for messages from the client
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = data.get("type")

            # ── Ping / Pong ─────────────────────────────────────────────
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            # ── Mark notification as read ───────────────────────────────
            elif msg_type == "mark_read":
                notification_id = data.get("id")
                if notification_id:
                    db = _get_db()
                    try:
                        notif = crud_notifications.get_notification(db, notification_id)
                        if notif and notif.usuario_id == user_id:
                            crud_notifications.update_notification(
                                db, notification_id, NotificationUpdate(leida=True)
                            )
                            await websocket.send_json({
                                "type": "marked_read",
                                "id": notification_id,
                            })
                    finally:
                        db.close()

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.exception("WebSocket error for user_id=%s: %s", user_id, e)
        manager.disconnect(websocket, user_id)
