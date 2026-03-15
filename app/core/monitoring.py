import os

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return float(value)
    except ValueError:
        return default


def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", os.getenv("ENV", "development")),
        release=os.getenv("SENTRY_RELEASE"),
        traces_sample_rate=_get_float_env("SENTRY_TRACES_SAMPLE_RATE", 0.0),
        profiles_sample_rate=_get_float_env("SENTRY_PROFILES_SAMPLE_RATE", 0.0),
        send_default_pii=os.getenv("SENTRY_SEND_DEFAULT_PII", "false").lower() == "true",
        integrations=[FastApiIntegration()],
    )