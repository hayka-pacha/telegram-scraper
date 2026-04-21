# 📱 Telegram Scraper

Scrape all messages from your Telegram groups, channels, and private conversations.

## How it works

This script uses **[Telethon](https://github.com/LonamiWebs/Telethon)**, a Python library that connects to your **personal Telegram account** via the MTProto API. This is **not a bot** — it's your own account connecting directly, as if you were opening Telegram on a new device.

### What the script does:

1. Connects to your Telegram account (phone number + OTP authentication)
2. Lists **all your dialogs** (groups, channels, private messages)
3. Scrapes messages from each dialog
4. Exports everything as JSON, CSV, or Markdown

### What the script does NOT do:

- ❌ Sends no messages
- ❌ Modifies no groups/contacts
- ❌ Deletes nothing
- ✅ Read-only

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- A Telegram account
- Telegram API credentials (free)

### 1. Get Telegram API credentials

1. Go to **[my.telegram.org](https://my.telegram.org)**
2. Log in with your Telegram phone number
3. Click on **"API development tools"**
4. Fill out the form:
   - **App title**: whatever you want (e.g., `my_scraper`)
   - **Short name**: a short name (e.g., `myscr`)
   - **Platform**: `Other`
   - **Description**: `Personal scraper`
5. Click **"Create application"**
6. Note the **`api_id`** (number) and **`api_hash`** (hex string)

### 2. Install dependencies

```bash
pip install telethon
```

### 3. Configure

Two options (pick one):

**Option A — `config.json` file (recommended)**

```bash
cp config.example.json config.json
```

Then edit `config.json` with your actual values:

```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here"
}
```

**Option B — Environment variables**

```bash
export TG_API_ID=12345678
export TG_API_HASH=your_api_hash_here
```

### 4. First run (authentication)

```bash
python3 telegram_scraper.py
```

The script will prompt you for:
1. **Your phone number** (with country code, e.g., `+33612345678`)
2. **The OTP code** that Telegram sends you through the Telegram app or via SMS
3. (If enabled) Your **Telegram 2FA password**

> ⚠️ **The first run creates a `session` file** that saves the authentication. Subsequent runs won't require re-authentication.

### 5. Subsequent runs

```bash
python3 telegram_scraper.py
# → Connects directly, no re-auth
```

---

## 📖 Usage

### Basic

```bash
# Scrape the last 50 messages from each dialog
python3 telegram_scraper.py --limit 50

# Scrape 500 messages per dialog (default)
python3 telegram_scraper.py

# Scrape the ENTIRE history (⚠️ can be VERY long)
python3 telegram_scraper.py --limit 0
```

### Filter by type

```bash
# Groups only
python3 telegram_scraper.py --types groups

# Channels only
python3 telegram_scraper.py --types channels

# Private conversations only
python3 telegram_scraper.py --types private
```

### Export formats

```bash
# JSON (default) — most complete
python3 telegram_scraper.py --format json

# CSV — compatible with Excel / Google Sheets
python3 telegram_scraper.py --format csv

# Markdown — human-readable
python3 telegram_scraper.py --format markdown
```

### Output directory

```bash
# Default: ./exports/
python3 telegram_scraper.py --output /path/to/folder
```

---

## 📁 Output structure

```
exports/
├── telegram_export_20260415_035253.json    # Full messages with metadata
├── telegram_summary_20260415_035253.json   # Overview (dialog count, message count)
```

### JSON format (full export)

```json
[
  {
    "name": "Group name",
    "type": "group",
    "id": 123456789,
    "message_count_scraped": 50,
    "members_count": 3390,
    "messages": [
      {
        "id": 123,
        "date": "2026-04-14T18:30:00+00:00",
        "sender_id": 987654321,
        "sender_name": "John Doe",
        "text": "Message content",
        "reply_to": null,
        "media_type": null,
        "forward": false
      }
    ]
  }
]
```

### JSON format (summary)

```json
{
  "scraped_at": "2026-04-15T03:52:53",
  "total_dialogs": 37,
  "total_messages": 1546,
  "format": "json",
  "output_file": "exports/telegram_export_20260415_035253.json",
  "dialogs": [
    { "name": "Group name", "type": "group", "id": 123, "messages_scraped": 50, "members": 3390 }
  ]
}
```

---

## 🔐 Security

### Sensitive files (already in `.gitignore`)

| File | Content | Risk |
|------|---------|------|
| `config.json` | api_id + api_hash | 🟡 Moderate — allows creating apps |
| `session` | Telegram auth token | 🔴 **High** — full account access |
| `exports/` | Personal messages | 🔴 **High** — private data |

### Best practices

- ✅ **Never commit** `config.json`, `session`, or `exports/`
- ✅ The repo's `.gitignore` is already configured to exclude them
- ✅ You can revoke access at any time in Telegram:
  - Settings → Active devices → disconnect the server
- ✅ To delete the session: `rm session`

---

## 🔧 Automation (cron)

You can run the scraper on a schedule with cron:

```bash
# Every 6 hours — scrape the last 100 messages
0 */6 * * * cd /path/to/repo && python3 telegram_scraper.py --limit 100 --output /path/to/exports >> /var/log/tg-scraper.log 2>&1
```

Or use a **systemd timer** for more control.

---

## 🐛 Troubleshooting

### "Please enter your phone (or bot token):"
→ First run, this is normal. Enter your phone number with country code.

### "The code entered is invalid"
→ The OTP code has expired or is incorrect. Rerun the script to get a new one.

### "Two-step verification is enabled"
→ Telegram is asking for your 2FA password. Enter it when the script prompts you.

### "Chat not found" or "Channel not found"
→ The group/channel may have been deleted or you were banned from it.

### "FloodWaitError: A wait of X seconds is required"
→ Telegram is rate-limiting requests. The script will wait automatically, or rerun later.

---

## 📦 Dependencies

- **[Telethon](https://github.com/LonamiWebs/Telethon)** — Telegram MTProto client for Python
- Python 3.10+ (for native type hint support)

## 📝 License

Personal use. Do whatever you want with it.
