import asyncio
import logging
import aiohttp
import os
from datetime import datetime, timedelta   # ← добавил
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

print("🚀 STABLE WORLD CUP BOT RUNNING")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

# ==================== СПИСОК КОМАНД ====================
TEAM_NAMES = { ... }  # твой словарь остаётся без изменений

def ru_team(name: str) -> str:
    return TEAM_NAMES.get(name, name)

# Полный список команд (оставил как было)
ALL_TEAMS = [
    "🇦🇷 Аргентина", "🇦🇺 Австралия", "🇦🇹 Австрия", "🇩🇿 Алжир", "🇧🇪 Бельгия",
    "🇧🇷 Бразилия", "🇧🇦 Босния и Герцеговина", "🇬🇭 Гана", "🇩🇪 Германия",
    "🇭🇹 Гаити", "🇪🇨 Эквадор", "🇪🇬 Египет", "🇮🇷 Иран", "🇮🇶 Ирак", "🇪🇸 Испания",
    "🇯🇵 Япония", "🇯🇴 Иордания", "🇰🇷 Южная Корея", "🇨🇦 Канада",
    "🇶🇦 Катар", "🇨🇴 Колумбия", "🇨🇮 Кот-д'Ивуар", "🇨🇼 Кюрасао",
    "🇲🇦 Марокко", "🇲🇽 Мексика", "🇳🇱 Нидерланды", "🇳🇿 Новая Зеландия",
    "🇳🇴 Норвегия", "🇵🇦 Панама", "🇵🇾 Парагвай", "🇵🇹 Португалия",
    "🇸🇦 Саудовская Аравия", "🇸🇳 Сенегал", "🇺🇸 США", "🇹🇳 Тунис",
    "🇹🇷 Турция", "🇺🇾 Уругвай", "🇺🇿 Узбекистан", "🇨🇿 Чехия",
    "🇨🇭 Швейцария", "🇸🇪 Швеция", "🇿🇦 ЮАР", "🇫🇷 Франция", "🇭🇷 Хорватия",
    "🇬🇧 Англия", "🇵🇪 Перу", "🇨🇱 Чили"
]

# ==================== МЕНЮ ====================
def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Текущие матчи", callback_data="matches")],
        [InlineKeyboardButton(text="📅 Расписание", callback_data="schedule")],
        [InlineKeyboardButton(text="🏆 Группы", callback_data="groups")],
        [InlineKeyboardButton(text="🌍 Все команды", callback_data="teams")],
        [InlineKeyboardButton(text="🏟 Стадионы", callback_data="stadiums")],
    ])

def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back")]
    ])

# ==================== API МАТЧИ ====================
async def get_matches():
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=12) as resp:
                data = await resp.json()

        events = data.get("events", [])
        if not events:
            return "⚽ Сейчас нет активных матчей на ЧМ-2026."

        text = "⚽ <b>Текущие и ближайшие матчи ЧМ-2026</b>\n\n"
        
        for e in events[:12]:   # увеличил немного
            comp = e["competitions"][0]
            teams = comp["competitors"]
            
            home = ru_team(teams[0]["team"]["displayName"])
            away = ru_team(teams[1]["team"]["displayName"])
            
            status = comp["status"]["type"].get("shortDetail", "—")
            venue = comp.get("venue", {}).get("fullName", "—")

            # === ИСПРАВЛЕННЫЙ БЛОК ВРЕМЕНИ ===
            match_time = "—"
            try:
                raw_date = e.get("date") or e.get("startDate")
                if raw_date:
                    dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                    dt = dt + timedelta(hours=3)          # перевод в МСК
                    match_time = dt.strftime("%d.%m.%Y %H:%M МСК")
            except Exception:
                pass

            score = ""
            try:
                h_score = teams[0].get("score", "")
                a_score = teams[1].get("score", "")
                if h_score not in ("", None) and a_score not in ("", None):
                    score = f" <b>{h_score}–{a_score}</b>"
            except:
                pass

            text += (
                f"<b>{home} — {away}</b>{score}\n"
                f"⏰ {match_time}\n"
                f"📍 {venue}\n"
                f"📌 {status}\n\n"
            )

        return text

    except Exception as e:
        logging.error(f"API Error: {e}")
        return "⚠️ Не удалось загрузить матчи. Попробуйте позже."

# ==================== ХЕНДЛЕРЫ (остальное без изменений) ====================
@dp.callback_query(F.data == "matches")
async def matches_handler(c: CallbackQuery):
    await c.answer()
    msg = await c.message.edit_text("⏳ Загружаем матчи...")
    text = await get_matches()
    await msg.edit_text(text, reply_markup=back_menu())

# ... (все остальные хендлеры оставь как в предыдущей версии)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🏆 <b>Добро пожаловать в World Cup 2026 Bot!</b>\n\n"
        "Выберите нужный раздел 👇",
        reply_markup=menu()
    )

@dp.message()
async def fallback(message: Message):
    await message.answer("Используй меню 👇", reply_markup=menu())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
