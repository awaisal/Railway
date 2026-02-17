import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

from telegram import ChatPermissions, Update
from telegram.ext import ContextTypes

from .config import (
    FLOOD_WINDOW_SEC, FLOOD_MAX_MSG, REPEAT_MAX, LINK_SPAM_ENABLED,
    DEFAULT_WELCOME, DEFAULT_RULES
)
from .db import get_strikes, set_strikes, forgive_user, get_chat_settings
from .utils import has_link, normalize_text

@dataclass
class UserWindow:
    ts: List[int]
    last_texts: List[str]

WINDOWS: Dict[Tuple[int, int], UserWindow] = {}

def _now() -> int:
    return int(time.time())

async def _is_admin(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False

def _punishment_for_strike(strike: int) -> Tuple[str, int]:
    if strike == 1:
        return ("restrict", 5 * 24 * 3600)      # 5 days
    if strike == 2:
        return ("restrict", 30 * 24 * 3600)     # 30 days (~1 month)
    return ("ban", 0)                           # permanent

async def apply_punishment(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not chat or not user or not msg:
        return

    chat_id = chat.id
    user_id = user.id

    if await _is_admin(context, chat_id, user_id):
        return

    strikes = get_strikes(chat_id, user_id) + 1
    ts = _now()
    set_strikes(chat_id, user_id, strikes, reason, ts)

    action, duration = _punishment_for_strike(strikes)

    if action == "restrict":
        until = ts + duration
        perms = ChatPermissions(
            can_send_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
        )
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=perms,
                until_date=until
            )
            await msg.reply_text(
                f"⚠️ Rule Violation: {reason}\n"
                f"User muted. Strike: {strikes}\n"
                f"Duration: {'5 days' if strikes==1 else '1 month'}"
            )
        except Exception as e:
            await msg.reply_text(f"❌ Could not restrict user. Error: {e}")
    else:
        try:
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
            await msg.reply_text(
                f"⛔ Rule Violation: {reason}\n"
                f"User banned permanently. Strike: {strikes}"
            )
        except Exception as e:
            await msg.reply_text(f"❌ Could not ban user. Error: {e}")

def check_flood(chat_id: int, user_id: int, text: str) -> bool:
    key = (chat_id, user_id)
    w = WINDOWS.get(key)
    if not w:
        w = UserWindow(ts=[], last_texts=[])
        WINDOWS[key] = w

    now = _now()
    w.ts = [t for t in w.ts if (now - t) <= FLOOD_WINDOW_SEC]
    w.ts.append(now)

    if len(w.ts) > FLOOD_MAX_MSG:
        return True

    nt = normalize_text(text)
    if nt:
        w.last_texts.append(nt)
        w.last_texts = w.last_texts[-10:]
        if w.last_texts.count(nt) >= REPEAT_MAX:
            return True

    return False

def check_link_spam(text: str) -> bool:
    if not LINK_SPAM_ENABLED:
        return False
    return has_link(text)

async def send_welcome_if_any(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat:
        return
    welcome, rules = get_chat_settings(chat.id)
    welcome_text = welcome or DEFAULT_WELCOME
    rules_text = rules or DEFAULT_RULES
    await context.bot.send_message(chat.id, f"👋 {welcome_text}\n\n📌 {rules_text}")
