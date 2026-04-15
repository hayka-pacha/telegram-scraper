#!/usr/bin/env python3
"""
Telegram Scraper — Scrape tous les groupes/canaux/discussions via Telethon.

Usage:
  1. Première exécution : python3 telegram_scraper.py → demande le numéro + code OTP
  2. Exécutions suivantes : python3 telegram_scraper.py → session persistente, pas de re-auth

  Arguments optionnels :
    --limit N       Nombre max de messages par dialog (défaut: 500, 0 = tout)
    --output DIR    Répertoire de sortie (défaut: ./exports/)
    --types TYPES   Filtrer par type: groups,channels,private,all (défaut: all)
    --format FMT    Format: json, csv, markdown (défaut: json)
    --config F      Fichier de config (défaut: config.json)
"""

import argparse
import asyncio
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────
# Charge les credentials depuis config.json ou variables d'environnement
CONFIG_FILE = Path(__file__).parent / "config.json"

def load_config():
    """Charge api_id et api_hash depuis config.json ou variables d'env."""
    config = {}

    # Priorité 1 : variables d'environnement
    if os.getenv("TG_API_ID") and os.getenv("TG_API_HASH"):
        config["api_id"] = int(os.getenv("TG_API_ID"))
        config["api_hash"] = os.getenv("TG_API_HASH")

    # Priorité 2 : fichier config.json
    elif CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config = json.load(f)

    else:
        print("❌ Erreur : aucun credential trouvé.")
        print("   → Crée config.json ou définis TG_API_ID + TG_API_HASH")
        print("   → Voir README.md pour les instructions.")
        sys.exit(1)

    return config

CFG = load_config()
API_ID = CFG["api_id"]
API_HASH = CFG["api_hash"]
SESSION_NAME = str(Path(__file__).parent / "session")
DEFAULT_OUTPUT = str(Path(__file__).parent / "exports")

from telethon import TelegramClient
from telethon.tl.types import (
    Channel,
    Chat,
    User,
    MessageMediaDocument,
    MessageMediaPhoto,
)


def get_entity_type(entity) -> str:
    """Classifie un dialog en type lisible."""
    if isinstance(entity, User):
        return "private"
    if isinstance(entity, Chat):
        return "group"
    if isinstance(entity, Channel):
        if entity.megagroup or entity.gigagroup:
            return "group"
        if entity.broadcast:
            return "channel"
    return "unknown"


def message_to_dict(msg) -> dict:
    """Convertit un message Telethon en dict sérialisable."""
    d = {
        "id": msg.id,
        "date": msg.date.isoformat() if msg.date else None,
        "sender_id": msg.sender_id,
        "sender_name": None,
        "text": msg.text or "",
        "reply_to": None,
        "media_type": None,
        "forward": msg.forward is not None,
    }

    if msg.sender:
        if isinstance(msg.sender, User):
            d["sender_name"] = f"{msg.sender.first_name or ''} {msg.sender.last_name or ''}".strip()
        elif hasattr(msg.sender, "title"):
            d["sender_name"] = msg.sender.title

    if msg.reply_to:
        d["reply_to"] = msg.reply_to.reply_to_msg_id

    if msg.media:
        if isinstance(msg.media, MessageMediaPhoto):
            d["media_type"] = "photo"
        elif isinstance(msg.media, MessageMediaDocument):
            d["media_type"] = "document"
        else:
            d["media_type"] = type(msg.media).__name__

    return d


async def scrape_dialogs(client, output_dir, msg_limit, type_filter, fmt):
    """Scrape tous les dialogs et exporte les messages."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # Récupérer tous les dialogs
    dialogs = await client.get_dialogs()
    print(f"\n📋 {len(dialogs)} dialogs trouvés\n")

    results = []
    total_messages = 0

    for i, dialog in enumerate(dialogs, 1):
        entity = dialog.entity
        entity_type = get_entity_type(entity)

        # Filtrer par type
        if type_filter != "all" and entity_type not in type_filter:
            continue

        name = getattr(entity, "title", None) or getattr(entity, "first_name", "Unknown")
        name_safe = name[:60]

        print(f"[{i}/{len(dialogs)}] 💬 {name_safe} ({entity_type})", end="")

        # Limite de messages
        limit = msg_limit if msg_limit > 0 else None

        try:
            messages = []
            async for msg in client.iter_messages(entity, limit=limit):
                messages.append(message_to_dict(msg))
        except Exception as e:
            print(f" ⚠️ Erreur: {e}")
            continue

        print(f" → {len(messages)} scrapés")

        dialog_data = {
            "name": name,
            "type": entity_type,
            "id": entity.id,
            "message_count_scraped": len(messages),
            "members_count": getattr(entity, "participants_count", None),
            "messages": messages,
        }
        results.append(dialog_data)
        total_messages += len(messages)

    # ─── Export ───────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "json":
        out_file = output / f"telegram_export_{timestamp}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    elif fmt == "csv":
        out_file = output / f"telegram_export_{timestamp}.csv"
        with open(out_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["dialog_name", "dialog_type", "dialog_id", "msg_id", "date", "sender_name", "sender_id", "text", "media_type"])
            for d in results:
                for m in d["messages"]:
                    writer.writerow([d["name"], d["type"], d["id"], m["id"], m["date"], m["sender_name"], m["sender_id"], m["text"][:500], m["media_type"]])

    elif fmt == "markdown":
        out_file = output / f"telegram_export_{timestamp}.md"
        with open(out_file, "w", encoding="utf-8") as f:
            for d in results:
                f.write(f"# {d['name']} ({d['type']})\n")
                f.write(f"> ID: {d['id']} | Membres: {d.get('members_count', '?')} | Messages scrapés: {d['message_count_scraped']}\n\n")
                for m in d["messages"]:
                    date_str = m["date"][:19] if m["date"] else "?"
                    f.write(f"**[{date_str}]** {m['sender_name'] or '???'}: {m['text'][:200]}\n\n")
                f.write("---\n\n")

    # ─── Résumé ──────────────────────────────────────────────────
    summary = {
        "scraped_at": datetime.now().isoformat(),
        "total_dialogs": len(results),
        "total_messages": total_messages,
        "format": fmt,
        "output_file": str(out_file),
        "dialogs": [
            {
                "name": d["name"],
                "type": d["type"],
                "id": d["id"],
                "messages_scraped": d["message_count_scraped"],
                "members": d.get("members_count"),
            }
            for d in results
        ],
    }

    summary_file = output / f"telegram_summary_{timestamp}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Export terminé !")
    print(f"   📁 {len(results)} dialogs, {total_messages} messages")
    print(f"   📄 Données: {out_file}")
    print(f"   📋 Résumé: {summary_file}")

    return str(out_file)


async def main():
    parser = argparse.ArgumentParser(description="Telegram scraper via Telethon")
    parser.add_argument("--limit", type=int, default=500, help="Messages par dialog (0 = tout)")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT, help="Répertoire de sortie")
    parser.add_argument("--types", type=str, default="all", help="Filtrer: groups,channels,private,all")
    parser.add_argument("--format", type=str, default="json", choices=["json", "csv", "markdown"], help="Format d'export")
    args = parser.parse_args()

    print("🔗 Connexion à Telegram...")
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        me = await client.get_me()
        print(f"✅ Connecté en tant que {me.first_name} {me.last_name or ''} (@{me.username or '?'})")

        await scrape_dialogs(client, args.output, args.limit, args.types, args.format)


if __name__ == "__main__":
    asyncio.run(main())
