# Telegram Notifications — What Was Done

## Overview

A new Django app called `notifications` was added to the project. It sends a Telegram message to a configured channel every time a key event happens on FAMMO, and keeps a log of every notification in the database.

---

## Files Created

| File | Purpose |
|---|---|
| `notifications/__init__.py` | Empty — marks directory as a Python package |
| `notifications/apps.py` | App config; calls `ready()` to wire up signal receivers at startup |
| `notifications/models.py` | `NotificationLog` model — stores every sent/failed notification |
| `notifications/telegram.py` | `send_telegram_message(text)` helper — calls the Telegram Bot API via HTTP |
| `notifications/signals.py` | All Django signal receivers (see Events section below) |
| `notifications/admin.py` | Registers `NotificationLog` in Django Admin so you can browse the log |
| `notifications/migrations/__init__.py` | Empty — marks migrations directory |
| `notifications/migrations/0001_initial.py` | Auto-generated migration to create the `NotificationLog` table |

---

## Files Modified

| File | Change |
|---|---|
| `famo/settings.py` | Added `'notifications'` to `INSTALLED_APPS`; added `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID` settings read from `.env` |
| `.env.example` | Added `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID` with instructions |

---

## Events That Trigger a Notification

| Event | Django Signal | Model Watched |
|---|---|---|
| New user registers | `post_save` (created=True) | `CustomUser` |
| New forum question posted | `post_save` (created=True) | `forum.Question` |
| New completed subscription | `post_save` (created=True, status='completed') | `subscription.SubscriptionTransaction` |
| New clinic / vet registered | `post_save` (created=True) | `vets.Clinic` |

---

## How to Activate (Setup Steps)

### 1. Create a Telegram Bot
1. Open Telegram, search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the **Bot Token** (looks like `123456:ABCdef...`)

### 2. Create a Telegram Channel
1. Create a new channel in Telegram (public or private)
2. Add your bot as an **Administrator** with "Post Messages" permission
3. Note the **Channel ID**:
   - Public channel: use `@your_channel_username`
   - Private channel: use the numeric ID like `-1001234567890`

### 3. Add Environment Variables

In your `.env` file (locally and on cPanel):
```
TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrSTUvwxyz
TELEGRAM_CHANNEL_ID=@fammo_alerts
```

### 4. Deploy to cPanel

```bash
# On cPanel, after uploading the new code:
python manage.py migrate notifications
```
No other services or changes needed.

---

## Notification Log (Admin)

All sent/failed notifications are stored in the database and visible at:

```
/admin/notifications/notificationlog/
```

Each record shows: event type, full message text, status (sent/failed), error detail, and timestamp.

---

## How It Works Internally

```
Event happens (e.g. user registers)
        ↓
Django post_save signal fires
        ↓
notifications/signals.py receiver runs
        ↓
notifications/telegram.py calls Telegram Bot API (HTTP POST, timeout=10s)
        ↓
NotificationLog record saved (status: sent or failed)
```

- If Telegram is unreachable or tokens are missing, the notification fails **silently** — it logs the error but never breaks the user-facing request.
- No Celery required — signals run synchronously. If you want async later, the Celery setup already in the project can be used.

---

## Example Telegram Messages

**New User:**
```
👤 New User Registered
📧 Email: user@example.com
🕐 Joined: 2026-05-11 14:32
```

**New Forum Question:**
```
❓ New Forum Question
📝 Title: My dog won't eat
🏷 Category: Dog Health
👤 Author: user@example.com
🕐 Posted: 2026-05-11 14:33
```

**New Subscription:**
```
💳 New Subscription
👤 User: user@example.com
📦 Plan: Optimal
💶 Amount: €19.99
🕐 Date: 2026-05-11 14:35
```

**New Clinic:**
```
🏥 New Clinic / Vet Registered
🏷 Name: Paws Veterinary Clinic
📍 City: Dublin
🕐 Registered: 2026-05-11 14:40
```
