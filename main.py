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

print("🚀 BOT STARTED - WORLD CUP AI V2")

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


# ---------------- API ----------------

async def fetch_matches():
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=8) as resp:
                data = await resp.json()

        events = data.get("events", [])

        if not events:
            return None

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
        return None


# ---------------- MATCHES ----------------

@dp.callback_query(F.data == "matches")
async def matches(c: CallbackQuery):
    await c.answer()

    msg = await c.message.answer("⏳ Загружаем матчи...")

    text = await fetch_matches()

    if not text:
        text = (
            "⚽ <b>Ближайшие матчи</b>\n\n"
            "🇧🇷 Brazil vs France 🇫🇷\n🕗 20:00\n\n"
            "🇦🇷 Argentina vs Germany 🇩🇪\n🕙 22:00\n\n"
            "🇪🇸 Spain vs Mexico 🇲🇽\n🕕 18:00\n\n"
            "📡 Данные временно недоступны, показан fallback"
        )

    await msg.edit_text(text)


# ---------------- SCHEDULE ----------------

@dp.callback_query(F.data == "schedule")
async def schedule(c: CallbackQuery):
    await c.answer()
    await c.message.answer(
        "📅 <b>ЧМ-2026</b>\n\n"
        "🏁 Group Stage\n"
        "➡ Round of 16\n"
        "➡ Quarterfinals\n"
        "➡ Semifinals\n"
        "🏆 Final"
    )


# ---------------- GROUPS ----------------

@dp.callback_query(F.data == "groups")
async def groups(c: CallbackQuery):
    await c.answer()
    await c.message.answer(
        "🏆 <b>Группы</b>\n\n"
        "Group A:\n🇧🇷 Brazil 🇫🇷 France 🇲🇽 Mexico 🇯🇵 Japan\n\n"
        "Group B:\n🇦🇷 Argentina 🇩🇪 Germany 🇪🇸 Spain 🇺🇸 USA"
    )


# ---------------- TEAMS ----------------

@dp.callback_query(F.data == "teams")
async def teams(c: CallbackQuery):
    await c.answer()
    await c.message.answer(
        "🌍 <b>Команды</b>\n\n"
        "🇧🇷 Brazil\n🇫🇷 France\n🇦🇷 Argentina\n🇩🇪 Germany\n🇪🇸 Spain\n🇲🇽 Mexico\n🇺🇸 USA\n🇯🇵 Japan"
    )


# ---------------- STADIUMS ----------------

@dp.callback_query(F.data == "stadiums")
async def stadiums(c: CallbackQuery):
    await c.answer()
    await c.message.answer(
        "🏟 <b>Стадионы ЧМ-2026</b>\n\n"
        "🇺🇸 MetLife Stadium (New York)\n"
        "🇺🇸 SoFi Stadium (Los Angeles)\n"
        "🇲🇽 Estadio Azteca (Mexico City)\n"
        "🇨🇦 BMO Field (Toronto)"
    )


# ---------------- FALLBACK ----------------

@dp.message()
async def fallback(message: Message):
    await message.answer("Используй меню 👇", reply_markup=menu())


# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
