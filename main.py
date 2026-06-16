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


# ---------------- KEYBOARDS ----------------

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


# ---------------- START ----------------

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


# ---------------- TODAY MATCHES ----------------

@dp.callback_query(F.data == "today_matches")
async def today_matches(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        """
⚽ <b>Матчи сегодня</b>

🇧🇷 Brazil vs France 🇫🇷
🕗 20:00

🇦🇷 Argentina vs Germany 🇩🇪
🕙 22:00

🇪🇸 Spain vs Mexico 🇲🇽
🕕 18:00
"""
    )


# ---------------- SCHEDULE ----------------

@dp.callback_query(F.data == "schedule")
async def schedule(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        """
📅 <b>Расписание ЧМ-2026</b>

1️⃣ Group Stage

2️⃣ Round of 16

3️⃣ Quarterfinals

4️⃣ Semifinals

5️⃣ Final 🏆
"""
    )


# ---------------- GROUPS ----------------

@dp.callback_query(F.data == "groups")
async def groups(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        """
🏆 <b>Группы ЧМ-2026</b>

<b>Group A</b>
🇧🇷 Brazil
🇫🇷 France
🇲🇽 Mexico
🇯🇵 Japan

<b>Group B</b>
🇦🇷 Argentina
🇩🇪 Germany
🇪🇸 Spain
🇺🇸 USA
"""
    )


# ---------------- TEAMS ----------------

@dp.callback_query(F.data == "teams")
async def teams(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        """
🌍 <b>Команды</b>

🇧🇷 Brazil
🇫🇷 France
🇦🇷 Argentina
🇩🇪 Germany
🇪🇸 Spain
🇲🇽 Mexico
🇺🇸 USA
🇯🇵 Japan
"""
    )


# ---------------- LANGUAGE ----------------

@dp.callback_query(F.data == "language")
async def language(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "🌐 Выберите язык:",
        reply_markup=language_keyboard(),
    )


# ---------------- TEXT ----------------

@dp.message()
async def text_handler(message: Message):
    await message.answer(
        """
⚽ Используйте кнопки меню.

Нажмите:
• Матчи сегодня
• Расписание
• Группы
• Команды
"""
    )


# ---------------- MAIN ----------------

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
