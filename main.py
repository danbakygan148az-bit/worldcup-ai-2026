import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        ]
    )


def teams_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇧🇷 Brazil", callback_data="team_brazil"),
                InlineKeyboardButton(text="🇫🇷 France", callback_data="team_france"),
            ],
            [
                InlineKeyboardButton(text="🇦🇷 Argentina", callback_data="team_argentina"),
                InlineKeyboardButton(text="🇩🇪 Germany", callback_data="team_germany"),
            ],
            [
                InlineKeyboardButton(text="🇪🇸 Spain", callback_data="team_spain"),
            ],
        ]
    )


def home_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚽ Матчи", callback_data="matches"),
                InlineKeyboardButton(text="🏆 ЧМ-2026", callback_data="wc"),
            ],
            [
                InlineKeyboardButton(text="📊 Анализ", callback_data="analysis"),
                InlineKeyboardButton(text="🧠 AI Coach", callback_data="coach"),
            ],
            [
                InlineKeyboardButton(text="🔥 Прогнозы", callback_data="predictions"),
            ],
        ]
    )


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        """
🏆 <b>Welcome to WorldCup AI</b>

Твой AI-ассистент по Чемпионату мира 2026 ⚽

Выбери язык:
""",
        reply_markup=language_keyboard(),
    )


@dp.callback_query(F.data.startswith("lang_"))
async def language_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚽ Выбери любимую сборную:",
        reply_markup=teams_keyboard(),
    )


@dp.callback_query(F.data.startswith("team_"))
async def team_handler(callback: CallbackQuery):
    team = callback.data.replace("team_", "")

    await callback.message.edit_text(
        f"""
🏆 <b>WorldCup AI</b>

Любимая команда:
<b>{team.title()}</b>

Добро пожаловать ⚽
""",
        reply_markup=home_keyboard(),
    )


async def football_ai(text: str):
    text = text.lower()

    if "brazil" in text or "бразилия" in text:
        return """
🇧🇷 <b>Brazil Analysis</b>

⚽ Brazil выглядит очень опасно в атаке.

🧠 Сильные стороны:
• быстрые фланги
• техника
• прессинг

🎯 Прогноз:
<b>2:1</b>
"""

    if "germany" in text or "германия" in text:
        return """
🇩🇪 <b>Germany Analysis</b>

⚽ Germany сильна через контроль мяча.

🧠 Слабость:
давление и быстрые контратаки.

🎯 Прогноз:
Высокие шансы на плей-офф.
"""

    if "france" in text or "франция" in text:
        return """
🇫🇷 <b>France Analysis</b>

⚽ France — один из фаворитов турнира.

🧠 Ключ:
баланс атаки и обороны.

🎯 Прогноз:
полуфинал или финал.
"""

    if "кто выиграет" in text:
        return """
🏆 <b>World Cup Prediction</b>

1. 🇫🇷 France
2. 🇧🇷 Brazil
3. 🇦🇷 Argentina
"""

    return f"""
⚽ <b>Match Analysis</b>

🧠 Анализ:
{ text.title() }

🎯 Прогноз:
<b>2:1</b>

🔥 Матч выглядит напряжённым.
"""


@dp.message()
async def smart_chat(message: Message):
    response = await football_ai(message.text)
    await message.answer(response)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
