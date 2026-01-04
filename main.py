import asyncio
import random
import os
from io import BytesIO
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.errors import FloodWait, RPCError
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL

# --- CREDENTIALS ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "7853734473:AAHdGjbtPFWD6wFlyu8KRWteRg_961WGRJk"

app = Client("DX_ELITE_FINAL", API_ID, API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

tagging_active = {}
EMOJIS = ["✨", "🌟", "🔥", "💎", "🎯", "⚡", "🌈", "🎈", "🍀", "🦋", "🚀", "👑", "👻", "🍎", "🍓"]

# --- ADMIN CHECKER ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

# --- ADVANCE IMAGE WELCOME ---
async def create_welcome_pic(user_id, first_name):
    img = Image.new('RGB', (1000, 500), color=(10, 10, 10))
    draw = ImageDraw.Draw(img)
    
    try:
        # User profile photo fetch
        async for photo in app.get_chat_photos(user_id, limit=1):
            path = await app.download_media(photo.file_id)
            pfp = Image.open(path).convert("RGBA").resize((250, 250))
            os.remove(path)
            img.paste(pfp, (375, 50))
    except Exception:
        pass # If no photo, keep it blank or use default

    # Font handling to avoid crash
    try:
        font = ImageFont.load_default() # For server compatibility
    except:
        font = None

    draw.text((500, 350), f"WELCOME {first_name.upper()}", fill=(255, 255, 255), anchor="mm", font=font)
    
    bio = BytesIO()
    bio.name = 'welcome.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

@app.on_message(filters.new_chat_members)
async def welcome_handler(client, message: Message):
    for user in message.new_chat_members:
        try:
            pic = await create_welcome_pic(user.id, user.first_name)
            welcome_text = (
                f"<b>╔══════════════════════╗</b>\n"
                f"<b> ✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴅᴀʀᴋ-ᴢᴏɴᴇ ✨ </b>\n"
                f"<b>╚══════════════════════╝</b>\n\n"
                f"<b>◈ User:</b> {user.mention}\n"
                f"<b>◈ ID:</b> <code>{user.id}</code>\n\n"
                f"✨ <i>ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴅx—ᴄᴏᴅᴇx</i>"
            )
            await message.reply_photo(pic, caption=welcome_text)
        except Exception as e:
            print(f"Welcome Error: {e}")
    
    # Delete Join Message
    try: await message.delete()
    except: pass

# --- TAGGER SYSTEM ---
@app.on_message(filters.command(["tagall", "all"]) & filters.group)
async def tagall_handler(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return
    
    chat_id = message.chat.id
    tagging_active[chat_id] = True
    
    args = message.text.split(None, 1)
    msg_text = args[1] if len(args) > 1 else "WAKE UP EVERYONE!"
    
    members = []
    async for m in client.get_chat_members(chat_id):
        if not m.user.is_bot and not m.user.is_deleted:
            members.append(m.user.id)
    
    for i in range(0, len(members), 5):
        if not tagging_active.get(chat_id): break
        
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
            await asyncio.sleep(3)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass

@app.on_message(filters.command("stop") & filters.group)
async def stop_tag(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    tagging_active[message.chat.id] = False
    await message.reply_text("🛑 <b>Tagger Stopped Successfully!</b>")

# --- MUSIC SYSTEM ---
@app.on_message(filters.command("play") & filters.group)
async def play_music(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🔎 <b>Give song name!</b>")
    
    query = " ".join(message.command[1:])
    m = await message.reply_text("⏳ ᴘʀᴏᴄᴇssɪɴɢ...")
    
    try:
        with YoutubeDL({"format": "bestaudio", "quiet": True}) as ytdl:
            info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        
        await call_py.join_group_call(
            message.chat.id,
            AudioPiped(info['url']),
            stream_type=StreamType.pulse_stream
        )
        
        design = (
            f"➲ <b>Sᴛᴀʀᴛᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ</b> |\n\n"
            f"‣ <b>Tɪᴛʟᴇ :</b> {info['title'][:25]}...\n"
            f"‣ <b>Dᴜʀᴀᴛɪᴏɴ :</b> {str(timedelta(seconds=info['duration']))}\n"
            f"‣ <b>Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {message.from_user.mention}\n"
        )
        await m.delete()
        await message.reply_text(design)
    except Exception as e:
        await m.edit(f"❌ <b>Error:</b> <code>{e}</code>")

# --- START BOT ---
async def main():
    await app.start()
    await call_py.start()
    print("--- DX—CODEX ELITE SYSTEM IS LIVE ---")
    await asyncio.Event().wait()

if __name__ == "__main__":
    app.run(main())
