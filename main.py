import asyncio
import logging
import aiohttp
import os
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
TEAM_NAMES = {
    "Canada": "Канада", "Mexico": "Мексика", "United States": "США", "USA": "США",
    "Japan": "Япония", "New Zealand": "Новая Зеландия", "Australia": "Австралия",
    "Iraq": "Ирак", "Iran": "Иран", "Jordan": "Иордания", "South Korea": "Южная Корея",
    "Korea Republic": "Южная Корея", "Qatar": "Катар", "Saudi Arabia": "Саудовская Аравия",
    "Uzbekistan": "Узбекистан",
    "Algeria": "Алжир", "Cape Verde": "Кабо-Верде", "DR Congo": "ДР Конго",
    "Congo DR": "ДР Конго", "Ivory Coast": "Кот-д'Ивуар", "Côte d'Ivoire": "Кот-д'Ивуар",
    "Egypt": "Египет", "Ghana": "Гана", "Morocco": "Марокко", "Senegal": "Сенегал",
    "South Africa": "ЮАР", "Tunisia": "Тунис",
    "Curacao": "Кюрасао", "Haiti": "Гаити", "Panama": "Панама",
    "Argentina": "Аргентина", "Brazil": "Бразилия", "Colombia": "Колумбия",
    "Ecuador": "Эквадор", "Paraguay": "Парагвай", "Uruguay": "Уругвай",
    "Austria": "Австрия", "Belgium": "Бельгия", "Bosnia and Herzegovina": "Босния и Герцеговина",
    "Croatia": "Хорватия", "Czech Republic": "Чехия", "Czechia": "Чехия",
    "England": "Англия", "France": "Франция", "Germany": "Германия",
    "Netherlands": "Нидерланды", "Norway": "Норвегия", "Portugal": "Португалия",
    "Scotland": "Шотландия", "Spain": "Испания", "Sweden": "Швеция",
    "Switzerland": "Швейцария", "Turkey": "Турция", "Türkiye": "Турция",
}

def ru_team(name: str) -> str:
    return TEAM_NAMES.get(name, name)

# Полный список всех 48 команд на русском
ALL_TEAMS = [
    "🇦🇷 Аргентина", "🇦🇺 Австралия", "🇦🇹 Австрия", "🇩🇿 Алжир", "🇧🇪 Бельгия",
    "🇧🇷 Бразилия", "🇧🇦 Босния и Герцеговина", "🇬🇭 Гана", "🇩🇪 Германия",
    "🇭🇹 Гаити", "🇪🇨 Эквадор", "🇪🇬 Египет", "🇮🇷 Иран", "🇮🇶 Ирак", "🇪🇸 Испания",
    "🇮🇹 Италия", "🇯🇵 Япония", "🇯🇴 Иордания", "🇰🇷 Южная Корея", "🇨🇦 Канада",
    "🇶🇦 Катар", "🇨🇴 Колумбия", "🇨🇷 Коста-Рика", "🇨🇮 Кот-д'Ивуар", "🇨🇼 Кюрасао",
    "🇲🇦 Марокко", "🇲🇽 Мексика", "🇳🇱 Нидерланды", "🇳🇿 Новая Зеландия",
    "🇳🇴 Норвегия", "🇵🇦 Панама", "🇵🇾 Парагвай", "🇵🇹 Португалия", "🇷🇺 Россия",
    "🇸🇦 Саудовская Аравия", "🇸🇳 Сенегал", "🇷🇸 Сербия", "🇺🇸 США", "🇹🇳 Тунис",
    "🇹🇷 Турция", "🇺🇾 Уругвай", "🇺🇿 Узбекистан", "🇨🇱 Чили", "🇨🇿 Чехия",
    "🇨🇭 Швейцария", "🇸🇪 Швеция", "🇿🇦 ЮАР", "🇫🇷 Франция", "🇭🇷 Хорватия",
    "🇬🇧 Англия", "🇵🇪 Перу"  # добавил на всякий случай, если будут изменения
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

# ==================== API ====================
async def get_matches():
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=12) as resp:
                data = await resp.json()

        events = data.get("events", [])
        if not events:
            return "⚽ Сейчас нет активных матчей."

        text = "⚽ <b>Текущие матчи ЧМ-2026</b>\n\n"
        for e in events[:10]:
            comp = e["competitions"][0]
            teams = comp["competitors"]
            home = ru_team(teams[0]["team"]["displayName"])
            away = ru_team(teams[1]["team"]["displayName"])
            status = comp["status"]["type"]["shortDetail"]
            venue = comp.get("venue", {}).get("fullName", "—")

            # Время в МСК
            try:
                dt = datetime.fromisoformat(e.get("date", "").replace("Z", "+00:00"))
                dt = dt + timedelta(hours=3)
                match_time = dt.strftime("%d.%m %H:%M")
            except:
                match_time = "—"

            score = ""
            if teams[0].get("score") is not None and teams[1].get("score") is not None:
                score = f" {teams[0]['score']}–{teams[1]['score']}"

            text += f"<b>{home} — {away}</b>{score}\n⏰ {match_time} МСК\n📍 {venue}\n{status}\n\n"

        return text
    except Exception as e:
        logging.error(f"API Error: {e}")
        return "⚠️ Не удалось загрузить матчи. Попробуйте позже."

# ==================== ХЕНДЛЕРЫ ====================
@dp.callback_query(F.data == "matches")
async def matches_handler(c: CallbackQuery):
    await c.answer()
    msg = await c.message.edit_text("⏳ Загружаем актуальные матчи...")
    text = await get_matches()
    await msg.edit_text(text, reply_markup=back_menu())

@dp.callback_query(F.data == "teams")
async def teams_handler(c: CallbackQuery):
    await c.answer()
    text = "🌍 <b>Все сборные на ЧМ-2026 (48 команд)</b>\n\n"
    for team in ALL_TEAMS:
        text += f"• {team}\n"
    await c.message.edit_text(text, reply_markup=back_menu())

@dp.callback_query(F.data == "schedule")
async def schedule_handler(c: CallbackQuery):
    await c.answer()
    await c.message.edit_text(
        "📅 <b>Расписание матчей</b>\n\n"
        "Полное расписание пока в разработке.\n"
        "Можешь посмотреть на официальном сайте ФИФА.",
        reply_markup=back_menu()
    )

@dp.callback_query(F.data == "groups")
async def groups_handler(c: CallbackQuery):
    await c.answer()
    await c.message.edit_text(
        "🏆 <b>Группы ЧМ-2026</b>\n\n"
        "Группы будут доступны после жеребьёвки.\n"
        "Следи за обновлениями!",
        reply_markup=back_menu()
    )

@dp.callback_query(F.data == "stadiums")
async def stadiums_handler(c: CallbackQuery):
    await c.answer()
    await c.message.edit_text(
        "🏟 <b>Главные стадионы ЧМ-2026</b>\n\n"
        "• MetLife Stadium (Нью-Йорк)\n"
        "• SoFi Stadium (Лос-Анджелес)\n"
        "• Estadio Azteca (Мехико)\n"
        "• BMO Field (Торонто)\n"
        "и другие...",
        reply_markup=back_menu()
    )

@dp.callback_query(F.data == "back")
async def back_handler(c: CallbackQuery):
    await c.answer()
    await c.message.edit_text(
        "🏆 <b>World Cup 2026 Bot</b>\nВыберите раздел:",
        reply_markup=menu()
    )

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🏆 <b>Добро пожаловать в World Cup 2026 Bot!</b>\n\n"
        "Выберите нужный раздел ниже 👇",
        reply_markup=menu()
    )

@dp.message()
async def fallback(message: Message):
    await message.answer("Используй меню 👇", reply_markup=menu())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
