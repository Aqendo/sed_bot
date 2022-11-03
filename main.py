import subprocess
import logging
import asyncio
from functools import wraps, partial
from aiogram import Bot, Dispatcher, executor, types
import re
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
REGEX = re.compile(r".*/.*/.*")
API_TOKEN = os.environ["BOT_TOKEN"]
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


@async_wrap
def make(input_string: str, sed: str):
    try:
        p1 = subprocess.Popen(["echo", input_string], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["sed", "-E", sed], stdin=p1.stdout, stdout=subprocess.PIPE)
        return p2.communicate()[0].decode("utf-8")
    except Exception as e:
        return f'Error occurred: {str(e)}'


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Author: @Aqendo")


@dp.message_handler()
async def echo(message: types.Message):
    if not re.match(REGEX, message.text):
        return
    result = await make(message.reply_to_message.text, message.text)
    if result == "":
        return
    await bot.send_message(message.chat.id, result, reply_to_message_id=message.reply_to_message.message_id, parse_mode="HTML")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
