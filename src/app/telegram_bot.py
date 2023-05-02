import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
from dotenv import load_dotenv
import openai
import duckduckgo as DDG

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MAX_TOKENS = 4096
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
GPT_CHAT_MODEL = os.getenv("GPT_CHAT_MODEL", "gpt-3.5-turbo")
GPT_COMPLETION_MODEL = os.getenv("GPT_COMPLETION_MODEL", "text-davinci-003")
CHAT_HISTORY_SIZE = min(int(os.getenv("CHAT_HISTORY_SIZE", 20)), 50)
MAX_TOKENS = min(int(os.getenv("MAX_TOKENS", 500)), 4096)
NUM_SEARCH_RESULTS = min(int(os.getenv("NUM_SEARCH_RESULTS", 3)), 10)

# If comma separated list of chat IDs is provided, the bot will only work in those chats
# If not provided, the bot will work in all chats
if os.getenv("ALLOWED_CHAT_IDS"):
    ALLOWED_CHAT_IDS = [int(chat_id) for chat_id in os.getenv("ALLOWED_CHAT_IDS").split(",")]
    IS_PUBLIC = False
else:
    ALLOWED_CHAT_IDS = []
    IS_PUBLIC = True


# Create dictionary to keep track of chat IDs and messages history
chat_history = {}
# Dictionary to keep track of web search chat_history
# It only keeps last prompt and last response (text)
web_search_history = {}


def add_chat_message(chat_id, message):
    if chat_id not in chat_history:
        chat_history[chat_id] = []
    chat_history[chat_id].append(message)
    if len(chat_history[chat_id]) > CHAT_HISTORY_SIZE:
        chat_history[chat_id].pop(0)


def clean_chat_history(chat_id):
    chat_history[chat_id] = []


def add_web_search_message(chat_id, message, completion_role):
    if chat_id not in web_search_history:
        web_search_history[chat_id] = {}
    if completion_role == "prompt":
        web_search_history[chat_id]["prompt"] = message
    elif completion_role == "text":
        web_search_history[chat_id]["text"] = message


def clean_web_search_history(chat_id, completion_role: str = "all"):
    if completion_role == "all":
        web_search_history[chat_id] = {}
    if completion_role == "prompt":
        web_search_history[chat_id]['prompt'] = ""
    if completion_role == "text":
        web_search_history[chat_id]['text'] = ""


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
        "/newtopic - Clear ChatGPT conversation history\n"
        "/regen - Regenerate last GPT response\n"
        "/web <query> - Search with Duckduckgo and process results with ChatGPT using query\n"
        "/webregen - Regenerate GPT response on the last web search"
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
async def newtopic_command(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    clean_chat_history(message.chat.id)
    status_text = "ChatGPT conversation history is cleared!"
    await message.answer(status_text)


@dp.message_handler(commands=['regen'])
async def regenerate_command(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    if chat_history.get(message.chat.id):
        chat_history[message.chat.id].pop()
    await send_typing_indicator(message.chat.id)
    regen_message = await message.answer("Generating new answer…")
    response_text = await chatgpt_chat_completion_request(chat_history[message.chat.id])
    await regen_message.delete()
    await message.answer(f"Generating new respose on your query:\n<i><b>{chat_history[message.chat.id][-1]['content']}</b></i>\n\n{response_text}", parse_mode=ParseMode.HTML)
    add_chat_message(message.chat.id, {"role": "assistant", "content": response_text})


@dp.message_handler(commands=['web'])
async def websearch_command(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return
    query = message.get_args()
    search_message = await message.answer("Searching…")
    await send_typing_indicator(message.chat.id)
    web_search_result, result_status = await DDG.web_search(query, NUM_SEARCH_RESULTS)
    if result_status == "OK":
        chat_gpt_instruction = 'Instructions: Using the provided web search results, write a comprehensive reply to the given query. Make sure to cite results using [number] notation after the reference. If the provided search results refer to multiple subjects with the same name, write separate anwers for each subject. In the end of answer provide a list of all used URLs.'
        input_text = web_search_result + "\n\n" + chat_gpt_instruction + "\n\n" + "Query: " + query + "\n"
        add_web_search_message(message.chat.id, input_text, "prompt")
        await send_typing_indicator(message.chat.id)
        response_text = await chatgpt_completion_request(input_text)
        add_web_search_message(message.chat.id, response_text, "text")
    if result_status == "ERROR":
        response_text = web_search_result
    await search_message.delete()
    await message.answer(response_text)


@dp.message_handler(commands=['webregen'])
async def web_regenerate_command(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    if not web_search_history.get('prompt'):
        await message.answer("You need to do web search first! Use '/web <query>' command.")
        return
    regen_message = await message.answer("Generating new answer…")
    await send_typing_indicator(message.chat.id)
    response_text = await chatgpt_completion_request(web_search_history[message.chat.id]['prompt'])
    await regen_message.delete()
    await message.answer(response_text)
    add_web_search_message(message.chat.id, response_text, "text")


@ dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def new_chat_member_handler(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    new_members = message.new_chat_members
    me = await bot.get_me()

    if me in new_members:
        await on_start(message)
        await help_command(message)

# Message handlers


@ dp.message_handler()
async def reply(message: types.Message):
    if not await is_allowed(message.from_user.id):
        return  # Ignore the message if the user is not allowed
    input_text = message.text
    add_chat_message(message.chat.id, {"role": "user", "content": input_text})
    await send_typing_indicator(message.chat.id)
    response_text = await chatgpt_chat_completion_request(chat_history[message.chat.id])
    await message.reply(response_text)
    add_chat_message(message.chat.id, {"role": "assistant", "content": response_text})


async def chatgpt_chat_completion_request(messages_history):
    response = openai.ChatCompletion.create(
        model=GPT_CHAT_MODEL,
        temperature=0.7,
        top_p=0.9,
        max_tokens=MAX_TOKENS,
        messages=messages_history
    )

    return response.choices[0].message.content.strip()


async def chatgpt_completion_request(prompt):
    tokens = OPENAI_MAX_TOKENS // 2 - len(prompt.split())
    response = openai.Completion.create(
        model=GPT_COMPLETION_MODEL,
        prompt=prompt,
        temperature=0.7,
        max_tokens=tokens,
        top_p=0.9
    )

    return response.choices[0].text.strip()


if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
