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

user_language = {}
favorite_team = {}


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский",
                    callback_data="lang_ru",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇬🇧 English",
                    callback_data="lang_en",
                )
            ],
        ]
    )


def teams_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇧🇷 Brazil",
                    callback_data="team_brazil",
                ),
                InlineKeyboardButton(
                    text="🇫🇷 France",
                    callback_data="team_france",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇦🇷 Argentina",
                    callback_data="team_argentina",
                ),
                InlineKeyboardButton(
                    text="🇩🇪 Germany",
                    callback_data="team_germany",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇪🇸 Spain",
                    callback_data="team_spain",
                )
            ],
        ]
    )


def home_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚽ Матчи",
                    callback_data="matches",
                ),
                InlineKeyboardButton(
                    text="🏆 ЧМ-2026",
                    callback_data="worldcup",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 Анализ",
                    callback_data="analysis",
                ),
                InlineKeyboardButton(
                    text="🧠 AI Coach",
                    callback_data="coach",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Прогнозы",
                    callback_data="predictions",
                )
            ],
        ]
    )


@dp.message(CommandStart())
async def start_handler(message: Message):
    text = """
🏆 <b>Welcome to WorldCup AI</b>

Твой AI-ассистент по Чемпионату мира 2026 ⚽

Выбери язык:
"""
    await message.answer(
        text,
        reply_markup=language_keyboard(),
    )


@dp.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery):
    lang = callback.data.replace("lang_", "")
    user_language[callback.from_user.id] = lang

    await callback.message.edit_text(
        "⚽ Выбери любимую сборную:",
        reply_markup=teams_keyboard(),
    )


@dp.callback_query(F.data.startswith("team_"))
async def team_selected(callback: CallbackQuery):
    team = callback.data.replace("team_", "")
    favorite_team[callback.from_user.id] = team

    await callback.message.edit_text(
        f"""
🏆 <b>WorldCup AI</b>

Любимая команда:
<b>{team.title()}</b>

Добро пожаловать ⚽
""",
        reply_markup=home_keyboard(),
    )


@dp.callback_query(F.data == "matches")
async def matches(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        """
⚽ <b>Матчи сегодня</b>

🇧🇷 Brazil vs France 🇫🇷
20:00

🇦🇷 Argentina vs Germany 🇩🇪
22:00
"""
    )


@dp.callback_query(F.data == "analysis")
async def analysis(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        """
📊 <b>AI Analysis</b>

France выглядит немного сильнее.

🧠 Ключ:
контроль центра поля.

🎯 Прогноз:
2:1
"""
    )


@dp.callback_query(F.data == "coach")
async def coach(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        """
🧠 <b>AI Coach</b>

Germany проиграла центр поля
и слишком часто теряла мяч под прессингом.
"""
    )


@dp.message()
async def smart_chat(message: Message):
    text = message.text.lower()

    if "brazil" in text or "бразилия" in text:
        await message.answer(
            """
🇧🇷 Brazil Analysis

Brazil выглядит сильно.

🎯 AI Score:
2:1
"""
        )

    elif "кто выиграет" in text:
        await message.answer(
            """
🏆 Prediction

1. France
2. Brazil
3. Argentina
"""
        )

    else:
        await message.answer(
            """
⚽ WorldCup AI понял запрос.

Полный AI-анализ скоро.
"""
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
