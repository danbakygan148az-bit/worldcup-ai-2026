import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    text = """
🏆 <b>Welcome to WorldCup AI</b>

Твой AI-ассистент по Чемпионату мира 2026 ⚽

Что умею:
📊 Анализ матчей
🧠 AI Coach
🏆 World Cup 2026
🔥 Прогнозы

Напиши название матча:

<b>Например:</b>
Brazil France
"""
    await message.answer(text)


@dp.message()
async def chat_handler(message: Message):
    user_text = message.text.lower()

    if "бразилия" in user_text or "brazil" in user_text:
        await message.answer(
            "🇧🇷 Brazil выглядит сильной командой.\n\n"
            "🧠 Ключевой фактор:\n"
            "быстрые переходы и сильная атака."
        )
    else:
        await message.answer(
            "⚽ WorldCup AI понял запрос.\n\n"
            "Полный AI-анализ скоро будет доступен."
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
