import asyncio
from configs import Config
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64

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

async def save_batch_media_in_channel(bot: Client, editable: Message, message_ids: list):
    try:
        forwarded_messages = []
        for message in (await bot.get_messages(chat_id=editable.chat.id, message_ids=message_ids)):
            sent_message = await forward_to_channel(bot, message, editable)
            if sent_message is None:
                continue
            forwarded_messages.append(sent_message)
            await asyncio.sleep(2)

        user_id = editable.reply_to_message.from_user.id
        user_filename_input[user_id] = {"editable": editable, "messages": forwarded_messages, "filenames": []}

        await editable.edit("Please provide filenames for each file, separated by commas:")
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

@Client.on_message(filters.private & filters.text)
async def receive_filename(bot: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_filename_input:
        return

    filenames = message.text.split(',')
    data = user_filename_input.pop(user_id)
    editable = data["editable"]
    forwarded_messages = data["messages"]

    if len(filenames) != len(forwarded_messages):
        await editable.edit("The number of filenames provided does not match the number of files. Please try again.")
        user_filename_input[user_id] = {"editable": editable, "messages": forwarded_messages, "filenames": []}
        return

    try:
        message_ids_str = ""
        for idx, forwarded_msg in enumerate(forwarded_messages):
            file_er_id = str(forwarded_msg.id)
            filename = filenames[idx].strip()
            await forwarded_msg.reply_text(
                f"#PRIVATE_FILE:\n\n[{message.from_user.first_name}](tg://user?id={message.from_user.id}) Got File Link!",
                disable_web_page_preview=True)
            media = forwarded_msg.document or forwarded_msg.video or forwarded_msg.audio or forwarded_msg.photo
            file_size = humanbytes(media.file_size)
            caption = forwarded_msg.caption if media.file_name else ""
            share_link = f"https://redirect.nonamebesty.workers.dev?start=Shakthimaan_{str_to_b64(file_er_id)}_{filename}"
            message_ids_str += f"{str(forwarded_msg.id)} "
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
    except FloodWait as sl:
        if sl.value > 45:
            print(f"Sleep of {sl.value}s caused by FloodWait ...")
            await asyncio.sleep(sl.value)
            await bot.send_message(
                chat_id=int(Config.LOG_CHANNEL),
                text="#FloodWait:\n"
                     f"Got FloodWait of `{str(sl.value)}s` from `{str(editable.chat.id)}` !!",
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
            text="#ERROR_TRACEBACK:\n"
                 f"Got Error from `{str(editable.chat.id)}` !!\n\n"
                 f"**Traceback:** `{err}`",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                ]
            )
        )

def start_bot():
    print("Bot started.")
    Bot.run()

if __name__ == "__main__":
    start_bot()
