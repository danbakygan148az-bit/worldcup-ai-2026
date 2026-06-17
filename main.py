import asyncio
import logging
import aiohttp
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

print("🚀 STABLE WORLD CUP BOT RUNNING")

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


def back_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ]
    )

# ---------------- SAFE API (ESPN REAL) ----------------

async def get_matches():
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as r:
                data = await r.json()

        events = data.get("events", [])

        if not events:
            return "⚽ Нет активных матчей сейчас."

        text = "⚽ <b>Матчи</b>\n\n"

        for e in events[:8]:
            comp = e["competitions"][0]
            teams = comp["competitors"]

            home = teams[0]["team"]["displayName"]
            away = teams[1]["team"]["displayName"]

            status = comp["status"]["type"]["shortDetail"]

            venue = "Неизвестно"
            if comp.get("venue"):
                venue = comp["venue"].get("fullName", "Неизвестно")

            raw_date = e.get("date", "")

            try:
                dt = datetime.fromisoformat(
                    raw_date.replace("Z", "+00:00")
                )
            
                dt = dt + timedelta(hours=3)
            
                match_time = dt.strftime("%d.%m.%Y %H:%M МСК")
            
            except Exception:
                match_time = raw_date
            
            score = ""

            try:
                home_score = teams[0].get("score", "")
                away_score = teams[1].get("score", "")

                if home_score != "" and away_score != "":
                    score = f"\n⚽ Счёт: {home_score}-{away_score}"
            except Exception:
                pass

            text += (
                f"🏟 <b>{home} vs {away}</b>\n"
                f"⏰ {match_time}\n"
                f"📍 {venue}\n"
                f"{score}\n"
                f"📌 {status}\n\n"
            )

        return text

    except Exception as e:
        print("MATCH API ERROR:", e)
        return "⚠️ Матчи временно недоступны"


# ---------------- HANDLERS ----------------

@dp.callback_query(F.data == "matches")
async def matches(c: CallbackQuery):
    await c.answer()

    msg = await c.message.answer("⏳ Загружаем матчи...")

    text = await get_matches()

    await msg.edit_text(
        text,
        reply_markup=back_menu()
    )


@dp.callback_query(F.data == "schedule")
async def schedule(c: CallbackQuery):
    await c.answer()

    await c.message.answer(
        "📅 <b>Расписание (пример)</b>\n\n"
        "⚽ Сегодня\n"
        "⚽ Завтра\n\n"
        "ℹ️ Реальные данные зависят от турниров ESPN"
    )


@dp.callback_query(F.data == "groups")
async def groups(c: CallbackQuery):
    await c.answer()

    await c.message.answer(
        "🏆 <b>Группы</b>\n\n"
        "Group A: Brazil, France\n"
        "Group B: Argentina, Germany\n"
        "Group C: Spain, USA"
    )


@dp.callback_query(F.data == "teams")
async def teams(c: CallbackQuery):
    await c.answer()

    await c.message.answer(
        "🌍 <b>Команды</b>\n\n"
        "Brazil\nFrance\nArgentina\nGermany\nSpain\nUSA"
    )


@dp.callback_query(F.data == "stadiums")
async def stadiums(c: CallbackQuery):
    await c.answer()

    await c.message.answer(
        "🏟 <b>Стадионы</b>\n\n"
        "MetLife Stadium\nSoFi Stadium\nEstadio Azteca\nBMO Field"
    )

@dp.callback_query(F.data == "back")
async def back(c: CallbackQuery):
    await c.answer()

    await c.message.edit_text(
        "🏆 World Cup Bot\nВыберите раздел:",
        reply_markup=menu()
    )
    
@dp.message()
async def fallback(message: Message):
    await message.answer("Используй меню 👇", reply_markup=menu())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
