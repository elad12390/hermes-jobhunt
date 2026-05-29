# 2. Telegram Setup

Telegram is how Hermes delivers everything to you - morning briefings, job matches, alerts. You need a bot and a group.

## Create a Telegram bot

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Pick a name (e.g. "My Hermes") and a username (e.g. `myhermes_bot`)
4. BotFather gives you a **token** - looks like `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

Save it, you'll need it in a minute.

## Get your Telegram user ID

1. Search for **@userinfobot** in Telegram
2. Send it any message
3. It replies with your user ID (a number like `86849198`)

## Configure Hermes with Telegram

Add to `~/.hermes/.env`:

```
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE   # from @BotFather
TELEGRAM_ALLOWED_USERS=YOUR_USER_ID
TELEGRAM_HOME_CHANNEL=YOUR_USER_ID
```

Then start the gateway:

```bash
hermes gateway install   # install as background service
hermes gateway start
hermes gateway status    # should show "active (running)"
```

Send your bot a message in Telegram - it should reply.

## Create a dedicated jobs group

You want job alerts in a separate group (not your DMs) so they don't clutter your personal chat.

1. Create a new Telegram group (e.g. "Hermes Jobs")
2. Add your bot to the group as a member
3. Send any message in the group (wakes the bot up)
4. In your Hermes session, run:
   ```
   hermes send_message action=list
   ```
   The group should now appear in the list with its chat ID (a negative number like `-5296852184`)

Save the group chat ID - you'll use it when configuring cron job delivery.

## Verify

Send a test message to your bot in DMs - it should respond. Then send a message in the group mentioning the bot - it should respond there too.

---

→ [Next: Google Workspace Setup](03-google-workspace.md)
