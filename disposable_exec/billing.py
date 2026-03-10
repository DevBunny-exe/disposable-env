import os
import uuid
from datetime import datetime
from typing import Any

from .db import get_conn
from .plans import get_plan_quota


SUPPORTED_SUBSCRIPTION_STATUSES = {
    "active",
    "canceled",
    "past_due",
    "paused",
    "trialing",
    "incomplete",
}


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def normalize_plan(plan: str | None) -> str:
    if not plan:
        return "Free"

    value = str(plan).strip().lower()

    mapping = {
        "free": "Free",
        "starter": "Starter",
        "pro": "Pro",
        "scale": "Scale",
    }

    return mapping.get(value, "Free")


def normalize_status(status: str | None) -> str:
    if not status:
        return "active"

    value = str(status).strip().lower()

    mapping = {
        "active": "active",
        "cancelled": "canceled",
        "canceled": "canceled",
        "past_due": "past_due",
        "past-due": "past_due",
        "paused": "paused",
        "pause": "paused",
        "trialing": "trialing",
        "incomplete": "incomplete",
    }

    result = mapping.get(value, value)
    if result not in SUPPORTED_SUBSCRIPTION_STATUSES:
        return "active"
    return result


def normalize_email(email: str | None) -> str | None:
    if not email:
        return None
    value = str(email).strip().lower()
    return value or None


def extract_user_id(payload: dict[str, Any]) -> str | None:
    candidates = [
        payload.get("user_id"),
        payload.get("userId"),
        payload.get("customer_id"),
        payload.get("customerId"),
        payload.get("user", {}).get("id") if isinstance(payload.get("user"), dict) else None,
        payload.get("customer", {}).get("id") if isinstance(payload.get("customer"), dict) else None,
        payload.get("meta", {}).get("user_id") if isinstance(payload.get("meta"), dict) else None,
        payload.get("metadata", {}).get("user_id") if isinstance(payload.get("metadata"), dict) else None,
        payload.get("custom_data", {}).get("user_id") if isinstance(payload.get("custom_data"), dict) else None,
    ]
    for value in candidates:
        if value:
            return str(value)
    return None


def extract_email(payload: dict[str, Any]) -> str | None:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    attrs = data.get("attributes") if isinstance(data.get("attributes"), dict) else {}
    customer = payload.get("customer") if isinstance(payload.get("customer"), dict) else {}

    candidates = [
        payload.get("email"),
        payload.get("customer_email"),
        payload.get("customerEmail"),
        customer.get("email"),
        payload.get("user", {}).get("email") if isinstance(payload.get("user"), dict) else None,
        payload.get("meta", {}).get("email") if isinstance(payload.get("meta"), dict) else None,
        payload.get("metadata", {}).get("email") if isinstance(payload.get("metadata"), dict) else None,
        payload.get("custom_data", {}).get("email") if isinstance(payload.get("custom_data"), dict) else None,
        attrs.get("email"),
        attrs.get("customer_email"),
    ]

    for value in candidates:
        normalized = normalize_email(value)
        if normalized:
            return normalized
    return None


def extract_provider_subscription_id(payload: dict[str, Any]) -> str | None:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}

    candidates = [
        payload.get("subscription_id"),
        payload.get("subscriptionId"),
        payload.get("id"),
        data.get("id"),
        data.get("subscription_id"),
    ]
    for value in candidates:
        if value:
            return str(value)
    return None


def extract_plan(payload: dict[str, Any]) -> str:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    attrs = data.get("attributes") if isinstance(data.get("attributes"), dict) else {}

    candidates = [
        payload.get("plan"),
        payload.get("plan_name"),
        payload.get("variant_name"),
        payload.get("product_name"),
        data.get("plan"),
        attrs.get("plan"),
        payload.get("meta", {}).get("plan") if isinstance(payload.get("meta"), dict) else None,
        payload.get("metadata", {}).get("plan") if isinstance(payload.get("metadata"), dict) else None,
        payload.get("custom_data", {}).get("plan") if isinstance(payload.get("custom_data"), dict) else None,
    ]
    for value in candidates:
        if value:
            return normalize_plan(str(value))
    return "Free"


def extract_status(payload: dict[str, Any]) -> str:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    attrs = data.get("attributes") if isinstance(data.get("attributes"), dict) else {}

    candidates = [
        payload.get("status"),
        payload.get("subscription_status"),
        data.get("status"),
        attrs.get("status"),
    ]
    for value in candidates:
        if value:
            return normalize_status(str(value))
    return "active"


def extract_period_start(payload: dict[str, Any]) -> str | None:
    candidates = [
        payload.get("period_start"),
        payload.get("current_period_start"),
        payload.get("renews_at"),
        payload.get("starts_at"),
    ]
    for value in candidates:
        if value:
            return str(value)
    return None


def extract_period_end(payload: dict[str, Any]) -> str | None:
    candidates = [
        payload.get("period_end"),
        payload.get("current_period_end"),
        payload.get("ends_at"),
        payload.get("expires_at"),
        payload.get("renews_at"),
    ]
    for value in candidates:
        if value:
            return str(value)
    return None


def find_or_create_user_by_email(email: str) -> str:
    email = normalize_email(email)
    if not email:
        raise ValueError("email is required")

    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM users WHERE lower(email) = ?",
        (email,),
    ).fetchone()

    if row:
        user_id = row["id"]
        conn.close()
        return user_id

    user_id = f"user_{uuid.uuid4().hex[:12]}"
    conn.execute(
        """
        INSERT INTO users (id, email, status, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, email, "active", now_iso()),
    )
    conn.commit()
    conn.close()
    return user_id


def sync_api_keys_plan_for_user(user_id: str, plan: str):
    conn = get_conn()
    conn.execute(
        "UPDATE api_keys SET plan = ? WHERE user_id = ?",
        (plan, user_id),
    )
    conn.commit()
    conn.close()


def upsert_subscription(
    *,
    user_id: str,
    provider: str,
    provider_subscription_id: str,
    plan: str,
    status: str,
    period_start: str | None = None,
    period_end: str | None = None,
) -> dict[str, Any]:
    conn = get_conn()
    row = conn.execute(
        """
        SELECT id
        FROM subscriptions
        WHERE provider = ? AND provider_subscription_id = ?
        """,
        (provider, provider_subscription_id),
    ).fetchone()

    current_time = now_iso()
    quota_monthly = get_plan_quota(plan)

    if row:
        subscription_id = row["id"]
        conn.execute(
            """
            UPDATE subscriptions
            SET user_id = ?,
                plan = ?,
                status = ?,
                quota_monthly = ?,
                period_start = ?,
                period_end = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                user_id,
                plan,
                status,
                quota_monthly,
                period_start,
                period_end,
                current_time,
                subscription_id,
            ),
        )
    else:
        subscription_id = f"sub_{provider}_{provider_subscription_id}"
        conn.execute(
            """
            INSERT INTO subscriptions
            (
                id, user_id, provider, provider_subscription_id, plan, status,
                quota_monthly, period_start, period_end, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subscription_id,
                user_id,
                provider,
                provider_subscription_id,
                plan,
                status,
                quota_monthly,
                period_start,
                period_end,
                current_time,
                current_time,
            ),
        )

    conn.commit()
    conn.close()

    sync_api_keys_plan_for_user(user_id, plan)

    return {
        "ok": True,
        "subscription_id": subscription_id,
        "user_id": user_id,
        "provider": provider,
        "provider_subscription_id": provider_subscription_id,
        "plan": plan,
        "status": status,
        "quota_monthly": quota_monthly,
        "period_start": period_start,
        "period_end": period_end,
    }


def get_latest_subscription_for_user(user_id: str | None):
    if not user_id:
        return None

    conn = get_conn()
    row = conn.execute(
        """
        SELECT id, user_id, provider, provider_subscription_id, plan, status,
               quota_monthly, period_start, period_end, created_at, updated_at
        FROM subscriptions
        WHERE user_id = ?
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()
    conn.close()

    return dict(row) if row else None


def validate_webhook_secret(provider: str, provided_secret: str | None):
    env_map = {
        "paddle": "DISPOSABLE_EXEC_PADDLE_WEBHOOK_SECRET",
        "lemon": "DISPOSABLE_EXEC_LEMON_WEBHOOK_SECRET",
        "polar": "DISPOSABLE_EXEC_POLAR_WEBHOOK_SECRET",
        "stripe": "DISPOSABLE_EXEC_STRIPE_WEBHOOK_SECRET",
    }

    env_name = env_map[provider]
    expected = os.getenv(env_name, "").strip()

    if not expected:
        return False, f"{provider} webhook secret is not configured"

    if not provided_secret or provided_secret.strip() != expected:
        return False, f"invalid {provider} webhook secret"

    return True, None


def process_subscription_webhook(provider: str, payload: dict[str, Any]):
    user_id = extract_user_id(payload)
    if not user_id:
        email = extract_email(payload)
        if email:
            user_id = find_or_create_user_by_email(email)

    if not user_id:
        return {"ok": False, "error": "missing user_id_or_email"}

    provider_subscription_id = extract_provider_subscription_id(payload)
    if not provider_subscription_id:
        return {"ok": False, "error": "missing provider_subscription_id"}

    plan = extract_plan(payload)
    status = extract_status(payload)
    period_start = extract_period_start(payload)
    period_end = extract_period_end(payload)

    return upsert_subscription(
        user_id=user_id,
        provider=provider,
        provider_subscription_id=provider_subscription_id,
        plan=plan,
        status=status,
        period_start=period_start,
        period_end=period_end,
    )


def handle_paddle_webhook(payload: dict[str, Any]):
    return process_subscription_webhook("paddle", payload)


def handle_lemon_webhook(payload: dict[str, Any]):
    return process_subscription_webhook("lemon", payload)


def handle_polar_webhook(payload: dict[str, Any]):
    return process_subscription_webhook("polar", payload)


def handle_stripe_webhook(payload: dict[str, Any]):
    return process_subscription_webhook("stripe", payload)