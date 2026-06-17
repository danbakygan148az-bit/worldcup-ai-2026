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

# ==================== РЕАЛЬНЫЕ ГРУППЫ ЧМ-2026 ====================
GROUPS_DATA = {
    "A": {
        "teams": ["🇲🇽 Мексика", "🇿🇦 ЮАР", "🇰🇷 Южная Корея", "🇨🇿 Чехия"],
        "standings": [
            ("1", "🇲🇽 Мексика", "1", "1", "0", "0", "2-0", "3"),
            ("2", "🇰🇷 Южная Корея", "1", "1", "0", "0", "2-1", "3"),
            ("3", "🇨🇿 Чехия", "1", "0", "0", "1", "1-2", "0"),
            ("4", "🇿🇦 ЮАР", "1", "0", "0", "1", "0-2", "0"),
        ]
    },
    "B": {
        "teams": ["🇨🇦 Канада", "🇧🇦 Босния и Герцеговина", "🇶🇦 Катар", "🇨🇭 Швейцария"],
        "standings": []
    },
    "C": {
        "teams": ["🇧🇷 Бразилия", "🇲🇦 Марокко", "🇭🇹 Гаити", "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Шотландия"],
        "standings": []
    },
    "D": {
        "teams": ["🇺🇸 США", "🇵🇾 Парагвай", "🇦🇺 Австралия", "🇹🇷 Турция"],
        "standings": []
    },
    "E": {
        "teams": ["🇩🇪 Германия", "🇨🇼 Кюрасао", "🇨🇮 Кот-д'Ивуар", "🇪🇨 Эквадор"],
        "standings": []
    },
    "F": {
        "teams": ["🇳🇱 Нидерланды", "🇯🇵 Япония", "🇸🇪 Швеция", "🇹🇳 Тунис"],
        "standings": []
    },
    "G": {
        "teams": ["🇧🇪 Бельгия", "🇪🇬 Египет", "🇮🇷 Иран", "🇳🇿 Новая Зеландия"],
        "standings": []
    },
    "H": {
        "teams": ["🇪🇸 Испания", "🇨🇻 Кабо-Верде", "🇸🇦 Саудовская Аравия", "🇺🇾 Уругвай"],
        "standings": []
    },
    "I": {
        "teams": ["🇫🇷 Франция", "🇸🇳 Сенегал", "🇮🇶 Ирак", "🇳🇴 Норвегия"],
        "standings": []
    },
    "J": {
        "teams": ["🇦🇷 Аргентина", "🇩🇿 Алжир", "🇦🇹 Австрия", "🇯🇴 Иордания"],
        "standings": []
    },
    "K": {
        "teams": ["🇵🇹 Португалия", "🇨🇩 ДР Конго", "🇺🇿 Узбекистан", "🇨🇴 Колумбия"],
        "standings": []
    },
    "L": {
        "teams": ["🏴󠁧󠁢󠁥󠁮󠁧󠁿 Англия", "🇭🇷 Хорватия", "🇬🇭 Гана", "🇵🇦 Панама"],
        "standings": []
    }
}

def groups_menu():
    buttons = []
    row = []
    for group in "ABCDEFGHIJKL":
        row.append(InlineKeyboardButton(text=f"Группа {group}", callback_data=f"group_{group}"))
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

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

# ==================== ФУНКЦИЯ МАТЧЕЙ ====================
async def get_matches_by_date(days_offset: int = 0):
    target_date = datetime.now() + timedelta(days=days_offset)
    date_str = target_date.strftime("%Y%m%d")

    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates={date_str}&limit=100"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=12) as resp:
                if resp.status != 200:
                    return "⚠️ API ESPN временно недоступен"
                data = await resp.json()

        events = data.get("events", [])
        if not events:
            return f"⚽ На {target_date.strftime('%d.%m.%Y')} матчей не найдено."

        text = f"📅 <b>Матчи — {target_date.strftime('%d.%m.%Y')}</b>\n\n"
        
        for e in events[:15]:
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

                score = "—"
                try:
                    h = teams[0].get("score", "")
                    a = teams[1].get("score", "")
                    if str(h) not in ("", "None", None) and str(a) not in ("", "None", None):
                        score = f"<b>{h}–{a}</b>"
                except:
                    pass

                text += f"<b>{home} — {away}</b>  {score}\n"
                text += f"⏰ {match_time} МСК\n"
                text += f"📍 {venue}\n"
                text += f"📌 {status}\n\n"
                text += "─" * 40 + "\n\n"

            except:
                continue

        return text

    except Exception as e:
        logging.error(f"API Error: {e}")
        return "⚠️ Не удалось загрузить матчи. Попробуй позже."

# ==================== СТАДИОНЫ ====================
async def get_stadiums():
    text = "🏟 <b>Стадионы ЧМ-2026</b>\n\n"
    text += "🇨🇦 <b>Канада</b>\n• BMO Field (Торонто) — 43 000\n• BC Place (Ванкувер) — 52 500\n\n"
    text += "🇲🇽 <b>Мексика</b>\n• Estadio Azteca (Мехико) — 82 000\n• Estadio Akron (Гвадалахара) — 46 000\n• Estadio BBVA (Монтеррей) — 53 500\n\n"
    text += "🇺🇸 <b>США</b>\n• MetLife Stadium (Нью-Йорк) — 82 500\n• SoFi Stadium (Лос-Анджелес) — 70 000\n• AT&T Stadium (Даллас) — 80 000\n• Mercedes-Benz Stadium (Атланта) — 71 000\n• NRG Stadium (Хьюстон) — 72 000\n• Hard Rock Stadium (Майами) — 65 000\n• Lumen Field (Сиэтл) — 69 000\n• Levi's Stadium (Сан-Франциско) — 68 500\n• Lincoln Financial Field (Филадельфия) — 69 000\n• GEHA Field at Arrowhead (Канзас-Сити) — 76 000\n• Gillette Stadium (Бостон) — 65 000\n\n"
    text += "Всего 16 стадионов."
    return text

# ==================== ХЕНДЛЕРЫ ====================
@dp.callback_query(F.data == "matches")
async def matches_handler(c: CallbackQuery):
    await c.answer()
    msg = await c.message.edit_text("⏳ Загружаем матчи...")
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
    msg = await c.message.edit_text("⏳ Загружаем...")
    text = "📅 <b>Ближайшие 3 дня</b>\n\n"
    for i in range(3):
        day_text = await get_matches_by_date(i)
        text += day_text
    await msg.edit_text(text[:4000], reply_markup=schedule_back_menu())

@dp.callback_query(F.data == "schedule_week")
async def schedule_week(c: CallbackQuery):
    await c.answer()
    msg = await c.message.edit_text("⏳ Загружаем...")
    text = "📅 <b>Расписание на неделю</b>\n\n"
    for i in range(7):
        day_text = await get_matches_by_date(i)
        text += day_text
    await msg.edit_text(text[:4000], reply_markup=schedule_back_menu())

@dp.callback_query(F.data == "groups")
async def groups_handler(c: CallbackQuery):
    await c.answer()
    await c.message.edit_text(
        "🏆 <b>Группы Чемпионата мира 2026</b>\n\nВыберите группу:",
        reply_markup=groups_menu()
    )

@dp.callback_query(F.data.startswith("group_"))
async def show_group(c: CallbackQuery):
    await c.answer()
    group_letter = c.data.split("_")[1]
    data = GROUPS_DATA.get(group_letter, {"teams": [], "standings": []})

    text = f"🏆 <b>Группа {group_letter}</b>\n\n"
    text += "<b>Состав группы:</b>\n"
    for team in data["teams"]:
        text += f"• {team}\n"

    if data["standings"]:
        text += "\n<b>Таблица группы:</b>\n"
        text += "┌────┬────────────────────┬────┬────┬────┬────┬───────┬────┐\n"
        text += "│ М  │ Команда            │ И  │ В  │ Н  │ П  │ Голы  │ О  │\n"
        text += "├────┼────────────────────┼────┼────┼────┼────┼───────┼────┤\n"
        for pos, team, p, w, d, l, goals, pts in data["standings"]:
            text += f"│ {pos:2} │ {team:<18} │ {p:2} │ {w:2} │ {d:2} │ {l:2} │ {goals:5} │ {pts:2} │\n"
        text += "└────┴────────────────────┴────┴────┴────┴────┴───────┴────┘\n"
    else:
        text += "\n📊 Таблица обновляется по ходу турнира."

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ К списку групп", callback_data="groups")],
        [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_main")]
    ])
    
    await c.message.edit_text(text, reply_markup=kb)

@dp.callback_query(F.data == "stadiums")
async def stadiums_handler(c: CallbackQuery):
    await c.answer()
    text = await get_stadiums()
    await c.message.edit_text(text, reply_markup=back_menu())

@dp.callback_query(F.data == "teams")
async def teams_handler(c: CallbackQuery):
    await c.answer()
    text = "🌍 <b>Все сборные на ЧМ-2026 (48 команд)</b>\n\n"
    for team in ALL_TEAMS if 'ALL_TEAMS' in globals() else []:  # если есть список
        text += f"• {team}\n"
    await c.message.edit_text(text, reply_markup=back_menu())

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
