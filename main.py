import asyncio
import random
import os
import re
import requests
from io import BytesIO
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
from ntgcalls import NTgCalls # NTgCalls integrated
from yt_dlp import YoutubeDL

# --- CREDENTIALS ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "7853734473:AAHdGjbtPFWD6wFlyu8KRWteRg_961WGRJk"

app = Client("DX_ELITE_RENDER", API_ID, API_HASH, bot_token=BOT_TOKEN)
ntgcalls = NTgCalls(app) # Music Engine changed to NTgCalls

tagging_active = {}
warns = {}
user_stats = {} 
EMOJIS = ["✨", "🌟", "🔥", "💎", "🎯", "⚡", "🌈", "🎈", "🍀", "🦋", "🚀", "👑", "👻", "🍎", "🍓"]

# --- ADMIN CHECKER ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

# --- RANK SYSTEM ---
def get_rank(count):
    if count < 50: return "🆕 Nᴇᴡʙɪᴇ"
    elif count < 200: return "🥉 Bʀᴏɴᴢᴇ"
    elif count < 500: return "🥈 Sɪʟᴠᴇʀ"
    elif count < 1000: return "🥇 Gᴏʟᴅ"
    elif count < 2500: return "💎 Dɪᴀᴍᴏɴᴅ"
    return "👑 Lᴇɢᴇɴᴅ"

# --- COMMANDS LIST (ONLY FOR 6703335929) ---
@app.on_message(filters.command(["command", "commands"]) & filters.group)
async def commands_list(client, message: Message):
    if message.from_user.id != 6703335929: return 
    help_text = (
        f"<b>╭╼━━━━━━✨━━━━━━╾╮</b>\n"
        f"<b>    ✨ ʙᴏᴛ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ✨    </b>\n"
        f"<b>╰╼━━━━━━✨━━━━━━╾╯</b>\n\n"
        f"➲ <b>ᴍᴜsɪᴄ:</b> <code>/play</code>, <code>/song</code>, <code>/stop</code>\n"
        f"➲ <b>ᴛᴀɢɢᴇʀ:</b> <code>/tagall</code>, <code>/stop</code>\n"
        f"➲ <b>ᴜsᴇʀ:</b> <code>/stats</code>, <code>/rank</code>, <code>/q</code>\n"
        f"➲ <b>ᴀᴅᴍɪɴ:</b> <code>/tmute</code>, <code>/ban</code>\n\n"
        f"✨ <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴅx—ᴄᴏᴅᴇx</b>"
    )
    await message.reply_text(help_text)

# --- WELCOME IMAGE CARD ---
async def create_welcome_pic(user_id, first_name):
    img = Image.new('RGB', (1000, 500), color=(10, 10, 10))
    draw = ImageDraw.Draw(img)
    try:
        async for photo in app.get_chat_photos(user_id, limit=1):
            path = await app.download_media(photo.file_id)
            pfp = Image.open(path).convert("RGBA").resize((250, 250))
            os.remove(path); img.paste(pfp, (375, 50))
    except: pass
    draw.text((500, 350), f"WELCOME {first_name.upper()}", fill=(255, 255, 255), anchor="mm")
    bio = BytesIO(); bio.name = 'welcome.png'; img.save(bio, 'PNG'); bio.seek(0)
    return bio

@app.on_message(filters.new_chat_members)
async def welcome_handler(client, message: Message):
    for user in message.new_chat_members:
        pic = await create_welcome_pic(user.id, user.first_name)
        await message.reply_photo(pic, caption=f"<b>╔══════════════════════╗</b>\n<b> ✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴅᴀʀᴋ-ᴢᴏɴᴇ ✨ </b>\n<b>╚══════════════════════╝</b>\n\n<b>◈ Usᴇʀ:</b> {user.mention}")

# --- TAGALL (ORIGINAL BORDER) ---
@app.on_message(filters.command(["tagall", "all"]) & filters.group)
async def tagall_handler(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    tagging_active[message.chat.id] = True
    txt = message.text.split(None, 1)[1] if len(message.command) > 1 else "WAKE UP!"
    members = [m.user.id async for m in client.get_chat_members(message.chat.id) if not m.user.is_bot]
    for i in range(0, len(members), 5):
        if not tagging_active.get(message.chat.id): break
        tags = [f'<a href="tg://user?id={uid}">{random.choice(EMOJIS)}</a>' for uid in members[i:i+5]]
        await client.send_message(message.chat.id, f"<b>╭╼━━━━━━✨━━━━━━╾╮</b>\n   <b>{txt}</b>\n<b>╰╼━━━━━━✨━━━━━━╾╯</b>\n\n{' • '.join(tags)}\n\n<code>💎 DX—CODEX</code>")
        await asyncio.sleep(3)

# --- MUSIC WITH NTGCALLS ---
@app.on_message(filters.command("play") & filters.group)
async def play_music(client, message: Message):
    if len(message.command) < 2: return
    m = await message.reply("⏳ ᴘʀᴏᴄᴇssɪɴɢ...")
    try:
        with YoutubeDL({"format": "bestaudio", "quiet": True}) as ytdl:
            info = ytdl.extract_info(f"ytsearch:{' '.join(message.command[1:])}", download=False)['entries'][0]
        await ntgcalls.join(message.chat.id, info['url']) # NTgCalls Join
        await m.edit(f"➲ <b>Sᴛᴀʀᴛᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ</b>\n\n‣ <b>Tɪᴛʟᴇ :</b> {info['title'][:25]}")
    except Exception as e: await m.edit(f"❌ ᴇʀʀᴏʀ: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop_music(client, message: Message):
    if await is_admin(message.chat.id, message.from_user.id):
        await ntgcalls.leave(message.chat.id)
        await message.reply("⏹ <b>Sᴛᴏᴘᴘᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ</b>")

# --- OTHER FEATURES (STATS, RANK, QUOTE, AUTO-MOD) ---
@app.on_message(filters.group & ~filters.bot, group=-1)
async def track_activity(client, message: Message):
    cid, uid = message.chat.id, message.from_user.id
    if cid not in user_stats: user_stats[cid] = {}
    if uid not in user_stats[cid]: user_stats[cid][uid] = {"name": message.from_user.first_name, "count": 0}
    user_stats[cid][uid]["count"] += 1

@app.on_message(filters.command("stats") & filters.group)
async def show_stats(client, message: Message):
    cid = message.chat.id
    if cid not in user_stats: return
    sorted_stats = sorted(user_stats[cid].items(), key=lambda x: x[1]["count"], reverse=True)[:10]
    res = "📊 <b>Mᴏsᴛ Aᴄᴛɪᴠᴇ Mᴇᴍʙᴇʀs</b>\n\n"
    for i, (uid, data) in enumerate(sorted_stats, 1):
        res += f"{i}. <b>{data['name']}</b> — <code>{data['count']}</code> msgs\n"
    await message.reply_text(res)

@app.on_message(filters.command("q") & filters.group)
async def quote_handler(client, message: Message):
    if not message.reply_to_message: return
    json_data = {"type": "quote", "format": "webp", "backgroundColor": "#1b1429", "width": 512, "height": 768, "scale": 2, "messages": [{"entities": [], "avatar": True, "from": {"id": message.reply_to_message.from_user.id, "first_name": message.reply_to_message.from_user.first_name}, "text": message.reply_to_message.text or "", "replyMessage": {}}]}
    try:
        res = requests.post("https://bot.lyo.su/quote/generate", json=json_data)
        if res.status_code == 200:
            sticker = BytesIO(res.content); sticker.name = "q.webp"; await message.reply_sticker(sticker)
    except: pass

@app.on_message(filters.group & ~filters.service)
async def auto_mod(client, message: Message):
    if not message.text or await is_admin(message.chat.id, message.from_user.id): return
    if re.search(r"http[s]?://|t.me/|@", message.text):
        await message.delete(); await message.reply(f"⚠️ {message.from_user.mention} <b>Lɪɴᴋs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ!</b>")

# --- START BOT ---
async def main():
    await app.start()
    print("NTGCALLS SYSTEM IS LIVE ON RENDER")
    await asyncio.Event().wait()

if __name__ == "__main__": asyncio.get_event_loop().run_until_complete(main())
