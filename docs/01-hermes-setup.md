# 1. Hermes Setup

Hermes Agent is the AI runtime that powers everything in this guide. It runs in your terminal and connects to your messaging platforms, tools, and LLM providers.

## Install Hermes

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

After install, restart your shell and run:

```bash
hermes doctor
```

This checks that all dependencies are present.

## Pick a model and provider

Hermes works with any LLM. For job hunting workflows you want a model that is:

- **Good at tool use** (reads files, calls APIs, patches YAML)
- **Has a large context window** (reading job descriptions + your memory)
- **Reliable streaming** (Anthropic Claude models work best for long cron tasks)

**Recommended for daily use:** any Claude model via Anthropic (claude-sonnet or better)

**Free/cheap options:** OpenRouter with DeepSeek V3/V4, Ollama for local models

Configure your model:

```bash
hermes setup
# or pick interactively:
hermes model
```

Set your API key in `~/.hermes/.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...
# OR
OPENROUTER_API_KEY=sk-or-...
```

## Configure fallbacks

If your primary provider hits a rate limit, Hermes falls back automatically. Edit `~/.hermes/config.yaml`:

```yaml
model:
  default: claude-sonnet-4-5
  provider: anthropic

fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4-5
```

> **Important for cron jobs:** Pin important crons to a reliable provider (e.g. Anthropic directly) to avoid mid-run streaming failures. See the troubleshooting doc.

## Set your timezone

```bash
hermes config set timezone Asia/Jerusalem
# or your own: America/New_York, Europe/London, etc.
```

## Verify everything works

```bash
hermes chat -q "What can you do?"
```

You should get a response. If not, run `hermes doctor --fix`.

---

→ [Next: Telegram Setup](02-telegram-setup.md)
