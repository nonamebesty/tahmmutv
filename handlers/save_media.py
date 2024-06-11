import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from pyrogram import Client, filters
import config

API_TOKEN = 'YOUR_BOT_TOKEN'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    waiting_for_filename = State()

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.reply_text(
        text="**Choose an option from below:**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Save in Batch", callback_data="addToBatchTrue")],
            [InlineKeyboardButton("Single Link", callback_data="addToBatchFalse")]
        ]),
        quote=True,
        disable_web_page_preview=True
    )

@dp.callback_query_handler(lambda c: c.data == 'addToBatchTrue')
async def process_callback_save_in_batch(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Please send the filename:")
    await Form.waiting_for_filename.set()

@dp.message_handler(state=Form.waiting_for_filename, content_types=types.ContentTypes.TEXT)
async def process_filename(message: types.Message, state: FSMContext):
    filename = message.text
    await state.update_data(filename=filename)
    await state.finish()
    # Generate the output link with the filename
    output_link = f"https://redirect.nonamebesty.workers.dev?start=Shakthimaan_{filename}"

    await message.reply_text(
        f"Filename: {filename}\nOutput link: {output_link}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Open Link", url=output_link)],
             [InlineKeyboardButton("Bots Channel", url="https://telegram.me/AS_botzz"),
              InlineKeyboardButton("Support Group", url="https://telegram.me/moviekoodu")]]
        ),
        disable_web_page_preview=True
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
