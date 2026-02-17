import os

def _required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing required env var: {name}")
    return v

BOT_TOKEN = _required("BOT_TOKEN")

# Railway public URL like: https://your-service.up.railway.app
PUBLIC_URL = _required("PUBLIC_URL").rstrip("/")

# Comma-separated Telegram user IDs (you / owners)
# Example: "123456789,987654321"
ADMIN_IDS = set()
_admin_raw = os.getenv("ADMIN_IDS", "").strip()
if _admin_raw:
    ADMIN_IDS = {int(x.strip()) for x in _admin_raw.split(",") if x.strip().isdigit()}

# Webhook path: token-based path for security
WEBHOOK_PATH = f"/{BOT_TOKEN}"

# Railway sets PORT automatically
PORT = int(os.getenv("PORT", "8080"))

# SQLite path (use /data if you attach Railway volume)
DB_PATH = os.getenv("DB_PATH", "/data/bot.db")

# Anti-spam tuning
FLOOD_WINDOW_SEC = int(os.getenv("FLOOD_WINDOW_SEC", "8"))
FLOOD_MAX_MSG = int(os.getenv("FLOOD_MAX_MSG", "6"))
REPEAT_MAX = int(os.getenv("REPEAT_MAX", "3"))
LINK_SPAM_ENABLED = os.getenv("LINK_SPAM_ENABLED", "1") == "1"

# Defaults (can be changed via commands)
DEFAULT_WELCOME = os.getenv("DEFAULT_WELCOME", "Welcome! ✅ Rules follow karo, spam mat karo 🙂")
DEFAULT_RULES = os.getenv(
    "DEFAULT_RULES",
    "Rules:\n1) Spam/Flood nahi\n2) Links bina permission nahi\n3) Abuse nahi\n4) Off-topic limit\nViolation par auto restriction."
)
