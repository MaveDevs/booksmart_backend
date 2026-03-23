"""
Push notification sender service.

Uses pywebpush to dispatch Web Push messages to subscribed devices.
The VAPID keys must be set as environment variables:
    VAPID_PRIVATE_KEY  — the private key generated with web-push
    VAPID_SUBJECT      — mailto: or https: claim (e.g. mailto:admin@booksmart.com)

The public key in the frontend (environment.ts) must match the private key here.
"""

import json
import logging
import os
from typing import Any, Dict

from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)

VAPID_PRIVATE_KEY = os.getenv(
    "VAPID_PRIVATE_KEY",
    "t5MCRJxTDacg3qV7Qz2irp2hMFNjageHYgxP4TwNSuc",
)
VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", "mailto:admin@booksmart.com")


def send_push(
    endpoint: str,
    p256dh: str,
    auth: str,
    title: str,
    body: str,
    url: str = "/app/home",
) -> bool:
    """
    Send a push notification to a single subscription.
    Returns True on success, False if the subscription is expired/invalid.
    Raises on unrecoverable errors.
    """
    subscription_info: Dict[str, Any] = {
        "endpoint": endpoint,
        "keys": {"p256dh": p256dh, "auth": auth},
    }
    payload = json.dumps({"title": title, "body": body, "url": url})

    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBJECT},
        )
        return True
    except WebPushException as ex:
        # 404 / 410 means the subscription is gone from the browser
        status = getattr(ex.response, "status_code", None)
        if status in (404, 410):
            logger.info("Push subscription expired (status %s) — endpoint: %s", status, endpoint)
            return False
        logger.error("WebPush failed (status %s): %s", status, ex)
        raise
