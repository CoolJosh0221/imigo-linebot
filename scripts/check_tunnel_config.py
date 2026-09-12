"""Validate actual cloudflared routing offline, without account credentials."""

from pathlib import Path
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    compose = yaml.safe_load((ROOT / "compose.cloudflare.yaml").read_text())
    image = compose["services"]["cloudflared"]["image"]
    config = ROOT / "deploy/cloudflared/config.yml"
    command = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "-v",
        f"{config}:/etc/cloudflared/config.yml:ro",
        image,
        "tunnel",
        "--config",
        "/etc/cloudflared/config.yml",
        "ingress",
    ]
    subprocess.run(command + ["validate"], check=True, timeout=120)
    cases = {
        "https://webhook.imigo.tw/webhook": "http://backend:8000",
        "https://webhook.imigo.tw/webhook?retry=1": "http://backend:8000",
        "https://webhook.imigo.tw/": "http_status:404",
        "https://webhook.imigo.tw/health": "http_status:404",
        "https://webhook.imigo.tw/api/docs": "http_status:404",
        "https://webhook.imigo.tw/api/chat/history/synthetic-check": "http_status:404",
        "https://webhook.imigo.tw/webhook/": "http_status:404",
        "https://imigo.tw/webhook": "http_status:404",
    }
    for url, expected in cases.items():
        result = subprocess.run(
            command + ["rule", url],
            check=True,
            text=True,
            capture_output=True,
            timeout=30,
        )
        if f"service: {expected}" not in result.stdout:
            raise RuntimeError(f"Unexpected tunnel route for {url}: {result.stdout}")
        print(f"PASS {url} -> {expected}")


if __name__ == "__main__":
    main()
