# Dynamic DNS (DDNS) Setup Guide

This guide explains how to set up Dynamic DNS for your IMIGO API when you have a dynamic (changing) IP address.

## What is DDNS?

Dynamic DNS automatically updates your DNS records when your public IP address changes, allowing `api.imigo.tw` to always point to your current IP address.

## Supported DDNS Providers

The DDNS updater supports 50+ providers. Here are the most popular free options:

1. **Cloudflare** - Best if your domain is already on Cloudflare (Recommended)
2. **DuckDNS** - Simplest, completely free, no account needed
3. **No-IP** - Popular, free tier available
4. **Dynu** - Free with more features

## Option 1: Cloudflare (Recommended if you own imigo.tw)

Cloudflare offers free DNS hosting with API access for dynamic updates.

### Step 1: Transfer Domain to Cloudflare (if not already)

1. Sign up at https://cloudflare.com (free)
2. Add your domain `imigo.tw`
3. Update nameservers at your domain registrar to Cloudflare's nameservers
4. Wait for DNS propagation (up to 24 hours)

### Step 2: Get Cloudflare API Token

1. Log in to Cloudflare Dashboard
2. Go to: **Profile** → **API Tokens** → **Create Token**
3. Use template: **Edit zone DNS**
4. Zone Resources: Include → Specific zone → `imigo.tw`
5. Click **Continue to summary** → **Create Token**
6. **Copy the token** (you won't see it again!)

### Step 3: Get Zone Identifier

1. In Cloudflare Dashboard, select your domain `imigo.tw`
2. Scroll down on the Overview page
3. Find **Zone ID** on the right sidebar
4. Copy the Zone ID

### Step 4: Configure DDNS

Edit `ddns/config.json`:

```json
{
  "settings": [
    {
      "provider": "cloudflare",
      "zone_identifier": "YOUR_ZONE_ID_FROM_STEP_3",
      "domain": "api.imigo.tw",
      "host": "@",
      "ttl": 600,
      "token": "YOUR_API_TOKEN_FROM_STEP_2",
      "ip_version": "ipv4"
    }
  ]
}
```

### Step 5: Create DNS Record in Cloudflare

1. Go to **DNS** → **Records** in Cloudflare
2. Click **Add record**
3. Type: `A`
4. Name: `api`
5. IPv4 address: `1.1.1.1` (temporary, DDNS will update this)
6. Proxy status: **DNS only** (turn off orange cloud)
7. TTL: Auto
8. Click **Save**

---

## Option 2: DuckDNS (Easiest, No Domain Transfer Needed)

DuckDNS is the simplest option. You'll use a subdomain like `yourname.duckdns.org` as an intermediate.

### Step 1: Get DuckDNS Token

1. Go to https://www.duckdns.org
2. Sign in with Google/GitHub/etc.
3. Create a subdomain (e.g., `imigo-api`)
4. Copy your **token** from the top of the page

### Step 2: Configure DDNS

Copy the example config:

```bash
cp ddns/config.json.duckdns ddns/config.json
```

Edit `ddns/config.json`:

```json
{
  "settings": [
    {
      "provider": "duckdns",
      "domain": "imigo-api",
      "token": "YOUR_DUCKDNS_TOKEN",
      "ip_version": "ipv4"
    }
  ]
}
```

### Step 3: Configure DNS CNAME

In your domain registrar (where you manage imigo.tw DNS):

1. Add a CNAME record:
   - Name: `api`
   - Points to: `imigo-api.duckdns.org`
   - TTL: 600 (or automatic)

Now `api.imigo.tw` → `imigo-api.duckdns.org` → Your dynamic IP

---

## Option 3: No-IP

No-IP offers free dynamic DNS with hostname management.

### Step 1: Create No-IP Account

1. Sign up at https://www.noip.com (free account)
2. Verify your email
3. Create a hostname (can use your own domain if you add it to No-IP)

### Step 2: Add Your Domain (Optional)

If you want to use `api.imigo.tw`:

1. Go to **Dynamic DNS** → **No-IP Hostnames**
2. Click **Add a Hostname**
3. Enter `api.imigo.tw` as hostname
4. Follow verification steps to prove domain ownership

### Step 3: Configure DDNS

Copy the example config:

```bash
cp ddns/config.json.noip ddns/config.json
```

Edit `ddns/config.json`:

```json
{
  "settings": [
    {
      "provider": "noip",
      "host": "api.imigo.tw",
      "username": "YOUR_NOIP_EMAIL",
      "password": "YOUR_NOIP_PASSWORD",
      "ip_version": "ipv4"
    }
  ]
}
```

---

## Option 4: Dynu

Dynu offers free DDNS with more features.

### Step 1: Create Dynu Account

1. Sign up at https://www.dynu.com (free)
2. Verify your email

### Step 2: Add Your Domain

1. Go to **DDNS Services** → **Add**
2. Choose to use your own domain `api.imigo.tw`
3. Follow the verification process

### Step 3: Configure DDNS

Copy the example config:

```bash
cp ddns/config.json.dynu ddns/config.json
```

Edit `ddns/config.json`:

```json
{
  "settings": [
    {
      "provider": "dynu",
      "host": "api.imigo.tw",
      "username": "YOUR_DYNU_EMAIL",
      "password": "YOUR_DYNU_PASSWORD",
      "ip_version": "ipv4"
    }
  ]
}
```

---

## Starting the DDNS Updater

Once you've configured your preferred provider:

### Step 1: Start Services

```bash
docker-compose up -d
```

The DDNS updater will:
- Check your public IP every 5 minutes
- Update DNS records when IP changes
- Log all updates

### Step 2: Check DDNS Status

Visit the DDNS web interface:

```
http://localhost:8888
```

Or check logs:

```bash
docker-compose logs -f ddns-updater
```

You should see:

```
INFO IP address updated successfully
```

### Step 3: Verify DNS

Wait 2-3 minutes, then check your DNS:

```bash
# Check what IP api.imigo.tw resolves to
nslookup api.imigo.tw

# Or
dig api.imigo.tw
```

It should match your current public IP.

---

## Multiple Domains/Subdomains

You can update multiple domains by adding more entries to `settings`:

```json
{
  "settings": [
    {
      "provider": "cloudflare",
      "zone_identifier": "YOUR_ZONE_ID",
      "domain": "api.imigo.tw",
      "host": "@",
      "token": "YOUR_TOKEN",
      "ip_version": "ipv4"
    },
    {
      "provider": "cloudflare",
      "zone_identifier": "YOUR_ZONE_ID",
      "domain": "traefik.imigo.tw",
      "host": "@",
      "token": "YOUR_TOKEN",
      "ip_version": "ipv4"
    }
  ]
}
```

---

## Troubleshooting

### DDNS updater not starting

Check logs:

```bash
docker-compose logs ddns-updater
```

Common issues:
- Invalid credentials
- Missing configuration file
- Incorrect provider name

### IP not updating

1. Check your public IP:
   ```bash
   curl ifconfig.me
   ```

2. Check DDNS logs:
   ```bash
   docker-compose logs -f ddns-updater
   ```

3. Verify configuration in `ddns/config.json`

### DNS not resolving

1. Wait 5-10 minutes for DNS propagation
2. Check TTL settings (lower = faster updates)
3. Verify DNS record exists in your provider's dashboard

### Web UI not accessible

The web UI runs on port 8888:

```
http://localhost:8888
```

If using a remote server:

```
http://YOUR_SERVER_IP:8888
```

---

## Security Notes

1. **Protect your configuration**:
   - `ddns/config.json` contains sensitive tokens
   - It's already in `.gitignore`
   - Never commit it to version control

2. **Use specific permissions**:
   - For Cloudflare, use API tokens (not Global API Key)
   - Limit token permissions to DNS editing only
   - Set expiration dates on tokens when possible

3. **Firewall the web UI** (optional):
   - The DDNS web UI is on port 8888
   - Consider blocking external access:
     ```bash
     sudo ufw deny 8888
     ```

---

## Update Frequency

The DDNS updater checks your IP every **5 minutes** by default.

To change this, edit `docker-compose.yaml`:

```yaml
environment:
  - PERIOD=10m  # Check every 10 minutes
  - UPDATE_COOLDOWN_PERIOD=5m  # Minimum time between updates
```

---

## Alternative: Router-Based DDNS

Some routers have built-in DDNS support. If your router supports it:

1. Configure DDNS in your router settings
2. You can skip the DDNS updater service
3. Remove or disable the `ddns-updater` service in docker-compose.yaml

---

## Next Steps

After DDNS is configured and running:

1. Verify DNS resolves correctly
2. Continue with the main deployment (see `DEPLOYMENT.md`)
3. SSL certificates will be provisioned automatically once DNS is working

---

## Support

For DDNS updater issues:
- GitHub: https://github.com/qdm12/ddns-updater
- Check logs: `docker-compose logs ddns-updater`
- Web UI: `http://localhost:8888`

For DNS provider issues:
- Cloudflare: https://dash.cloudflare.com
- DuckDNS: https://www.duckdns.org
- No-IP: https://www.noip.com/support
- Dynu: https://www.dynu.com/en-US/Support
