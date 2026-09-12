"""Exercise real Compose merging without a Docker daemon or real credentials."""

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("base", ["docker-compose.yaml", "podman-compose.yaml"])
def test_cloudflare_overlay_routes_only_through_named_connector(tmp_path, base):
    if not shutil.which("docker"):
        pytest.skip("Docker Compose CLI is not installed")
    for name in (base, "compose.cloudflare.yaml"):
        shutil.copyfile(ROOT / name, tmp_path / name)
    (tmp_path / ".env").write_text(
        "LINE_CHANNEL_SECRET=test\nLINE_CHANNEL_ACCESS_TOKEN=test\n"
    )
    env = dict(
        os.environ,
        CLOUDFLARE_TUNNEL_ID="00000000-0000-0000-0000-000000000001",
        CLOUDFLARE_TUNNEL_CREDENTIALS="./.secrets/cloudflared.json",
    )
    result = subprocess.run(
        [
            "docker",
            "compose",
            "--project-directory",
            str(tmp_path),
            "-f",
            str(tmp_path / base),
            "-f",
            str(tmp_path / "compose.cloudflare.yaml"),
            "config",
            "--format",
            "json",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    services = json.loads(result.stdout)["services"]
    assert "cloudflared" in services
    assert "ngrok" not in services  # Explicit profile is inactive.
    connector = services["cloudflared"]
    assert connector["command"][-1] == env["CLOUDFLARE_TUNNEL_ID"]
    assert connector["depends_on"]["backend"]["condition"] == "service_healthy"
    assert not connector.get("ports")
    assert all(volume["read_only"] for volume in connector["volumes"])
    assert {volume["target"] for volume in connector["volumes"]} == {
        "/etc/cloudflared/config.yml",
        "/run/secrets/cloudflared.json",
    }
    for service in services.values():
        assert all(port["host_ip"] == "127.0.0.1" for port in service.get("ports", []))
