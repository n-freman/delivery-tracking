import json

import requests
from constance import config
from django.conf import settings


def _get_chat_ids() -> list[str]:
    raw = config.TELEGRAM_ADMIN_CHAT_IDS
    if not raw:
        return []
    return [cid.strip() for cid in raw.split(",") if cid.strip()]


def send_telegram_message(text: str) -> None:
    chat_ids = _get_chat_ids()
    if not chat_ids:
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in chat_ids:
        try:
            response = requests.post(
                url,
                data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                timeout=5,
            )
            response.raise_for_status()
            print(response.json())
        except requests.RequestException:
            raise
            pass


def send_telegram_media_group(image_urls: list[str], caption: str = "") -> None:
    """Send up to 10 images in a single Telegram album message."""

    print("Sending telegram media group")
    chat_ids = _get_chat_ids()
    if not chat_ids or not image_urls:
        return

    # Telegram allows max 10 images per media group
    image_urls = image_urls[:10]

    media = []
    for i, url in enumerate(image_urls):
        item = {"type": "photo", "media": url}
        if i == 0 and caption:
            item["caption"] = caption
            item["parse_mode"] = "HTML"
        media.append(item)

    bot_url = (
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMediaGroup"
    )
    for chat_id in chat_ids:
        try:
            response = requests.post(
                bot_url,
                data={
                    "chat_id": chat_id,
                    "media": json.dumps(media),
                },
                timeout=10,
            )
            # response.raise_for_status()
            print(response.json())
        except requests.RequestException:
            raise
            pass
