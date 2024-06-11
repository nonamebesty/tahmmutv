# (c) @JAsuran

import asyncio
from configs import Config
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64

# Conversation states
ASK_FILES, RECEIVE_FILES, ASK_FILENAME, RECEIVE_FILENAME = range(4)

# Initialize the bot
bot = Client("bot", bot_token=Config.BOT_TOKEN, api_id=Config.API_ID, api_hash=Config.API_HASH)

user_data = {}

# Helper functions
def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

async def reply_forward(message: Message, file_id: int):
    try:
        media = message.document or message.video or message.audio or message.photo
        file_name = media.file_name if media.file_name else ""
        caption = message.caption if media.file_name else ""
        await message.reply_text(
            f"**Kindly Subscribe and Support My Youtube Channel: https://www.youtube.com/@JAsuranvideos**\n\n"
            f"**Files will be Deleted After 15 min**\n\n"
            f"**__To Retrieve the Stored File, just again open the link!__**\n\n"
            f"**<blockquote>{caption}\n\nLink:** https://redirect.nonamebesty.workers.dev?start=Shakthimaan_{str_to_b64(str(file_id))}</blockquote>",
            disable_web_page_preview=True, quote=True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await reply_forward(message, file_id)

async def media_forward(bot: Client, user_id: int, file_id: int):
    try:
        if Config.FORWARD_AS_COPY:
            return await bot.copy_message(chat_id=user_id, from_chat_id=Config.DB_CHANNEL, message_id=file_id)
        else:
            return await bot.forward_messages(chat_id=user_id, from_chat_id=Config.DB_CHANNEL, message_ids=file_id)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await media_forward(bot, user_id, file_id)

async def send_media_and_reply(bot: Client, user_id: int, file_id: int):
    sent_message = await media_forward(bot, user_id, file_id)
    await reply_forward(message=sent_message, file_id=file_id)
    asyncio.create_task(delete_after_delay(sent_message, 900))

async def delete_after_delay(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"Error deleting message {message.message_id}: {e}")

# Command handler

@bot.on_message(filters.command("batch") & filters.private)
async def batch(bot, message):
    await message.reply_text("How many files do you need to send?")
    user_data[message.chat.id] = {"state": ASK_FILES}

    state = user_data[chat_id].get("state")

    if state == ASK_FILES:
        try:
            file_count = int(message.text)
            user_data[chat_id].update({"file_count": file_count, "files": [], "state": RECEIVE_FILES})
            await message.reply_text(f"Please send file 1 of {file_count}")
        except ValueError:
            await message.reply_text("Please send a valid number.")
    
    elif state == RECEIVE_FILES:
        if message.document or message.video or message.audio or message.photo:
            user_data[chat_id]["files"].append(message)
            current_count = len(user_data[chat_id]["files"])
            total_count = user_data[chat_id]["file_count"]
            
            if current_count < total_count:
                await message.reply_text(f"Please send file {current_count + 1} of {total_count}")
            else:
                user_data[chat_id]["state"] = ASK_FILENAME
                await message.reply_text("All files received. Please send the filename for each file.")
        else:
            await message.reply_text("Please send a valid file.")
    
    elif state == ASK_FILENAME:
        if "filenames" not in user_data[chat_id]:
            user_data[chat_id]["filenames"] = []
        user_data[chat_id]["filenames"].append(message.text)
        
        current_filename_count = len(user_data[chat_id]["filenames"])
        total_file_count = user_data[chat_id]["file_count"]
        
        if current_filename_count < total_file_count:
            await message.reply_text(f"Please send the filename for file {current_filename_count + 1} of {total_file_count}")
        else:
            await process_files(bot, message)
            user_data.pop(chat_id)

async def process_files(bot, message):
    chat_id = message.chat.id
    files = user_data[chat_id]["files"]
    filenames = user_data[chat_id]["filenames"]
    message_ids_str = ""
    
    for idx, file_message in enumerate(files):
        sent_message = await file_message.forward(Config.DB_CHANNEL)
        file_id = str(sent_message.id)
        file_name = filenames[idx]
        message_ids_str += f"{file_id} "
        await file_message.reply_text(
            f"**File:** {file_name}\n**Link:** https://redirect.nonamebesty.workers.dev?start=Shakthimaan_{str_to_b64(file_id)}"
        )
    
    share_link = f"https://redirect.nonamebesty.workers.dev?start=Shakthimaan_{str_to_b64(message_ids_str.strip())}"
    
    await bot.send_message(
        chat_id=chat_id,
        text=f"All files uploaded successfully!\n\n**Link:** {share_link}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Open Link", url=share_link)]]
        )
    )

bot.run()
