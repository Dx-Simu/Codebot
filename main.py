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

app = Client("DX_ELITE_V29", API_ID, API_HASH, bot_token=BOT_TOKEN)

# --- WEB SERVER (RENDER SUPPORT) ---
web = Flask('')
@web.route('/')
def home(): return f"{DEV} IS ACTIVE"
def run_web(): web.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- STORAGE ---
tagging_active = {}; user_stats = {}; warn_stats = {}; badword_count = {}; BLOCK_WORDS = {} 
# PREMIUM EMOJI LIST
EMOJIS = ["✨", "🌟", "🔥", "💎", "🎯", "⚡", "🌈", "🎈", "🍀", "🦋", "🚀", "👑", "👻", "💀", "🌙", "🧿", "🎸", "🏆", "🦁", "🦅", "🐍", "🐲", "👾", "🌀", "🍿", "🪐", "💣", "👽"]
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
    elif count < 5000: return "💎 ᴘʟᴀᴛɪɴᴜᴍ"
    return "👑 ʟᴇɢᴇɴᴅ"

# --- 1. SERVICE CLEANER ---
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

# --- 2. TAGALL & ADMIN TOOLS ---
@app.on_message(filters.command(["tagall", "all"]) & filters.group)
async def tagall_handler(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    tagging_active[message.chat.id] = True
    txt = message.text.split(None, 1)[1] if len(message.command) > 1 else "ᴀᴛᴛᴇɴᴛɪᴏɴ ᴘʟᴇᴀsᴇ!"
    members = [m.user.id async for m in client.get_chat_members(message.chat.id) if not m.user.is_bot]
    await message.delete()
    for i in range(0, len(members), 5):
        if not tagging_active.get(message.chat.id): break
        tags = [f'<a href="tg://user?id={uid}">{random.choice(EMOJIS)}</a>' for uid in members[i:i+5]]
        await client.send_message(message.chat.id, f"<b>╭╼━ {random.choice(EMOJIS)} {txt} {random.choice(EMOJIS)} ━╾╮</b>\n\n{' • '.join(tags)}"); await asyncio.sleep(3)

@app.on_message(filters.command("stop") & filters.group)
async def stop_tag(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    tagging_active[message.chat.id] = False
    await message.reply_text("<b>🛑 ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘᴇᴅ!</b>")

@app.on_message(filters.command("purge") & filters.group)
async def purge_msgs(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id) or not message.reply_to_message: return
    msg_ids = [msg.id async for msg in client.get_chat_history(message.chat.id, offset_id=message.reply_to_message.id, reverse=True)]
    try: await client.delete_messages(message.chat.id, msg_ids); await message.delete()
    except: pass

@app.on_message(filters.command("zombies") & filters.group)
async def zombies_handler(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    count = 0
    async for m in client.get_chat_members(message.chat.id):
        if m.user.is_deleted:
            try: await client.ban_chat_member(message.chat.id, m.user.id); count += 1
            except: pass
    await message.reply(f"<b>🧹 ᴄʟᴇᴀɴᴇᴅ {count} ᴢᴏᴍʙɪᴇs!</b>"); await message.delete()

# --- 3. STATS & PROFILE ---
@app.on_message(filters.command("rank") & filters.group)
async def rank_cmd(client, message: Message):
    cid, uid = message.chat.id, message.from_user.id
    if cid not in user_stats or uid not in user_stats[cid]: return
    sorted_stats = sorted(user_stats[cid].items(), key=lambda x: x[1]['count'], reverse=True)
    rank = next(i for i, (u_id, _) in enumerate(sorted_stats, 1) if u_id == uid)
    count = user_stats[cid][uid]['count']
    res = (f"<b>╭╼━ ✨ ʏᴏᴜʀ ʀᴀɴᴋ ✨ ━╾╮</b>\n"
           f"<b>🏆 ᴘᴏsɪᴛɪᴏɴ:</b> <code>#{rank}</code>\n"
           f"<b>✉️ ᴍsɢs:</b> <code>{count}</code>\n"
           f"<b>🎭 ᴛɪᴛʟᴇ:</b> <code>{get_rank_title(count)}</code>\n"
           f"<b>╰╼━━━ {DEV} ━━━╾╯</b>")
    await message.reply_text(res); await message.delete()

@app.on_message(filters.command("top") & filters.group)
async def top_active(client, message: Message):
    cid = message.chat.id
    if cid not in user_stats: return
    sorted_stats = sorted(user_stats[cid].items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    res = f"<b>╭╼━ ✨ ᴛᴏᴘ 10 ᴀᴄᴛɪᴠᴇ ✨ ━╾╮</b>\n"
    for i, (uid, data) in enumerate(sorted_stats, 1):
        res += f"<b>{i}.</b> <code>{data['name'][:10]}</code> — {data['count']} {random.choice(EMOJIS)}\n"
    res += f"<b>╰╼━━━━ {DEV} ━━━━╾╯</b>"
    await message.reply_text(res); await message.delete()

# --- 4. MUSIC DOWNLOADER (YT-DLP) ---
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
            caption = f"<b>╭╼━ ✨ ᴍᴜsɪᴄ ✨ ━╾╮</b>\n<b>🎶:</b> <code>{info['title'][:30]}</code>\n<b>🎤:</b> <code>{info['uploader'][:15]}</code>\n<b>╰╼━━━ {DEV} ━━━╾╯</b>"
            await message.reply_audio(audio=file, caption=caption, title=info['title'])
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
            if badword_count[cid][uid] >= 10: # Punishment early
                try: await client.restrict_chat_member(cid, uid, ChatPermissions(can_send_messages=False), until_date=datetime.now() + timedelta(minutes=10))
                except: pass

@app.on_message(filters.command("addword") & filters.group)
async def add_word_cmd(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id) or len(message.command) < 2: return
    word = message.text.split(None, 1)[1].lower()
    cid = message.chat.id
    if cid not in BLOCK_WORDS: BLOCK_WORDS[cid] = []
    BLOCK_WORDS[cid].append(word)
    await message.reply_text(f"<b>✅ ᴀᴅᴅᴇᴅ:</b> <code>{word}</code>"); await message.delete()

# --- 6. WELCOME IMAGE ---
@app.on_message(filters.new_chat_members)
async def welcome_handler(client, message: Message):
    for user in message.new_chat_members:
        if user.is_bot: continue
        img = Image.new('RGB', (1000, 500), color=(15, 15, 15))
        draw = ImageDraw.Draw(img)
        draw.text((500, 350), f"WELCOME {user.first_name.upper()}", fill=(255, 255, 255), anchor="mm")
        bio = BytesIO(); bio.name = 'w.png'; img.save(bio, 'PNG'); bio.seek(0)
        await message.reply_photo(bio, caption=f"<b>✨ ᴡᴇʟᴄᴏᴍᴇ {user.mention} ᴛᴏ ᴏᴜʀ ᴄʟᴀɴ!</b>"); await message.delete()

# --- START ---
if __name__ == "__main__":
    if not os.path.exists('downloads'): os.makedirs('downloads')
    Thread(target=run_web).start()
    app.run()
