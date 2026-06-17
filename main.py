import asyncio
import logging
import aiohttp
import os
from datetime import datetime, timedelta
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
    "🇬🇧 Англия"
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
        [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_main")]
    ])

def schedule_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завтра", callback_data="schedule_tomorrow")],
        [InlineKeyboardButton(text="Ближайшие 3 дня", callback_data="schedule_3days")],
        [InlineKeyboardButton(text="На неделю", callback_data="schedule_week")],
        [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_main")],
    ])

def schedule_back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в расписание", callback_data="schedule")],
        [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_main")],
    ])

# ==================== ФУНКЦИЯ ЗАГРУЗКИ МАТЧЕЙ ====================
async def get_matches_by_date(days_offset: int = 0):
    target_date = datetime.now() + timedelta(days=days_offset)
    date_str = target_date.strftime("%Y%m%d")

    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates={date_str}&limit=100"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as resp:
                if resp.status != 200:
                    return "⚠️ API ESPN временно недоступен"
                data = await resp.json()

        events = data.get("events", [])
        if not events:
            return f"⚽ На {target_date.strftime('%d.%m.%Y')} матчей не найдено."

        text = f"📅 <b>Матчи — {target_date.strftime('%d.%m.%Y')}</b>\n\n"
        count = 0

        for e in events[:20]:
            try:
                comp = e["competitions"][0]
                teams = comp["competitors"]

                home = ru_team(teams[0]["team"]["displayName"])
                away = ru_team(teams[1]["team"]["displayName"])

                status = comp.get("status", {}).get("type", {}).get("shortDetail", "—")
                venue = comp.get("venue", {}).get("fullName", "—")

                match_time = "—"
                try:
                    raw_date = e.get("date") or comp.get("date")
                    if raw_date:
                        dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                        dt = dt + timedelta(hours=3)
                        match_time = dt.strftime("%H:%M")
                except:
                    pass

                score = ""
                try:
                    h = teams[0].get("score", "")
                    a = teams[1].get("score", "")
                    if str(h) not in ("", "None", None) and str(a) not in ("", "None", None):
                        score = f" <b>{h}–{a}</b>"
                except:
                    pass

                text += f"<b>{home} — {away}</b>{score}\n⏰ {match_time} МСК\n📍 {venue}\n📌 {status}\n\n"
                count += 1
            except:
                continue

        return text if count > 0 else f"⚽ На {target_date.strftime('%d.%m')} матчей пока нет."

    except Exception as e:
        logging.error(f"API Error: {e}")
        return "⚠️ Не удалось загрузить расписание. Попробуй позже."

# ==================== СТАДИОНЫ ====================
async def get_stadiums():
    text = "🏟 <b>Стадионы чемпионата мира 2026</b>\n\n"

    text += "🇨🇦 <b>Канада (красные)</b>\n"
    text += "• BMO Field (Торонто) — 43 000 мест\n"
    text += "• BC Place (Ванкувер) — 52 500 мест\n\n"

    text += "🇲🇽 <b>Мексика (зелёные)</b>\n"
    text += "• Estadio Azteca (Мехико) — 82 000 мест\n"
    text += "• Estadio Akron (Гвадалахара) — 46 000 мест\n"
    text += "• Estadio BBVA (Монтеррей) — 53 500 мест\n\n"

    text += "🇺🇸 <b>США (синие)</b>\n"
    text += "• MetLife Stadium (Нью-Йорк / Нью-Джерси) — 82 500 мест (финал)\n"
    text += "• SoFi Stadium (Лос-Анджелес) — 70 000 мест\n"
    text += "• AT&T Stadium (Даллас) — 80 000 мест\n"
    text += "• Mercedes-Benz Stadium (Атланта) — 71 000 мест\n"
    text += "• NRG Stadium (Хьюстон) — 72 000 мест\n"
    text += "• Hard Rock Stadium (Майами) — 65 000 мест\n"
    text += "• Lumen Field (Сиэтл) — 69 000 мест\n"
    text += "• Levi's Stadium (Сан-Франциско) — 68 500 мест\n"
    text += "• Lincoln Financial Field (Филадельфия) — 69 000 мест\n"
    text += "• GEHA Field at Arrowhead Stadium (Канзас-Сити) — 76 000 мест\n"
    text += "• Gillette Stadium (Бостон) — 65 000 мест\n\n"

    text += "Всего будет использовано 16 стадионов."
    return text

# ==================== ХЕНДЛЕРЫ ====================
@dp.callback_query(F.data == "matches")
async def matches_handler(c: CallbackQuery):
    await c.answer()
    msg = await c.message.edit_text("⏳ Загружаем текущие матчи...")
    text = await get_matches_by_date(0)
    await msg.edit_text(text, reply_markup=back_menu())

@dp.callback_query(F.data == "schedule")
async def schedule_main(c: CallbackQuery):
    await c.answer()
    await c.message.edit_text(
        "📅 <b>Расписание матчей ЧМ-2026</b>\n\nВыберите период:",
        reply_markup=schedule_menu()
    )

@dp.callback_query(F.data == "schedule_tomorrow")
async def schedule_tomorrow(c: CallbackQuery):
    await c.answer()
    msg = await c.message.edit_text("⏳ Загружаем матчи на завтра...")
    text = await get_matches_by_date(1)
    await msg.edit_text(text, reply_markup=schedule_back_menu())

@dp.callback_query(F.data == "schedule_3days")
async def schedule_3days(c: CallbackQuery):
    await c.answer()
    msg = await c.message.edit_text("⏳ Загружаем ближайшие 3 дня...")
    text = "📅 <b>Ближайшие 3 дня</b>\n\n"
    for i in range(3):
        day_text = await get_matches_by_date(i)
        text += day_text + "\n" + "—" * 35 + "\n\n"
    await msg.edit_text(text[:4000], reply_markup=schedule_back_menu())

@dp.callback_query(F.data == "schedule_week")
async def schedule_week(c: CallbackQuery):
    await c.answer()
    msg = await c.message.edit_text("⏳ Загружаем расписание на неделю...")
    text = "📅 <b>Расписание на неделю (7 дней)</b>\n\n"
    for i in range(7):
        day_text = await get_matches_by_date(i)
        text += day_text + "\n" + "—" * 35 + "\n\n"
    await msg.edit_text(text[:4000], reply_markup=schedule_back_menu())

@dp.callback_query(F.data == "stadiums")
async def stadiums_handler(c: CallbackQuery):
    await c.answer()
    text = await get_stadiums()
    await c.message.edit_text(text, reply_markup=back_menu())

@dp.callback_query(F.data == "teams")
async def teams_handler(c: CallbackQuery):
    await c.answer()
    text = "🌍 <b>Все сборные на ЧМ-2026</b>\n\n"
    for team in ALL_TEAMS:
        text += f"• {team}\n"
    await c.message.edit_text(text, reply_markup=back_menu())

@dp.callback_query(F.data == "groups")
async def groups_handler(c: CallbackQuery):
    await c.answer()
    await c.message.edit_text("🏆 Группы будут добавлены позже.", reply_markup=back_menu())

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(c: CallbackQuery):
    await c.answer()
    await c.message.edit_text(
        "🏆 <b>World Cup 2026 Bot</b>\n\nВыберите раздел:",
        reply_markup=menu()
    )

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
