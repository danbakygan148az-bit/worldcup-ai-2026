import asyncio
import logging
import os
import requests

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

BASE_URL = "https://worldcup26.ir/api"


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        ]
    )


def home_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚽ Матчи сегодня",
                    callback_data="today_matches",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Расписание",
                    callback_data="schedule",
                ),
                InlineKeyboardButton(
                    text="🏆 Группы",
                    callback_data="groups",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🌍 Команды",
                    callback_data="teams",
                ),
                InlineKeyboardButton(
                    text="🌐 Language",
                    callback_data="language",
                ),
            ],
        ]
    )


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        """
🏆 <b>Welcome to WorldCup AI</b>

Ваш помощник по Чемпионату мира 2026 ⚽

Выберите язык:
""",
        reply_markup=language_keyboard(),
    )


@dp.callback_query(F.data.startswith("lang_"))
async def language_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        """
🏆 <b>WorldCup AI</b>

Добро пожаловать!

Выберите раздел:
""",
        reply_markup=home_keyboard(),
    )


def get_today_matches():
    try:
        response = requests.get(
            "https://worldcup26.ir/get/games",
            timeout=10
        )

        matches = response.json()

        text = "⚽ <b>Ближайшие матчи</b>\n\n"

        for match in matches[:5]:
            home = match.get("home", "TBD")
            away = match.get("away", "TBD")
            date = match.get("date", "")
            time = match.get("time", "")

            text += (
                f"🏟 <b>{home}</b> vs <b>{away}</b>\n"
                f"📅 {date}\n"
                f"🕒 {time}\n\n"
            )

        return text

    except Exception as e:
        print("MATCH API ERROR:", e)

        return """
⚠️ Не удалось загрузить матчи.

Попробуйте позже.
"""


@dp.callback_query(F.data == "today_matches")
async def today_matches(callback: CallbackQuery):
    await callback.answer()

    text = get_today_matches()

    await callback.message.answer(text)


@dp.callback_query(F.data == "schedule")
async def schedule(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        """
📅 <b>Расписание ЧМ-2026</b>

1️⃣ Group Stage

2️⃣ Round of 32

3️⃣ Round of 16

4️⃣ Quarterfinals

5️⃣ Semifinals

6️⃣ Final 🏆
"""
    )


@dp.callback_query(F.data == "groups")
async def groups(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        """
🏆 <b>Группы</b>

Данные скоро будут загружаться автоматически.
"""
    )


@dp.callback_query(F.data == "teams")
async def teams(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        """
🌍 <b>Команды</b>

Список сборных скоро будет загружаться автоматически.
"""
    )


@dp.callback_query(F.data == "language")
async def language(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "🌐 Выберите язык:",
        reply_markup=language_keyboard(),
    )


@dp.message()
async def text_handler(message: Message):
    await message.answer(
        """
⚽ Используйте меню.

Нажмите:
• Матчи сегодня
• Расписание
• Группы
• Команды
"""
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
