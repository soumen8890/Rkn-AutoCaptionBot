# AutoCaptionBot by RknDeveloper
# Copyright (c) 2024 RknDeveloper
# Licensed under the MIT License
# https://github.com/RknDeveloper/Rkn-AutoCaptionBot/blob/main/LICENSE
# Please retain this credit when using or forking this code.

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import UserNotParticipant
from config import Rkn_Botz
from .database import rkn_botz

class ForceSubCheck:
    def __init__(self, channel: str):
        self.channel = channel.lstrip("@") if channel else None

    async def __call__(self, _, client: Client, message: Message) -> bool:
        if not self.channel:
            return False  # No force sub required
        
        user_id = message.from_user.id

        # Register user in DB if not already
        await rkn_botz.register_user(user_id)

        try:
            member = await client.get_chat_member(self.channel, user_id)
            return member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]
        except UserNotParticipant:
            return True
        except Exception as e:
            print(f"Error checking channel membership: {e}")
            return False

@Client.on_message(filters.private & filters.create(ForceSubCheck(Rkn_Botz.FORCE_SUB)))
async def handle_force_sub(client: Client, message: Message):
    user_id = message.from_user.id
    channel = Rkn_Botz.FORCE_SUB.lstrip("@")
    chat_link = f"https://t.me/{channel}"
    
    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔔 Join Update Channel", url=chat_link)]]
    )

    try:
        member = await client.get_chat_member(channel, user_id)
        if member.status == enums.ChatMemberStatus.BANNED:
            return await message.reply_text(
                "**🚫 You are banned from using this bot.**\nContact admin if this is a mistake."
            )
    except UserNotParticipant:
        pass  # Expected case - user hasn't joined
    except Exception as e:
        return await message.reply_text(f"⚠️ Error checking your status: `{str(e)}`")

    return await message.reply_text(
        "**Hey buddy! 🔐 You need to join our updates channel before using me.**\n\n"
        "Please join the channel and try again.",
        reply_markup=button
    )
