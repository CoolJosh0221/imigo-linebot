# LINE webhooks at webhook.imigo.tw

This setup publishes `https://webhook.imigo.tw/webhook` through a named Cloudflare
Tunnel to the local bot. The website can remain hosted on Vercel and inference
stays on the GPU machine. The machine and its Internet connection must remain online.

The repository contains the connector and routing configuration. Merging it does
not create a Cloudflare account, move DNS, start a tunnel, or update LINE settings.
The hostname will not work until the account steps below are complete.

## 1. Prepare the domain and named tunnel

`imigo.tw` used Vercel nameservers when checked on 2026-09-13. For Cloudflare's
standard tunnel setup, add the domain to your Cloudflare account. Copy all existing
DNS records, including the Vercel website records and any email records, before
changing nameservers at the registrar. Confirm the website still works and the
Cloudflare zone is active. The registrar and website hosting do not need to move.

Install `cloudflared` using [Cloudflare's installation instructions](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/).
Create a **locally managed** named tunnel so the rules in this repository control routing:

```bash
cloudflared tunnel login
cloudflared tunnel create imigo-linebot
cloudflared tunnel route dns imigo-linebot webhook.imigo.tw
```

The login opens a browser for your Cloudflare account. Creation prints the tunnel
UUID and writes its credential JSON under `~/.cloudflared`. Keep the account-wide
`cert.pem` there; only the tunnel-specific JSON is needed by the runtime container.

```bash
mkdir -p .secrets
chmod 700 .secrets
# Replace YOUR-TUNNEL-UUID with the ID returned by the create command.
cp ~/.cloudflared/YOUR-TUNNEL-UUID.json .secrets/cloudflared.json
chmod 600 .secrets/cloudflared.json
id -u
id -g
```

Add to `.env`, using the UUID and the two numeric IDs printed above:

```dotenv
CLOUDFLARE_TUNNEL_ID=YOUR-TUNNEL-UUID
CLOUDFLARE_TUNNEL_CREDENTIALS=./.secrets/cloudflared.json
CLOUDFLARED_UID=1000
CLOUDFLARED_GID=1000
```

`.secrets/` is excluded from Git and Docker build contexts. The connector runs
with the file owner's UID/GID so it can read a mode-600 credential file. This setup
uses a tunnel JSON credential, not a dashboard-generated tunnel token.

## 2. Validate and start the deployment

Before creating any Cloudflare resources, the checked-in routing rules can be
tested with Docker and the Python dependencies installed:

```bash
.venv/bin/python -m scripts.check_tunnel_config
```

This uses the connector version pinned in the Compose file, with container
networking disabled. It checks allowed and denied URLs without tunnel credentials.

Run from the repository root. The override leaves ngrok behind an explicit
`ngrok` profile, so the default combined stack uses only Cloudflare for public ingress.

```bash
docker compose -f docker-compose.yaml -f compose.cloudflare.yaml config --quiet
docker compose -f docker-compose.yaml -f compose.cloudflare.yaml run --rm --no-deps \
  cloudflared tunnel --config /etc/cloudflared/config.yml ingress validate
docker compose -f docker-compose.yaml -f compose.cloudflare.yaml up -d --build
docker compose -f docker-compose.yaml -f compose.cloudflare.yaml ps
docker compose -f docker-compose.yaml -f compose.cloudflare.yaml logs --tail 50 cloudflared
```

If ngrok is already running in this compose project, explicitly stop it after
validating the new endpoint: `docker compose -f docker-compose.yaml stop ngrok`.
Do not run two model servers on the same GPU or two stacks on the same local ports;
replace the previous stack as part of a planned rollout. Preserve its database.

For a Podman installation with a Compose-compatible provider, use
`podman compose -f podman-compose.yaml -f compose.cloudflare.yaml` in place of
`docker compose -f docker-compose.yaml -f compose.cloudflare.yaml`. GPU access
still depends on the existing NVIDIA/Podman configuration.

The backend must become healthy before the connector starts. Only the exact host
`webhook.imigo.tw` and path `/webhook` reach the backend. Everything else receives
404, including `/health`, `/api/docs`, and chat history. Local debugging remains
available at `http://127.0.0.1:8000/health`. Published container ports bind to loopback.

Do not add an interactive Cloudflare Access login or browser challenge to this
webhook route; LINE cannot complete them. The application checks LINE's signature
against the unmodified request body. No application rewrite is required.

## 3. Verify, then activate LINE delivery

```bash
.venv/bin/python -m scripts.check_webhook
```

The check reads `LINE_CHANNEL_SECRET` locally and sends a signed empty event.
It also checks rejection of unsigned events and inaccessible non-webhook routes.
It sends no chat messages and does not change the registered LINE webhook.

After it passes, set the webhook URL in the channel's LINE Developers console to
`https://webhook.imigo.tw/webhook`, select **Verify**, and enable **Use webhook**.
Keep the previous endpoint recorded until the new endpoint has passed verification.

If validation fails, leave LINE pointing at the previous working endpoint and
check tunnel logs, the active DNS zone, the credential UUID, and backend health.
If a completed cutover must be rolled back, restore the previous verified LINE
endpoint and start its original deployment/tunnel configuration.

## References

- [Cloudflare locally managed tunnels](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/create-local-tunnel/)
- [Cloudflare ingress rules and validation](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/configuration-file/)
- [LINE HTTPS requirements](https://developers.line.biz/en/docs/messaging-api/ssl-tls-spec-of-the-webhook-source/)
- [LINE webhook verification](https://developers.line.biz/en/docs/messaging-api/verify-webhook-url/)
