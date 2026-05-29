# 5. Proxy Setup (Optional but Recommended)

LinkedIn has bot detection. Without a proxy, the scraper will eventually get flagged or rate-limited. A residential proxy routes your requests through real home IP addresses, making the traffic look like a real user.

## Do you need this?

- **Without proxy:** Works fine initially. May get challenged or blocked after a few days of regular scraping.
- **With proxy:** Much more reliable long-term. Looks like a real user from your country.

## Residential proxy providers

| Provider | Notes |
|----------|-------|
| [Evomi](https://evomi.com) | Good value, rotating residential IPs |
| [Bright Data](https://brightdata.com) | Industry standard, more expensive |
| [Oxylabs](https://oxylabs.io) | High quality, enterprise pricing |
| [IPRoyal](https://iproyal.com) | Budget option |
| [Smartproxy](https://smartproxy.com) | Good balance of price/quality |

Most offer a pay-as-you-go plan. For this use case (scraping ~10 pages every 2 hours) you'll use very little bandwidth - around 50-100MB/day.

## Proxy URL format

Most providers give you a URL in this format:

```
http://USERNAME:PASSWORD@PROXY_HOST:PORT
```

Example (replace with your actual credentials):

```
http://myuser:mypassword123@proxy.provider.com:1000
```

## Configure the scraper

In `scripts/linkedin-scraper.py`, set your proxy URL:

```python
PROXY_URL = "http://YOUR_USERNAME:YOUR_PASSWORD@YOUR_PROXY_HOST:YOUR_PORT"
```

Or set it in `~/.hermes/.env` and read it in the script:

```
LINKEDIN_PROXY_URL=http://YOUR_USERNAME:YOUR_PASSWORD@YOUR_PROXY_HOST:YOUR_PORT
```

Then in the script:
```python
PROXY_URL = os.environ.get("LINKEDIN_PROXY_URL", "")
if PROXY_URL:
    os.environ["HTTP_PROXY"] = PROXY_URL
    os.environ["HTTPS_PROXY"] = PROXY_URL
    os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1"
```

## Test the proxy

```bash
curl --proxy "http://USER:PASS@HOST:PORT" https://httpbin.org/ip
```

You should see an IP address that is NOT your home IP.

## Note on MCP tools

If you use MCP tools (like the web-research-assistant for company research), make sure to exclude localhost from proxy routing or SearXNG local search will break:

In `~/.hermes/config.yaml` under your MCP server:
```yaml
mcp_servers:
  web-research-assistant:
    env:
      NO_PROXY: localhost,127.0.0.1,::1
      HTTP_PROXY: http://USER:PASS@HOST:PORT
      HTTPS_PROXY: http://USER:PASS@HOST:PORT
```

---

→ [Next: Job Pipeline](06-job-pipeline.md)
