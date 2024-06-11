import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import FloodWait
from configs import Config

# Dictionary to store user state for filename input
user_filename_input = {}

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

def str_to_b64(text):
    import base64
    text_bytes = text.encode('ascii')
    base64_bytes = base64.b64encode(text_bytes)
    base64_string = base64_bytes.decode('ascii')
    return base64_string

async def forward_to_channel(bot: Client, message: Message, editable: Message):
    try:
        __SENT = await message.forward(Config.DB_CHANNEL)
        return __SENT
    except FloodWait as sl:
        if sl.value > 45:
            await asyncio.sleep(sl.value)
            await bot.send_message(
                chat_id=int(Config.LOG_CHANNEL),
                text=f"#FloodWait:\nGot FloodWait of `{str(sl.value)}s` from `{str(editable.chat.id)}` !!",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                    ]
                )
            )
        return await forward_to_channel(bot, message, editable)

async def save_batch_media_in_channel(bot: Client, editable: Message, message_ids: list, filenames: list):
    try:
        message_ids_str = ""
        for idx, message_id in enumerate(message_ids):
            message = await bot.get_messages(chat_id=editable.chat.id, message_ids=message_id)
            sent_message = await forward_to_channel(bot, message, editable)
            if sent_message is None:
                continue
            file_er_id = str(sent_message.id)
            filename = filenames[idx].strip()
            message_ids_str += f"{str(sent_message.id)} "
            await asyncio.sleep(2)
            
            # get media type
            media = message.document or message.video or message.audio or message.photo
            # get file size
            file_size = humanbytes(media.file_size)
            # get caption (if any)
            caption = message.caption if media.file_name else ""
            share_link = f"https://redirect.nonamebesty.workers.dev?start=Shakthimaan_{str_to_b64(file_er_id)}_{filename}"
            await editable.edit(
                f"<blockquote>**{caption} - {file_size}\n\nFilename: {filename}\n\n{share_link}**</blockquote>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Open Link", url=share_link)],
                     [InlineKeyboardButton("Bots Channel", url="https://telegram.me/AS_botzz"),
                      InlineKeyboardButton("Support Group", url="https://telegram.me/moviekoodu")]]
                ),
                disable_web_page_preview=True
            )
        
        SaveMessage = await bot.send_message(
            chat_id=Config.DB_CHANNEL,
            text=message_ids_str,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Delete Batch", callback_data="closeMessage")
            ]])
        )
        share_link = f"https://redirect.nonamebesty.workers.dev?start=Shakthimaan_{str_to_b64(str(SaveMessage.id))}"

        await editable.edit(
            f"<blockquote>**Link:** {share_link}</blockquote>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Open Link", url=share_link)],
                 [InlineKeyboardButton("Bots Channel", url="https://telegram.me/AS_botzz"),
                  InlineKeyboardButton("Support Group", url="https://telegram.me/moviekoodu")]]
            ),
            disable_web_page_preview=True
        )
        await bot.send_message(
            chat_id=int(Config.LOG_CHANNEL),
            text=f"#BATCH_SAVE:\n\n[{editable.reply_to_message.from_user.first_name}](tg://user?id={editable.reply_to_message.from_user.id}) Got Batch Link!",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open Link", url=share_link)]])
        )
    except Exception as err:
        await editable.edit(f"Something Went Wrong!\n\n**Error:** `{err}`")
        await bot.send_message(
            chat_id=int(Config.LOG_CHANNEL),
            text=f"#ERROR_TRACEBACK:\nGot Error from `{str(editable.chat.id)}` !!\n\n**Traceback:** `{err}`",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                ]
            )
        )

async def save_media_in_channel(bot: Client, editable: Message, message: Message):
    user_id = message.from_user.id
    user_filename_input[user_id] = {"editable": editable, "message": message}

    await editable.edit("Please provide a filename for this file:")
    return

@Client.on_message(filters.private & filters.text)
async def receive_filename(bot: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_filename_input:
        return

    filename = message.text
    data = user_filename_input.pop(user_id)
    editable = data["editable"]
    original_message = data["message"]

    try:
        forwarded_msg = await original_message.forward(Config.DB_CHANNEL)
        file_er_id = str(forwarded_msg.id)
        await forwarded_msg.reply_text(
            f"#PRIVATE_FILE:\n\n[{original_message.from_user.first_name}](tg://user?id={original_message.from_user.id}) Got File Link!",
            disable_web_page_preview=True)
        # get media type
        media = original_message.document or original_message.video or original_message.audio or original_message.photo
        # get file size
        file_size = humanbytes(media.file_size)
        # get caption (if any)
        caption = original_message.caption if media.file_name else ""
        share_link = f"https://redirect.nonamebesty.workers.dev?start=Shakthimaan_{str_to_b64(file_er_id)}_{filename}"
        await editable.edit(
            f"<blockquote>**{caption} - {file_size}\n\nFilename: {filename}\n\n{share_link}**</blockquote>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Open Link", url=share_link)],
                 [InlineKeyboardButton("Bots Channel", url="https://telegram.me/AS_botzz"),
                  InlineKeyboardButton("Support Group", url="https://telegram.me/moviekoodu")]]
            ),
            disable_web_page_preview=True
        )
    except FloodWait as sl:
        if sl.value > 45:
            await asyncio.sleep(sl.value)
            await bot.send_message(
                chat_id=int(Config.LOG_CHANNEL),
                text=f"#FloodWait:\nGot FloodWait of `{str(sl.value)}s` from `{str(editable.chat.id)}` !!",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                    ]
                )
            )
        await receive_filename(bot, message)
    except Exception as err:
        await editable.edit(f"Something Went Wrong!\n\n**Error:** `{err}`")
        await bot.send_message(
            chat_id=int(Config.LOG_CHANNEL),
            text=f"#ERROR_TRACEBACK:\nGot Error from `{str(editable.chat.id)}` !!\n\n**Traceback:** `{err}`",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                ]
            )
        )

@Client.on_message(filters.private & filters.command("batch"))
async def start_batch_save(bot: Client, message: Message):
    await message.reply_text("How many files do you want to batch save?")
    user_filename_input[message.from_user.id] = {"step": "ask_batch_count"}

@Client.on_message(filters.private & filters.text)
async def handle_text(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_filename_input:
        user_data = user_filename_input[user_id]

        if user_data["step"] == "ask_batch_count":
            try:
                count = int(message.text)
                await message.reply_text(f"Please send the {count} files one by one.")
                user_filename_input[user_id] = {"step": "receive_files", "count": count, "received": 0, "message_ids": []}
            except ValueError:
                await message.reply_text("Please enter a valid number.")

        elif user_data["step"] == "ask_filenames":
            filenames = message.text.split(',')
            if len(filenames) != user_data["count"]:
                await message.reply_text("The number of filenames provided does not match the number of files. Please try again.")
                return

            await save_batch_media_in_channel(bot, user_data["editable"], user_data["message_ids"], filenames)
            del user_filename_input[user_id]

@Client.on_message(filters.private & filters.media)
async def receive_files(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_filename_input:
        user_data = user_filename_input[user_id]

        if user_data["step"] == "receive_files":
            user_data["message_ids"].append(message.message_id)
            user_data["received"] += 1

            if user_data["received"] == user_data["count"]:
                await message.reply_text("Please provide filenames for each file, separated by commas.")
                user_filename_input[user_id] = {"step": "ask_filenames", "editable": message, "count": user_data["count"], "message_ids": user_data["message_ids"]}

if __name__ == "__main__":
    app = Client("my_bot", bot_token=Config.BOT_TOKEN, api_id=Config.API_ID, api_hash=Config.API_HASH)
    app.run()
