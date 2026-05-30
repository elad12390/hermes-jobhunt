# 2. Telegram Setup

Telegram is how Hermes delivers everything to you - morning briefings, job matches, alerts. The jobhunt setup uses two separate Telegram bots, each running on its own Hermes profile.

## Architecture: two bots, two profiles

```
Eladiut (default profile)          Merc (jobs profile)
├── Bot token: 8755794348          ├── Bot token: 8491442386
├── Hermes profile: default        ├── Hermes profile: jobs
├── Gateway: hermes-gateway        ├── Gateway: hermes-gateway-jobs
├── Cron: Morning Briefing only    ├── Cron: Scraper, Curator, Enricher
└── Personal assistant             └── Job pipeline only

Both deliver to → Hermes-Jobs Telegram group
```

**Why separate?** Memory, config, session context, and model chains are fully independent. Merc owns the job pipeline; Eladiut handles personal tasks. If one goes down, the other keeps running.

## Create your Telegram bots

Do this twice - once for each bot:

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Pick a name and username for each (e.g. "My Assistant" + "My Jobs")
4. BotFather gives you a **token** for each - save them

> After creating both bots, set **Privacy Mode ON** for each via @BotFather → Bot Settings → Group Privacy → Turn on. This means bots only see @mentions and /commands in groups (not all chatter). Cron deliveries still work because they're send operations, not reads.

## Create a dedicated jobs group

1. Create a new Telegram group (e.g. "Hermes Jobs")
2. Add BOTH bots to the group
3. Send any message in the group
4. In your Hermes session, run `/platforms` to find the group chat ID (a negative number like `-1001234567890`)

Save the group chat ID - all cron jobs deliver here.

## Configure Hermes profiles

**Default profile** (`~/.hermes/.env`):
```
TELEGRAM_BOT_TOKEN=your_default_bot_token_here
```

**Jobs profile** (`~/.hermes/profiles/jobs/.env`):
```
TELEGRAM_BOT_TOKEN=your_jobs_bot_token_here
```

## Start both gateways

```bash
# Default profile gateway
hermes gateway install
hermes gateway start

# Jobs profile gateway
hermes --profile jobs gateway install --force
hermes --profile jobs gateway start
```

Verify both are running:
```bash
systemctl --user is-active hermes-gateway
systemctl --user is-active hermes-gateway-jobs
```

## Verify

Send a message to each bot in DMs - both should respond. Then send a message in the group mentioning either bot - it should respond.

---

→ [Next: Google Workspace Setup](03-google-workspace.md)
