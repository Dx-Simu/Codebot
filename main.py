import asyncio
import random
import os
import time
import yt_dlp
from io import BytesIO
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus, MessageServiceType
from pyrogram.errors import FloodWait, RPCError
from flask import Flask
from threading import Thread

# --- CREDENTIALS ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "7853734473:AAHdGjbtPFWD6wFlyu8KRWteRg_961WGRJk"
OWNER_ID = 6703335929 

app = Client("DX_ELITE_V27", API_ID, API_HASH, bot_token=BOT_TOKEN)

# --- WEB SERVER (RENDER SUPPORT) ---
web = Flask('')
@web.route('/')
def home(): return "DX-ELITE IS ACTIVE"
def run_web(): web.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- STORAGE ---
tagging_active = {}; user_stats = {}; warn_stats = {}; badword_count = {}; BLOCK_WORDS = {} 
EMOJIS = ["✨", "🌟", "🔥", "💎", "🎯", "⚡", "🌈", "🎈", "🍀", "🦋", "🚀", "👑", "👻"]
S = "➲"

# --- HELPERS ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

def get_rank_title(count):
    if count < 50: return "🆕 ɴᴇᴡ"
    elif count < 500: return "🥈 sɪʟᴠᴇʀ"
    elif count < 1000: return "🥇 ɢᴏʟᴅ"
    return "👑 ʟᴇɢᴇɴᴅ"

# --- 1. SERVICE MESSAGE CLEANER ---
@app.on_message(filters.service)
async def service_cleaner(client, message: Message):
    service_types = [
        MessageServiceType.VIDEO_CHAT_STARTED, MessageServiceType.VIDEO_CHAT_ENDED,
        MessageServiceType.VIDEO_CHAT_INVITE_MEMBERS, MessageServiceType.NEW_CHAT_MEMBERS,
        MessageServiceType.LEFT_CHAT_MEMBER
    ]
    if message.service in service_types:
        try: await message.delete()
        except: pass

# --- 2. OWNER COMMANDS & ADMIN TOOLS ---
@app.on_message(filters.command("commands") & filters.group)
async def owner_commands(client, message: Message):
    if message.from_user.id != OWNER_ID: return
    cmd_list = (
        "<b>╭╼━ ✨ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ ✨ ━╾╮</b>\n"
        f"<b>{S} ᴍᴜsɪᴄ:</b> <code>/song</code>\n"
        f"<b>{S} sᴛᴀᴛs:</b> <code>/rank, /top, /profile</code>\n"
        f"<b>{S} ᴀᴅᴍɪɴ:</b> <code>/warn, /zombies, /purge</code>\n"
        f"<b>{S} ᴡᴏʀᴅs:</b> <code>/addword, /words</code>\n"
        f"<b>{S} ᴛᴀɢ:</b> <code>/tagall, /stop</code>\n"
        "<b>╰╼━━━━━━ ✨ ━━━━━━╾╯</b>"
    )
    await message.reply_text(cmd_list); await message.delete()

@app.on_message(filters.command("purge") & filters.group)
async def purge_msgs(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id) or not message.reply_to_message: return
    msg_ids = [msg.id async for msg in client.get_chat_history(message.chat.id, offset_id=message.reply_to_message.id, reverse=True)]
    try: await client.delete_messages(message.chat.id, msg_ids); await message.delete()
    except: pass

# --- 3. RANK & TOP ACTIVE ---
@app.on_message(filters.command("rank") & filters.group)
async def rank_cmd(client, message: Message):
    cid, uid = message.chat.id, message.from_user.id
    if cid not in user_stats or uid not in user_stats[cid]:
        return await message.reply_text("<b>⚠️ ɴᴏ ᴅᴀᴛᴀ ғᴏᴜɴᴅ!</b>")
    
    sorted_stats = sorted(user_stats[cid].items(), key=lambda x: x[1]['count'], reverse=True)
    rank = next(i for i, (u_id, _) in enumerate(sorted_stats, 1) if u_id == uid)
    count = user_stats[cid][uid]['count']
    
    res = (f"<b>╭╼━ ✨ ʏᴏᴜʀ ʀᴀɴᴋ ✨ ━╾╮</b>\n"
           f"<b>🏆 ᴘᴏsɪᴛɪᴏɴ:</b> <code>#{rank}</code>\n"
           f"<b>✉️ ᴍᴇssᴀɢᴇs:</b> <code>{count}</code>\n"
           f"<b>🎭 ᴛɪᴛʟᴇ:</b> <code>{get_rank_title(count)}</code>\n"
           f"<b>╰╼━━━━ DX-ELITE ━━━━╾╯</b>")
    await message.reply_text(res); await message.delete()

# --- 4. MUSIC & TAGALL ---
@app.on_message(filters.command("song") & filters.group)
async def music_dl(client, message: Message):
    if len(message.command) < 2: return
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("<b>🎵 sᴇᴀʀᴄʜɪɴɢ...</b>")
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'downloads/%(title)s.%(ext)s', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            file = ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp3"
            os.rename(ydl.prepare_filename(info), file)
            await message.reply_audio(audio=file, title=info['title'][:30], performer="DX-ELITE")
            await m.delete()
            if os.path.exists(file): os.remove(file)
    except: await m.edit_text("<b>❌ ᴇʀʀᴏʀ!</b>")
    await message.delete()

# --- 5. TRACKER & AUTO-MOD ---
@app.on_message(filters.group & ~filters.bot, group=-1)
async def tracker(client, message: Message):
    if not message.from_user: return
    cid, uid = message.chat.id, message.from_user.id
    if cid not in user_stats: user_stats[cid] = {}
    if uid not in user_stats[cid]: user_stats[cid][uid] = {"name": message.from_user.first_name, "count": 0}
    user_stats[cid][uid]["count"] += 1
    
    words = BLOCK_WORDS.get(cid, [])
    if message.text and any(w in message.text.lower() for w in words):
        if not await is_admin(cid, uid):
            await message.delete()
            badword_count[cid] = badword_count.get(cid, {}); badword_count[cid][uid] = badword_count[cid].get(uid, 0) + 1
            if badword_count[cid][uid] == 15:
                await client.restrict_chat_member(cid, uid, ChatPermissions(can_send_messages=False), until_date=datetime.now() + timedelta(minutes=10))

# --- START ---
if __name__ == "__main__":
    if not os.path.exists('downloads'): os.makedirs('downloads')
    Thread(target=run_web).start()
    app.run()
