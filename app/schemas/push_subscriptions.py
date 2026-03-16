from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionCreate(BaseModel):
    """Payload sent by the Angular SwPush.requestSubscription() → toJSON()."""
    endpoint: str
    keys: PushSubscriptionKeys


class PushSubscriptionResponse(BaseModel):
    id: int
    usuario_id: int
    endpoint: str
    created_at: datetime

    class Config:
        from_attributes = True


class SendPushRequest(BaseModel):
    """Body for admin/server-side manual push dispatch."""
    usuario_id: int
    title: str
    body: str
    url: Optional[str] = "/app/home"
