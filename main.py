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

print("🚀 WORLD CUP BOT FIXED API VERSION")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()

API = "https://worldcup26.ir/get"


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
        "🏆 <b>World Cup 2026 AI</b>\n\nВыберите раздел:",
        reply_markup=menu()
    )


# ---------------- HTTP ----------------

async def fetch(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as r:
                return await r.json()
    except Exception as e:
        print("API ERROR:", e)
        return None


# ---------------- MATCHES ----------------

@dp.callback_query(F.data == "matches")
async def matches(c: CallbackQuery):
    await c.answer()

    msg = await c.message.answer("⏳ Загружаем матчи...")

    data = await fetch(f"{API}/games")

    if not data:
        await msg.edit_text("⚠️ API недоступен")
        return

    text = "⚽ <b>Матчи</b>\n\n"

    for m in data[:12]:
        home = m.get("home", "TBD")
        away = m.get("away", "TBD")
        score = m.get("score", "")
        status = m.get("status", "")

        if score:
            text += f"🏟 {home} {score} {away}\n"
        else:
            text += f"🏟 {home} vs {away}\n"

        text += f"📌 {status}\n\n"

    await msg.edit_text(text)


# ---------------- SCHEDULE ----------------

@dp.callback_query(F.data == "schedule")
async def schedule(c: CallbackQuery):
    await c.answer()

    data = await fetch(f"{API}/schedule")

    if not data:
        await c.message.answer("⚠️ Ошибка расписания")
        return

    text = "📅 <b>Ближайшие матчи (24h)</b>\n\n"

    for m in data[:12]:
        text += (
            f"🏟 {m.get('home')} vs {m.get('away')}\n"
            f"🕒 {m.get('date')} {m.get('time')}\n\n"
        )

    await c.message.answer(text)


# ---------------- GROUPS ----------------

@dp.callback_query(F.data == "groups")
async def groups(c: CallbackQuery):
    await c.answer()

    data = await fetch(f"{API}/groups")

    if not data:
        await c.message.answer("⚠️ Ошибка групп")
        return

    kb = []

    for g in data:
        kb.append([InlineKeyboardButton(text=f"Group {g['name']}", callback_data=f"group_{g['name']}")])

    await c.message.answer("🏆 Выберите группу:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


@dp.callback_query(F.data.startswith("group_"))
async def group_detail(c: CallbackQuery):
    await c.answer()

    group_name = c.data.split("_")[1]

    data = await fetch(f"{API}/groups/{group_name}")

    if not data:
        await c.message.answer("⚠️ Ошибка группы")
        return

    text = f"🏆 <b>Group {group_name}</b>\n\n"

    for team in data.get("teams", []):
        text += f"🌍 {team}\n"

    text += "\n⚽ Matches:\n\n"

    for m in data.get("matches", []):
        home = m.get("home")
        away = m.get("away")
        score = m.get("score", "")

        text += f"{home} {score} {away}\n"

    await c.message.answer(text)


# ---------------- TEAMS ----------------

@dp.callback_query(F.data == "teams")
async def teams(c: CallbackQuery):
    await c.answer()

    data = await fetch(f"{API}/teams")

    if not data:
        await c.message.answer("⚠️ Ошибка команд")
        return

    text = "🌍 <b>Все команды</b>\n\n"

    for t in data:
        text += f"🇳🇱 {t}\n"

    await c.message.answer(text)


# ---------------- STADIUMS ----------------

@dp.callback_query(F.data == "stadiums")
async def stadiums(c: CallbackQuery):
    await c.answer()

    data = await fetch(f"{API}/stadiums")

    if not data:
        await c.message.answer("⚠️ Ошибка стадионов")
        return

    text = "🏟 <b>Стадионы</b>\n\n"

    for s in data:
        text += f"{s['name']} — {s['capacity']} seats\n"

    await c.message.answer(text)


# ---------------- FALLBACK ----------------

@dp.message()
async def fallback(message: Message):
    await message.answer("Используй меню 👇", reply_markup=menu())


# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
