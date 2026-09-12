import base64
import hashlib
import hmac
import json
from unittest.mock import AsyncMock

import httpx
import pytest
from linebot.v3.webhook import WebhookParser

import main
from scripts.check_webhook import VERIFICATION_BODY, check_webhook

SECRET = "synthetic-test-secret"


def signature(body):
    return base64.b64encode(
        hmac.new(SECRET.encode(), body, hashlib.sha256).digest()
    ).decode()


@pytest.mark.asyncio
async def test_signed_empty_event_is_accepted_without_calling_line(monkeypatch):
    monkeypatch.setattr(main, "get_line_parser", lambda: WebhookParser(SECRET))
    handler = AsyncMock()
    monkeypatch.setattr(main, "handle_message", handler)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=main.app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/webhook",
            content=VERIFICATION_BODY,
            headers={"X-Line-Signature": signature(VERIFICATION_BODY)},
        )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    handler.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "header", ["", "not-a-valid-signature", signature(b'{ "events": [] }')]
)
async def test_signature_is_checked_against_exact_body(monkeypatch, header):
    monkeypatch.setattr(main, "get_line_parser", lambda: WebhookParser(SECRET))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=main.app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/webhook", content=VERIFICATION_BODY, headers={"X-Line-Signature": header}
        )
    assert response.status_code == 400


def test_candidate_check_sends_only_empty_events_and_keeps_signature_local():
    calls = []

    def route(request):
        calls.append(request)
        if request.method == "POST":
            assert request.content == VERIFICATION_BODY
            assert json.loads(request.content) == {"events": []}
            if request.headers.get("X-Line-Signature") == signature(request.content):
                return httpx.Response(200, json={"status": "ok"})
            return httpx.Response(400)
        return httpx.Response(404)

    with httpx.Client(transport=httpx.MockTransport(route)) as client:
        check_webhook("https://webhook.imigo.tw/webhook", SECRET, client)
    assert len(calls) == 6
    assert all(request.url.host == "webhook.imigo.tw" for request in calls)
    assert all(SECRET not in str(request.headers) for request in calls)


@pytest.mark.parametrize("failure", ["redirect", "unsigned", "public_api"])
def test_candidate_check_rejects_broken_or_overbroad_routing(failure):
    def route(request):
        if request.method == "POST" and request.headers.get("X-Line-Signature"):
            if failure == "redirect":
                return httpx.Response(
                    308, headers={"Location": "https://other.example/webhook"}
                )
            return httpx.Response(200, json={"status": "ok"})
        if request.method == "POST":
            return httpx.Response(200 if failure == "unsigned" else 400)
        return httpx.Response(200 if failure == "public_api" else 404)

    with httpx.Client(transport=httpx.MockTransport(route)) as client:
        with pytest.raises(ValueError):
            check_webhook("https://webhook.imigo.tw/webhook", SECRET, client)


@pytest.mark.parametrize(
    "url",
    [
        "http://webhook.imigo.tw/webhook",
        "https://webhook.imigo.tw/",
        "https://user:secret@webhook.imigo.tw/webhook",
    ],
)
def test_candidate_check_rejects_invalid_urls_before_network_access(url):
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda request: pytest.fail("unexpected network request")
        )
    ) as client:
        with pytest.raises(ValueError):
            check_webhook(url, SECRET, client)
