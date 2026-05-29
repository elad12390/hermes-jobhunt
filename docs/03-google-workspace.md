# 3. Google Workspace Setup

This connects Hermes to your Gmail and Google Calendar. Used for the morning briefing (new emails, today's events) and any calendar-aware tasks.

## Overview

Hermes uses Google OAuth to read your Gmail and Calendar. You need to create a free Google Cloud project and authorize it once. After that, tokens refresh automatically.

> **Note:** Google blocks browser-based login via automation. This is intentional - you authorize via a one-time URL flow, not by logging in through a browser.

## Step 1: Create a Google Cloud project

1. Go to https://console.cloud.google.com/projectselector2/home/dashboard
2. Create a new project (e.g. "Hermes Agent")
3. Enable these APIs from the API Library (https://console.cloud.google.com/apis/library):
   - Gmail API
   - Google Calendar API
   - Google Drive API (optional)
   - Google Sheets API (optional)
   - Google Docs API (optional)
   - People API

## Step 2: Create OAuth credentials

1. Go to https://console.cloud.google.com/apis/credentials
2. Click **Create Credentials → OAuth 2.0 Client ID**
3. Application type: **Desktop app**
4. Click Create, then download the JSON file

The JSON looks like this (you don't need to create this yourself, just download it):
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    ...
  }
}
```

## Step 3: Add yourself as a test user

Since the app is in "Testing" mode:

1. Go to https://console.cloud.google.com/auth/audience
2. Under "Test users", add your Google email address

> **Token expiry note:** In Testing mode, tokens expire every 7 days. You'll need to re-auth weekly. To avoid this, publish your app (https://console.cloud.google.com/auth/overview) - it stays in "unverified" state but tokens last 6 months.

## Step 4: Configure Hermes

Save your client credentials:

```bash
# Save the downloaded JSON as:
cp ~/Downloads/client_secret_*.json ~/.hermes/google_client_secret.json
```

Run the setup script:

```bash
GSETUP="python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --client-secret ~/.hermes/google_client_secret.json
```

## Step 5: Authorize (one-time)

```bash
$GSETUP --auth-url
```

This prints a URL. Open it in your browser, sign in with your Google account, approve the permissions. Your browser will redirect to `http://localhost:1/?code=...` - copy the **entire URL** from the address bar.

Then paste it back:

```bash
$GSETUP --auth-code "http://localhost:1/?code=4/0A..."
```

## Step 6: Verify

```bash
$GSETUP --check
# Should print: AUTHENTICATED
```

Test it:

```bash
GAPI="python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI calendar list
$GAPI gmail search "is:unread" --max 5
```

## Multi-account support (optional)

If you want Hermes to also check a partner's or household email:

```bash
$GSETUP --account partner --auth-url
# follow same steps, paste back code
$GSETUP --account partner --auth-code "..."

# Use with:
$GAPI --account partner calendar list
```

---

→ [Next: Obsidian Setup](04-obsidian-setup.md)
