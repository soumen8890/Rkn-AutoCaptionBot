# AutoCaptionBot by RknDeveloper
# Copyright (c) 2024 RknDeveloper
# Licensed under the MIT License
# https://github.com/RknDeveloper/Rkn-AutoCaptionBot/blob/main/LICENSE
# Please retain this credit when using or forking this code.

from pyrogram import Client, filters, errors, types
from config import Rkn_Botz
from .database import rkn_botz
import asyncio, time, re, os, sys
from datetime import datetime

# Helper functions for new variables
def get_file_extension(file_name):
    return os.path.splitext(file_name)[1][1:].upper() if '.' in file_name else "Unknown"

def get_wish():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"

def get_resolution(media):
    if hasattr(media, 'width') and hasattr(media, 'height'):
        return f"{media.width}x{media.height}"
    return "Unknown"

@Client.on_message(filters.private & filters.user(Rkn_Botz.ADMIN) & filters.command("rknusers"))
async def show_user_stats(client, message):
    start = time.monotonic()
    rkn = await message.reply_text("🔍 Gathering bot statistics...")

    total = await rkn_botz.fetch_total_users()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - client.uptime))
    ping = (time.monotonic() - start) * 1000

    await rkn.edit_text(
        f"📊 <b>Bot Stats</b>\n\n"
        f"⏱️ <b>Uptime:</b> {uptime}\n"
        f"📡 <b>Ping:</b> <code>{ping:.2f} ms</code>\n"
        f"👤 <b>Total Users:</b> <code>{total}</code>"
    )
    
@Client.on_message(filters.private & filters.user(Rkn_Botz.ADMIN) & filters.command(["broadcast"]))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply("❗ <b>Reply to a message to broadcast it to all users.</b>")

    rkn_status_msg = await message.reply("🔄 <b>Bot Processing...</b>\nChecking all registered users.")
    
    all_registered_users = await rkn_botz.list_all_users()
    total_users = len(all_registered_users)

    success = 0
    failed = 0
    deactivated = 0
    blocked = 0

    for user_id in all_registered_users:
        try:
            await asyncio.sleep(0.5)
            await message.reply_to_message.copy(chat_id=user_id)
            success += 1
        except errors.InputUserDeactivated:
            deactivated += 1
            await rkn_botz.remove_user_by_id(user_id)
        except errors.UserIsBlocked:
            blocked += 1
            await rkn_botz.remove_user_by_id(user_id)
        except errors.FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            failed += 1
            continue

        try:
            await rkn_status_msg.edit(
                f"<u><b>📣 ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ...</b></u>\n\n"
                f"• 👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: <code>{total_users}</code>\n"
                f"• ✅ sᴜᴄᴄᴇssғᴜʟ: <code>{success}</code>\n"
                f"• ⛔ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: <code>{blocked}</code>\n"
                f"• 🗑️ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: <code>{deactivated}</code>\n"
                f"• ⚠️ ᴜɴsᴜᴄᴄᴇssғᴜʟ: <code>{failed}</code>"
            )
        except Exception:
            pass

    await rkn_status_msg.edit(
        f"<u><b>✅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b></u>\n\n"
        f"• 👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: <code>{total_users}</code>\n"
        f"• ✅ sᴜᴄᴄᴇssғᴜʟ: <code>{success}</code>\n"
        f"• ⛔ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: <code>{blocked}</code>\n"
        f"• 🗑️ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: <code>{deactivated}</code>\n"
        f"• ⚠️ ᴜɴsᴜᴄᴄᴇssғᴜʟ: <code>{failed}</code>"
    )

@Client.on_message(filters.private & filters.user(Rkn_Botz.ADMIN) & filters.command("restart"))
async def restart_bot(client, message):
    reply = await message.reply("🔄 Restarting bot...")
    await asyncio.sleep(3)
    await reply.edit("✅ Bot restarted successfully.")
    os.execl(sys.executable, sys.executable, *sys.argv)
    
@Client.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message):
    await rkn_botz.register_user(message.from_user.id)
    
    await message.reply_photo(
        photo=Rkn_Botz.RKN_PIC,
        caption=(
            f"<b>Hey, {message.from_user.mention} 👋\n\n"
            f"I'm an Auto Caption Bot.\n"
            f"I auto-edit captions for videos, audio, documents posted in channels.\n\n"
            f"/set_caption – Set your custom caption\n"
            f"/delcaption – Delete and use default caption\n\n"
            f"Note: Commands only work in channels where I'm admin.</b>"
        ),
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton("📢 Main Channel", url="https://t.me/Rkn_Bots_Updates")],
            [types.InlineKeyboardButton("❓ Help Group", url="https://t.me/Rkn_Bots_Support")],
            [types.InlineKeyboardButton("🔥 Source Code", url="https://github.com/RknDeveloper/Rkn-AutoCaptionBot")]
        ])
    )

@Client.on_message(filters.command("set_caption") & filters.channel)
async def set_caption(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /set_caption <your caption>\n\nAvailable variables:\n"
                                 "{filename}, {filesize}, {caption}, {language}, {year}, {quality}, "
                                 "{season}, {episode}, {duration}, {height}, {width}, {ext}, "
                                 "{resolution}, {mime_type}, {title}, {artist}, {wish}")

    caption = message.text.split(" ", 1)[1]
    channel_id = message.chat.id

    existing = await rkn_botz._channels_collection.find_one({"channelId": channel_id})
    if existing:
        await rkn_botz.update_channel_caption(channel_id, caption)
    else:
        await rkn_botz.add_channel_caption(channel_id, caption)

    await message.reply(f"✅ Caption set:\n\n<code>{caption}</code>")

@Client.on_message(filters.command(["delcaption", "del_caption", "delete_caption"]) & filters.channel)
async def delete_caption(client, message):
    channel_id = message.chat.id
    result = await rkn_botz._channels_collection.delete_one({"channelId": channel_id})
    if result.deleted_count:
        await message.reply("🗑️ Caption deleted. Using default now.")
    else:
        await message.reply("ℹ️ No caption found.")

@Client.on_message(filters.channel)
async def auto_caption(client, message):
    if not message.media:
        return

    media = None
    file_name = ""
    file_size = None
    duration = None
    width = None
    height = None
    mime_type = None
    title = None
    artist = None
    
    for mtype in ("video", "audio", "document", "voice"):
        media = getattr(message, mtype, None)
        if media:
            file_name = re.sub(r"@\w+", "", media.file_name or "").replace("_", " ").replace(".", " ").strip()
            file_size = getattr(media, "file_size", None)
            duration = getattr(media, "duration", None)
            width = getattr(media, "width", None)
            height = getattr(media, "height", None)
            mime_type = getattr(media, "mime_type", None)
            title = getattr(media, "title", None)
            artist = getattr(media, "performer", None)
            break

    if not media:
        return

    channel_id = message.chat.id
    cap_data = await rkn_botz._channels_collection.find_one({"channelId": channel_id})
    original_caption = message.caption or file_name

    try:
        format_vars = {
            'filename': file_name,
            'filesize': convert_size(file_size) if file_size else "Unknown",
            'caption': original_caption,
            'language': detect_language(original_caption),
            'year': detect_year(original_caption),
            'quality': detect_quality(original_caption),
            'season': detect_season(original_caption),
            'episode': detect_episode(original_caption),
            'duration': f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown",
            'height': height if height else "Unknown",
            'width': width if width else "Unknown",
            'ext': get_file_extension(file_name),
            'resolution': get_resolution(media),
            'mime_type': mime_type if mime_type else "Unknown",
            'title': title if title else "Unknown",
            'artist': artist if artist else "Unknown",
            'wish': get_wish()
        }

        if cap_data:
            formatted = cap_data.get("caption", "").format(**format_vars)
        else:
            formatted = Rkn_Botz.DEFAULT_CAPTION.format(**format_vars)
            
        await message.edit_caption(formatted)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"Error formatting caption: {e}")

# Helper functions (keep your existing ones and add new ones)
def detect_year(file_name):
    clean_name = re.sub(r"[^\d]", " ", file_name)
    candidates = re.findall(r"\b\d{4}\b", clean_name)
    for year in candidates:
        year_int = int(year)
        if 1900 <= year_int <= 2099:
            return year
    return "Unknown"
    
def detect_season(file_name):
    match = re.search(r'\bS(\d{2})\b', file_name, re.IGNORECASE)
    return int(match.group(1)) if match else "Unknown"

def detect_episode(file_name):
    match = re.search(r'\bE(\d{2})\b', file_name, re.IGNORECASE)
    return int(match.group(1)) if match else "Unknown"
    
def detect_quality(file_name):
    match = re.search(r'\b(2160p|1440p|1080p|720p|480p|360p|240p)\b', file_name.lower())
    return match.group(1) if match else "Unknown"
    
def detect_language(file_name):
    languages = ['hindi', 'english', 'telugu', 'tamil', 'malayalam', 'kannada', 'bengali', 'marathi', 'urdu']
    for lang in languages:
        if re.search(rf'\b{lang}\b', file_name, re.IGNORECASE):
            return lang.capitalize()
    return "Unknown"

def convert_size(size):    
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'

# Developer Contacts:
# Telegram: @RknDeveloperr
# Updates Channel: @Rkn_Bots_Updates & @Rkn_Botz
# Special Thanks To: @ReshamOwner
# Update Channels: @Digital_Botz & @DigitalBotz_Support

# ⚠️ Please do not remove this credit!
