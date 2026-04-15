# 📱 Telegram Scraper

Scrape tous les messages de tes groupes, canaux et conversations privées sur Telegram.

## Comment ça marche

Ce script utilise **[Telethon](https://github.com/LonamiWebs/Telethon)**, une librairie Python qui se connecte à ton **compte Telegram personnel** via l'API MTProto. Ce n'est **pas un bot** — c'est ton compte qui se connecte directement, comme si tu ouvrais Telegram sur un nouvel appareil.

### Ce que le script fait :

1. Se connecte à ton compte Telegram (authentification par numéro + code OTP)
2. Liste **tous tes dialogs** (groupes, canaux, messages privés)
3. Scrape les messages de chaque dialog
4. Exporte tout en JSON, CSV ou Markdown

### Ce que le script ne fait PAS :

- ❌ N'envoie aucun message
- ❌ Ne modifie aucun groupe/contact
- ❌ Ne supprime rien
- ✅ Lecture seule

---

## 🚀 Installation

### Prérequis

- Python 3.10+
- Un compte Telegram
- Les API credentials de Telegram (gratuit)

### 1. Obtenir les API credentials Telegram

1. Va sur **[my.telegram.org](https://my.telegram.org)**
2. Connecte-toi avec ton numéro de téléphone Telegram
3. Clique sur **"API development tools"**
4. Remplis le formulaire :
   - **App title** : ce que tu veux (ex: `my_scraper`)
   - **Short name** : un nom court (ex: `myscr`)
   - **Platform** : `Other`
   - **Description** : `Personal scraper`
5. Clique sur **"Create application"**
6. Note le **`api_id`** (nombre) et **`api_hash`** (chaîne hex)

### 2. Installer les dépendances

```bash
pip install telethon
```

### 3. Configurer

Deux options (choisis-en une) :

**Option A — Fichier `config.json` (recommandé)**

```bash
cp config.example.json config.json
```

Puis édite `config.json` avec tes vraies valeurs :

```json
{
  "api_id": 12345678,
  "api_hash": "votre_api_hash_ici"
}
```

**Option B — Variables d'environnement**

```bash
export TG_API_ID=12345678
export TG_API_HASH=votre_api_hash_ici
```

### 4. Première exécution (authentification)

```bash
python3 telegram_scraper.py
```

Le script va te demander :
1. **Ton numéro de téléphone** (avec indicatif pays, ex: `+33612345678`)
2. **Le code OTP** que Telegram t'envoie dans l'app Telegram ou par SMS
3. (Si activé) Ton **mot de passe 2FA** Telegram

> ⚠️ **La première exécution crée un fichier `session`** qui sauvegarde l'authentification. Les exécutions suivantes n'auront plus besoin de s'authentifier.

### 5. Exécutions suivantes

```bash
python3 telegram_scraper.py
# → Directement connecté, pas de re-auth
```

---

## 📖 Utilisation

### Basique

```bash
# Scrape 50 derniers messages de chaque dialog
python3 telegram_scraper.py --limit 50

# Scrape 500 messages par dialog (défaut)
python3 telegram_scraper.py

# Scrape TOUT l'historique (⚠️ peut être TRÈS long)
python3 telegram_scraper.py --limit 0
```

### Filtrer par type

```bash
# Seulement les groupes
python3 telegram_scraper.py --types groups

# Seulement les canaux
python3 telegram_scraper.py --types channels

# Seulement les conversations privées
python3 telegram_scraper.py --types private
```

### Formats d'export

```bash
# JSON (défaut) — le plus complet
python3 telegram_scraper.py --format json

# CSV — compatible Excel / Google Sheets
python3 telegram_scraper.py --format csv

# Markdown — lisible directement
python3 telegram_scraper.py --format markdown
```

### Répertoire de sortie

```bash
# Par défaut: ./exports/
python3 telegram_scraper.py --output /chemin/vers/dossier
```

---

## 📁 Structure de sortie

```
exports/
├── telegram_export_20260415_035253.json    # Messages complets avec metadata
├── telegram_summary_20260415_035253.json   # Vue d'ensemble (nb dialogs, messages)
```

### Format JSON (export complet)

```json
[
  {
    "name": "Nom du groupe",
    "type": "group",
    "id": 123456789,
    "message_count_scraped": 50,
    "members_count": 3390,
    "messages": [
      {
        "id": 123,
        "date": "2026-04-14T18:30:00+00:00",
        "sender_id": 987654321,
        "sender_name": "Jean Dupont",
        "text": "Contenu du message",
        "reply_to": null,
        "media_type": null,
        "forward": false
      }
    ]
  }
]
```

### Format JSON (résumé)

```json
{
  "scraped_at": "2026-04-15T03:52:53",
  "total_dialogs": 37,
  "total_messages": 1546,
  "format": "json",
  "output_file": "exports/telegram_export_20260415_035253.json",
  "dialogs": [
    { "name": "Nom du groupe", "type": "group", "id": 123, "messages_scraped": 50, "members": 3390 }
  ]
}
```

---

## 🔐 Sécurité

### Fichiers sensibles (déjà dans `.gitignore`)

| Fichier | Contenu | Risque |
|---------|---------|--------|
| `config.json` | api_id + api_hash | 🟡 Modéré — permet de créer des apps |
| `session` | Token d'auth Telegram | 🔴 **Élevé** — accès complet au compte |
| `exports/` | Messages personnels | 🔴 **Élevé** — données privées |

### Bonnes pratiques

- ✅ **Ne jamais commiter** `config.json`, `session`, ou `exports/`
- ✅ Le repo `.gitignore` est déjà configuré pour les exclure
- ✅ Tu peux révoquer l'accès à tout moment dans Telegram :
  - Paramètres → Appareils actifs → déconnecte le serveur
- ✅ Pour supprimer la session : `rm session`

---

## 🔧 Automatisation (cron)

Tu peux lancer le scraper régulièrement avec cron :

```bash
# Toutes les 6 heures — scraper les 100 derniers messages
0 */6 * * * cd /chemin/vers/repo && python3 telegram_scraper.py --limit 100 --output /chemin/vers/exports >> /var/log/tg-scraper.log 2>&1
```

Ou avec **systemd timer** pour plus de contrôle.

---

## 🐛 Dépannage

### "Please enter your phone (or bot token):"
→ Première exécution, normal. Entre ton numéro avec l'indicatif pays.

### "The code entered is invalid"
→ Le code OTP a expiré ou est incorrect. Relance le script pour en obtenir un nouveau.

### "Two-step verification is enabled"
→ Telegram te demande ton mot de passe 2FA. Entre-le quand le script le demande.

### "Chat not found" ou "Channel not found"
→ Le groupe/canal a peut-être été supprimé ou tu en as été banni.

### "FloodWaitError: A wait of X seconds is required"
→ Telegram limite les requêtes. Le script attendra automatiquement, ou relance plus tard.

---

## 📦 Dépendances

- **[Telethon](https://github.com/LonamiWebs/Telethon)** — Client Telegram MTProto pour Python
- Python 3.10+ (pour le support natif des type hints)

## 📝 Licence

Usage personnel. Fais-en ce que tu veux.
