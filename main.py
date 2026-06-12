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
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()

user_language = {}
favorite_team = {}


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
                InlineKeyboardButton(text="🇪🇸 Spain", callback_data="team_spain")
            ],
        ]
    )


def home_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚽ Матчи", callback_data="matches"),
                InlineKeyboardButton(text="🏆 ЧМ-2026", callback_data="worldcup"),
            ],
            [
                InlineKeyboardButton(text="📊 Анализ", callback_data="analysis"),
                InlineKeyboardButton(text="🧠 AI Coach", callback_data="coach"),
            ],
            [
                InlineKeyboardButton(text="🔥 Прогнозы", callback_data="predictions")
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
async def language_selected(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚽ Выбери любимую сборную:",
        reply_markup=teams_keyboard(),
    )


@dp.callback_query(F.data.startswith("team_"))
async def team_selected(callback: CallbackQuery):
    team = callback.data.replace("team_", "")

    await callback.message.edit_text(
        f"""
🏆 <b>WorldCup AI</b>

Любимая команда:
<b>{team.title()}</b>
""",
        reply_markup=home_keyboard(),
    )


async def football_ai(prompt: str):
    text = prompt.lower()

    if "brazil" in text or "бразилия" in text:
        return """
🇧🇷 <b>Brazil Analysis</b>

⚽ Brazil выглядит очень опасно в атаке.

🧠 Сильные стороны:
• быстрые фланги
• высокий прессинг
• техника

🎯 Прогноз:
Brazil фаворит.
Вероятный счёт: <b>2:1</b>
"""

    elif "germany" in text or "германия" in text:
        return """
🇩🇪 <b>Germany Analysis</b>

⚽ Germany часто доминирует через владение.

🧠 Проблема:
потеря темпа под высоким прессингом.

🎯 Прогноз:
Шансы хорошие,
но защита нестабильна.
"""

    elif "france" in text or "франция" in text:
        return """
🇫🇷 <b>France Analysis</b>

⚽ France выглядит одной из сильнейших сборных.

🧠 Ключ:
баланс между обороной и атакой.

🎯 Прогноз:
топ-кандидат на титул.
"""

    elif "кто выиграет" in text:
        return """
🏆 <b>World Cup Prediction</b>

1. 🇫🇷 France
2. 🇧🇷 Brazil
3. 🇦🇷 Argentina

🧠 AI считает France фаворитом.
"""

    elif "vs" in text or " " in text:
        return f"""
⚽ <b>Match Analysis</b>

🧠 {prompt.title()} выглядит как матч высокого уровня.

🎯 Вероятный счёт:
<b>2:1</b>

🔥 Игра будет напряжённой.
"""

    return """
⚽ <b>WorldCup AI</b>

Спроси про:
• Brazil France
• Кто выиграет ЧМ?
• Почему Germany проиграла?
"""

@dp.message()
async def smart_chat(message: Message):
    wait_message = await message.answer(
        "🧠 Анализирую матч..."
    )

    try:
        result = await football_ai(message.text)

        await wait_message.edit_text(result)

    except Exception:
        await wait_message.edit_text(
            "⚠️ AI временно недоступен."
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
