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
DEV = "ᴅx—ᴄᴏᴅᴇx"

app = Client("DX_ELITE_V30", API_ID, API_HASH, bot_token=BOT_TOKEN)

# --- WEB SERVER (RENDER STABILITY) ---
web = Flask('')
@web.route('/')
def home(): return f"{DEV} STABLE"
def run_web():
    port = int(os.environ.get('PORT', 8080))
    web.run(host='0.0.0.0', port=port)

# --- STORAGE ---
tagging_active = {}; user_stats = {}; warn_stats = {}; badword_count = {}; BLOCK_WORDS = {} 
EMOJIS = ["✨", "🌟", "🔥", "💎", "🎯", "⚡", "🌈", "🎈", "🍀", "🦋", "🚀", "👑", "👻", "💀", "🌙", "🧿", "🎸", "🏆", "🦁", "🦅", "🐍", "🐲"]
S = "➲"

# --- HELPERS ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

def get_rank_title(count):
    if count < 50: return "🆕 ɴᴇᴡʙɪᴇ"
    elif count < 500: return "🥈 sɪʟᴠᴇʀ"
    elif count < 1000: return "🥇 ɢᴏʟᴅ"
    return "👑 ʟᴇɢᴇɴᴅ"

# --- 1. SERVICE & VC CLEANER ---
@app.on_message(filters.service)
async def service_cleaner(client, message: Message):
    try: await message.delete()
    except: pass

# --- 2. TAGALL SYSTEM (FIXED) ---
@app.on_message(filters.command(["tagall", "all"]) & filters.group)
async def tagall_handler(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    tagging_active[message.chat.id] = True
    txt = message.text.split(None, 1)[1] if len(message.command) > 1 else "ᴀᴛᴛᴇɴᴛɪᴏɴ!"
    members = []
    async for m in client.get_chat_members(message.chat.id):
        if not m.user.is_bot: members.append(m.user.id)
    
    await message.delete()
    for i in range(0, len(members), 5):
        if not tagging_active.get(message.chat.id): break
        tags = [f'<a href="tg://user?id={uid}">{random.choice(EMOJIS)}</a>' for uid in members[i:i+5]]
        await client.send_message(message.chat.id, f"<b>╭╼━ ✨ {txt} ✨ ━╾╮</b>\n\n{' • '.join(tags)}")
        await asyncio.sleep(3)

@app.on_message(filters.command("stop") & filters.group)
async def stop_tag(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    tagging_active[message.chat.id] = False
    await message.reply_text("<b>🛑 ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘᴇᴅ!</b>")

# --- 3. OWNER & STATS ---
@app.on_message(filters.command("commands") & filters.group)
async def owner_commands(client, message: Message):
    if message.from_user.id != OWNER_ID: return
    res = (f"<b>╭╼━ ✨ {DEV} ᴘᴀɴᴇʟ ✨ ━╾╮</b>\n"
           f"<b>{S} ᴍᴜsɪᴄ:</b> <code>/song</code>\n"
           f"<b>{S} sᴛᴀᴛs:</b> <code>/rank, /top, /profile</code>\n"
           f"<b>{S} ᴀᴅᴍɪɴ:</b> <code>/warn, /purge, /zombies</code>\n"
           f"<b>{S} ᴛᴀɢ:</b> <code>/tagall, /stop</code>\n"
           f"<b>╰╼━━━ {DEV} ━━━╾╯</b>")
    await message.reply_text(res); await message.delete()

@app.on_message(filters.command("profile") & filters.group)
async def profile_handler(client, message: Message):
    target = message.from_user
    if message.reply_to_message: target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try: target = await client.get_users(message.command[1])
        except: return
    
    data = user_stats.get(message.chat.id, {}).get(target.id, {"count": 0})
    res = (f"<b>╭╼━ ✨ ᴘʀᴏғɪʟᴇ ✨ ━╾╮</b>\n"
           f"<b>👤:</b> <code>{target.first_name[:15]}</code>\n"
           f"<b>✉️:</b> <code>{data['count']}</code>\n"
           f"<b>🎭:</b> <code>{get_rank_title(data['count'])}</code>\n"
           f"<b>╰╼━━━ {DEV} ━━━╾╯</b>")
    await message.reply_text(res); await message.delete()

@app.on_message(filters.command("top") & filters.group)
async def top_active(client, message: Message):
    cid = message.chat.id
    if cid not in user_stats: return
    sorted_stats = sorted(user_stats[cid].items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    res = f"<b>╭╼━ ✨ ᴛᴏᴘ 10 ᴀᴄᴛɪᴠᴇ ✨ ━╾╮</b>\n"
    for i, (uid, data) in enumerate(sorted_stats, 1):
        res += f"<b>{i}.</b> <code>{data['name'][:10]}</code> — {data['count']}\n"
    res += f"<b>╰╼━━━━ {DEV} ━━━━╾╯</b>"
    await message.reply_text(res); await message.delete()

# --- 4. MUSIC DOWNLOADER ---
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
            await message.reply_audio(audio=file, title=info['title'])
            await m.delete()
            if os.path.exists(file): os.remove(file)
    except: await m.edit_text("<b>❌ ᴇʀʀᴏʀ</b>")
    await message.delete()

# --- 5. TRACKER & AUTO-MOD ---
@app.on_message(filters.group & ~filters.bot, group=-1)
async def tracker(client, message: Message):
    if not message.from_user: return
    cid, uid = message.chat.id, message.from_user.id
    if cid not in user_stats: user_stats[cid] = {}
    if uid not in user_stats[cid]: user_stats[cid][uid] = {"name": message.from_user.first_name, "count": 0}
    user_stats[cid][uid]["count"] += 1

@app.on_message(filters.new_chat_members)
async def welcome_img(client, message: Message):
    for user in message.new_chat_members:
        if user.is_bot: continue
        img = Image.new('RGB', (600, 300), color=(15, 15, 15))
        draw = ImageDraw.Draw(img)
        draw.text((300, 150), "WELCOME", fill=(255, 255, 255), anchor="mm")
        bio = BytesIO(); bio.name = 'w.png'; img.save(bio, 'PNG'); bio.seek(0)
        await message.reply_photo(bio, caption=f"<b>✨ ᴡᴇʟᴄᴏᴍᴇ {user.mention}!</b>")

# --- START ---
if __name__ == "__main__":
    if not os.path.exists('downloads'): os.makedirs('downloads')
    Thread(target=run_web).start()
    app.run()
