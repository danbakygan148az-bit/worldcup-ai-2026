import asyncio
import logging
import os
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()


# ---------------- MENU ----------------

def menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚽ Матчи", callback_data="matches")],
            [InlineKeyboardButton(text="📅 Расписание", callback_data="schedule")],
            [InlineKeyboardButton(text="🏆 Группы", callback_data="groups")],
            [InlineKeyboardButton(text="🌍 Команды", callback_data="teams")],
            [InlineKeyboardButton(text="🏟 Стадионы", callback_data="stadiums")],
        ]
    )


# ---------------- START ----------------

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🏆 <b>World Cup 2026</b>\n\nВыберите раздел:",
        reply_markup=menu()
    )


# ---------------- REAL API ----------------

async def fetch_matches():
    """
    Бесплатный публичный ESPN scoreboard API
    (работает без ключа)
    """
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()

        events = data.get("events", [])

        if not events:
            return "⚽ Сейчас нет доступных матчей."

        text = "⚽ <b>Реальные матчи</b>\n\n"

        for e in events[:5]:
            comp = e["competitions"][0]
            teams = comp["competitors"]

            home = teams[0]["team"]["displayName"]
            away = teams[1]["team"]["displayName"]
            status = comp["status"]["type"]["description"]

            text += f"🏟 {home} vs {away}\n📌 {status}\n\n"

        return text

    except Exception as e:
        print("API ERROR:", e)
        return "⚠️ Не удалось загрузить матчи сейчас."


# ---------------- HANDLERS ----------------

@dp.callback_query(F.data == "matches")
async def matches(c: CallbackQuery):
    await c.answer()
    text = await fetch_matches()
    await c.message.answer(text)


@dp.callback_query(F.data == "schedule")
async def schedule(c: CallbackQuery):
    await c.answer()
    await c.message.answer(
        "📅 <b>ЧМ-2026 этапы</b>\n\n"
        "🏁 Group Stage\n"
        "➡ Round of 16\n"
        "➡ Quarterfinals\n"
        "➡ Semifinals\n"
        "🏆 Final"
    )


@dp.callback_query(F.data == "groups")
async def groups(c: CallbackQuery):
    await c.answer()
    await c.message.answer(
        "🏆 <b>Группы (пример структура турнира)</b>\n\n"
        "Group A:\n🇧🇷 Brazil 🇫🇷 France 🇲🇽 Mexico 🇯🇵 Japan\n\n"
        "Group B:\n🇦🇷 Argentina 🇩🇪 Germany 🇪🇸 Spain 🇺🇸 USA"
    )


@dp.callback_query(F.data == "teams")
async def teams(c: CallbackQuery):
    await c.answer()
    await c.message.answer(
        "🌍 <b>Команды</b>\n\n"
        "🇧🇷 Brazil\n🇫🇷 France\n🇦🇷 Argentina\n🇩🇪 Germany\n🇪🇸 Spain\n🇲🇽 Mexico\n🇺🇸 USA\n🇯🇵 Japan"
    )


@dp.callback_query(F.data == "stadiums")
async def stadiums(c: CallbackQuery):
    await c.answer()
    await c.message.answer(
        "🏟 <b>Стадионы ЧМ</b>\n\n"
        "🇺🇸 MetLife Stadium\n"
        "🇺🇸 SoFi Stadium\n"
        "🇲🇽 Estadio Azteca\n"
        "🇨🇦 BMO Field"
    )


@dp.message()
async def fallback(message: Message):
    await message.answer("Используй меню 👇", reply_markup=menu())


# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
