import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
# from aiogram.types import ParseMode
from aiogram.utils import executor
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-3.5-turbo")
MAX_TOKENS = min(int(os.getenv("MAX_TOKENS", 500)), 4096)

if os.getenv("ALLOWED_CHAT_IDS"):
    ALLOWED_CHAT_IDS = [int(chat_id) for chat_id in os.getenv("ALLOWED_CHAT_IDS").split(",")]
    IS_PUBLIC = False
else:
    ALLOWED_CHAT_IDS = []
    IS_PUBLIC = True
if os.getenv("CHAT_HISTORY_SIZE"):
    CHAT_HISTORY_SIZE = int(os.getenv("CHAT_HISTORY_SIZE"))
else:
    CHAT_HISTORY_SIZE = 20


# Create dictionary to keep track of chat IDs and messages history
chat_history = {}


def add_message(chat_id, message):
    if chat_id not in chat_history:
        chat_history[chat_id] = []
    chat_history[chat_id].append(message)
    if len(chat_history[chat_id]) > CHAT_HISTORY_SIZE:
        chat_history[chat_id].pop(0)


def clean_history(chat_id):
    chat_history[chat_id] = []


# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


async def is_allowed(user_id: int) -> bool:
    if user_id in ALLOWED_CHAT_IDS:
        return True
    return IS_PUBLIC


async def send_typing_indicator(chat_id: int):
    await bot.send_chat_action(chat_id, action="typing")

# Command handlers


async def on_start(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    await message.answer(f"Hello! I am a ChatGPT bot.\nI am using {GPT_MODEL}.\nType your message and I'll respond.")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    await message.answer(f"Hello! I'm a ChatGPT bot.\nI am using {GPT_MODEL}.\nSend me a message or a command, and I'll respond!")


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    help_text = (
        "Here's a list of available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/info - Get information about the bot\n"
        "/status - Check the bot's status\n"
        "/newtopic - Clear ChatGPT conversation history"
    )
    await message.answer(help_text)


@dp.message_handler(commands=['info'])
async def info_command(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    info_text = f"I'm a ChatGPT bot.\nI am using {GPT_MODEL}.\nI can respond to your messages and a few basic commands."
    await message.answer(info_text)


@dp.message_handler(commands=['status'])
async def status_command(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    status_text = "I'm currently up and running!"
    await message.answer(status_text)


@dp.message_handler(commands=['newtopic'])
async def status_command(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    clean_history(message.chat.id)
    status_text = "ChatGPT conversation history is cleared!"
    await message.answer(status_text)


@dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def new_chat_member_handler(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    new_members = message.new_chat_members
    me = await bot.get_me()

    if me in new_members:
        await on_start(message)
        await help_command(message)

# Message handlers


@dp.message_handler()
async def reply(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    input_text = message.text
    add_message(message.chat.id, {"role": "user", "content": input_text})
    await send_typing_indicator(message.chat.id)
    response_text = await chatgpt_request(chat_history[message.chat.id])
    await message.reply(response_text)
    add_message(message.chat.id, {"role": "assistant", "content": response_text})


async def chatgpt_request(messages_history):
    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
    }

    data = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": MAX_TOKENS,
        "messages": messages_history
    }
    # data = {
    #     "prompt": prompt,
    #     "max_tokens": 50,
    # }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as response:  # Change the URL to use gpt-3.5-turbo
            response.raise_for_status()
            result = await response.json()
    return result["choices"][0]["message"]["content"].strip()

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
