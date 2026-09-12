"""Check a candidate webhook with a signed empty event; never changes LINE settings."""

import argparse
import base64
import hashlib
import hmac
import os
from urllib.parse import urlsplit

import httpx
from dotenv import load_dotenv

VERIFICATION_BODY = b'{"events":[]}'


def check_webhook(url: str, secret: str, client: httpx.Client) -> None:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.path != "/webhook"
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "Use an HTTPS URL ending in /webhook, without credentials or a query"
        )
    if not secret:
        raise ValueError("LINE_CHANNEL_SECRET is required to verify the webhook")
    signature = base64.b64encode(
        hmac.new(secret.encode(), VERIFICATION_BODY, hashlib.sha256).digest()
    ).decode()
    response = client.post(
        url,
        content=VERIFICATION_BODY,
        headers={"Content-Type": "application/json", "X-Line-Signature": signature},
        follow_redirects=False,
    )
    if response.status_code != 200 or response.json() != {"status": "ok"}:
        raise ValueError(
            f"Signed webhook verification failed (HTTP {response.status_code})"
        )
    # A reachable server must still reject unauthenticated messages.
    response = client.post(url, content=VERIFICATION_BODY, follow_redirects=False)
    if response.status_code != 400:
        raise ValueError(
            f"Unsigned webhook was not rejected (HTTP {response.status_code})"
        )
    for path in ("/", "/health", "/api/docs", "/api/chat/history/synthetic-check"):
        response = client.get(
            f"{parsed.scheme}://{parsed.netloc}{path}", follow_redirects=False
        )
        if response.status_code != 404:
            raise ValueError(
                f"Non-webhook route {path} is exposed (HTTP {response.status_code})"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://webhook.imigo.tw/webhook")
    args = parser.parse_args()
    load_dotenv()
    try:
        with httpx.Client(timeout=15) as client:
            check_webhook(args.url, os.getenv("LINE_CHANNEL_SECRET", ""), client)
    except (ValueError, httpx.HTTPError) as error:
        print(f"Webhook verification failed: {error}")
        return 1
    print("Signed webhook accepted; unsigned events and non-webhook routes blocked.")
    print(
        "No LINE webhook settings were changed. The candidate is ready for LINE's Verify check."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
