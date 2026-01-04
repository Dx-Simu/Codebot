import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.errors import FloodWait

# API Credentials
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8170872541:AAEW9FehHQ7RoDaTIGuWywH4xubLaALcZd8"

app = Client(
    "DX_ADVANCE_TAGGER", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML
)

tagging_active = {}
EMOJIS = ["✨", "🌟", "🔥", "💎", "🎯", "⚡", "🌈", "🎈", "🍀", "🍎", "🍓", "🦋", "🚀", "👑", "👻"]

# --- Admin Checker Function ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

# --- 1. Service Message Remover (Your requested feature) ---
@app.on_message(filters.group & filters.service)
async def delete_service_messages(_, message: Message):
    try:
        await message.delete()
    except Exception:
        pass

# --- 2. /ctag (Hidden Tagging - Advanced Fix) ---
@app.on_message(filters.command("ctag") & filters.group)
async def hidden_tag(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return
    
    chat_id = message.chat.id
    tagging_active[chat_id] = True
    
    args = message.text.split(None, 1)
    msg_text = args[1] if len(args) > 1 else "Attention Everyone!"
    
    members = []
    async for m in client.get_chat_members(chat_id):
        if not m.user.is_bot and not m.user.is_deleted:
            members.append(m.user.id)

    for i in range(0, len(members), 5):
        if not tagging_active.get(chat_id):
            break
        
        # Zero-width joiner tags
        hidden_mentions = "".join([f'<a href="tg://user?id={u_id}">\u200D</a>' for u_id in members[i:i+5]])
        try:
            await client.send_message(chat_id, f"{hidden_mentions}{msg_text}")
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
        await asyncio.sleep(2.5)

# --- 3. /ltag (Line by Line Emoji Mentions) ---
@app.on_message(filters.command("ltag") & filters.group)
async def line_tag(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return

    chat_id = message.chat.id
    tagging_active[chat_id] = True
    
    members = []
    async for m in client.get_chat_members(chat_id):
        if not m.user.is_bot and not m.user.is_deleted:
            members.append(m.user.id)

    for i in range(0, len(members), 5):
        if not tagging_active.get(chat_id):
            break
        
        lines = [f"{random.choice(EMOJIS)} <a href='tg://user?id={u_id}'>Mentioned User</a>" for u_id in members[i:i+5]]
        output = "\n".join(lines)
        try:
            await client.send_message(chat_id, output)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
        await asyncio.sleep(3.0)

# --- 4. /tagall or /all (Original Decoration Restored) ---
@app.on_message(filters.command(["tagall", "all"]) & filters.group)
async def dx_tagger(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return

    chat_id = message.chat.id
    tagging_active[chat_id] = True
    
    args = message.text.split(None, 1)
    msg_text = args[1] if len(args) > 1 else "WAKE UP EVERYONE!"
    
    await message.reply_text("<blockquote>🚀 <b>DX—CODEX Tagger Processing...</b></blockquote>")

    members = []
    async for m in client.get_chat_members(chat_id):
        if not m.user.is_bot and not m.user.is_deleted:
            members.append(m.user.id)

    for i in range(0, len(members), 5):
        if not tagging_active.get(chat_id):
            break
            
        tag_list = [f'<a href="tg://user?id={uid}">{random.choice(EMOJIS)}</a>' for uid in members[i:i+5]]
        output = (
            f"<b>╭╼━━━━━━✨━━━━━━╾╮</b>\n"
            f"   <b>{msg_text}</b>\n"
            f"<b>╰╼━━━━━━✨━━━━━━╾╯</b>\n\n"
            f"{' • '.join(tag_list)}\n\n"
            f"<code>💎 DX—CODEX</code>"
        )
        
        try:
            await client.send_message(chat_id, output)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
        await asyncio.sleep(3.0)

# --- 5. /stop (Stopping All Processes) ---
@app.on_message(filters.command("stop") & filters.group)
async def stop_tag(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return
    tagging_active[message.chat.id] = False
    await message.reply_text("<code>🛑 All Tagging Stopped.</code>")

print("--- DX—CODEX ADVANCE BOT IS READY ---")
app.run()
