import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_message(text: str) -> bool:
    """
    Send *text* to the configured Telegram channel.
    Returns True on success, False on any failure.
    Does NOT raise — callers can always continue safely.
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    channel = getattr(settings, 'TELEGRAM_CHANNEL_ID', '')

    if not token or not channel:
        logger.warning("Telegram notifications not configured (TELEGRAM_BOT_TOKEN / TELEGRAM_CHANNEL_ID missing).")
        return False

    url = TELEGRAM_API_URL.format(token=token)
    payload = {
        "chat_id": channel,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        logger.error("Failed to send Telegram notification: %s", exc)
        return False
