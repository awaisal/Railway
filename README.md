# Telegram Bot (Webhook) - Railway

## Features
- Webhook based
- Welcome + rules
- Anti-spam (flood/repeat + link spam)
- Strike system:
  - 1st strike: 5 days mute
  - 2nd strike: 30 days mute
  - 3rd strike: permanent ban
- Owner controls (reply-based):
  - /status
  - /forgive
  - /unrestrict
  - /ban
  - /setrules <text>
  - /setwelcome <text>

## Railway Environment Variables (Required)
- BOT_TOKEN = your telegram bot token
- PUBLIC_URL = your railway public URL (https://xxxx.up.railway.app)
- ADMIN_IDS = your telegram numeric id (comma separated allowed)
Optional:
- DB_PATH=/data/bot.db
- FLOOD_WINDOW_SEC=8
- FLOOD_MAX_MSG=6
- REPEAT_MAX=3
- LINK_SPAM_ENABLED=1

## Important
To keep strikes permanent, attach a Railway Volume and mount it to /data
Otherwise DB may reset on restart.
