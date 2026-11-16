import os
import json
import asyncio
from pathlib import Path
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Update
from aiogram.filters import CommandStart, Command

TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_URL = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-this-secret")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")
if not PUBLIC_URL:
    raise RuntimeError("RENDER_EXTERNAL_URL is required on Render")

bot = Bot(TOKEN)
dp = Dispatcher()
DATA_FILE = Path("players.json")

def load_players():
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_players(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

players = load_players()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 ဇာတ်လမ်းစမယ်", callback_data="begin")],
        [InlineKeyboardButton(text="👤 ကိုယ့်အခြေအနေ", callback_data="status")]
    ])

@dp.message(CommandStart())
async def start(message: Message):
    uid = str(message.from_user.id)
    players.setdefault(uid, {"name": "", "gender": "", "chapter": 1, "scene": "intro"})
    save_players(players)
    await message.answer(
        "🎮 MY LIFE RPG မှ ကြိုဆိုပါတယ်။\n\nကိုယ့်ဇာတ်ကောင်ရဲ့ လိင်ကို ရွေးချယ်ပါ။",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👨 Male", callback_data="male"),
             InlineKeyboardButton(text="👩 Female", callback_data="female")]
        ])
    )

@dp.callback_query(F.data.in_({"male", "female"}))
async def choose_gender(call: CallbackQuery):
    uid = str(call.from_user.id)
    players.setdefault(uid, {})
    players[uid]["gender"] = call.data
    save_players(players)
    await call.message.answer("ဇာတ်ကောင်နာမည်ကို ရိုက်ထည့်ပေးပါ။")
    await call.answer()

@dp.message(F.text & ~F.text.startswith("/"))
async def set_name(message: Message):
    uid = str(message.from_user.id)
    if uid in players and players[uid].get("gender") and not players[uid].get("name"):
        players[uid]["name"] = message.text.strip()[:30]
        save_players(players)
        await message.answer(f"ကြိုဆိုပါတယ် {players[uid]['name']}။ MY LIFE RPG Chapter 1 ကို စတင်နိုင်ပါပြီ။", reply_markup=main_menu())

@dp.callback_query(F.data == "begin")
async def begin(call: CallbackQuery):
    await call.message.answer(
        "📍 Chapter 1 — နေ့သစ်တစ်ခု\n\nမနက်ခင်း နေရောင်ခြည်က ပြတင်းပေါက်ကနေ ဝင်လာတယ်။ ဒီနေ့ဟာ မင်းရဲ့ဘဝသစ်ရဲ့ ပထမဆုံးနေ့ပဲ။\n\nဘာလုပ်မလဲ?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 အိမ်ထဲမှာနေမယ်", callback_data="home")],
            [InlineKeyboardButton(text="🚶 အပြင်ထွက်မယ်", callback_data="outside")]
        ])
    )
    await call.answer()

@dp.callback_query(F.data.in_({"home", "outside"}))
async def choice(call: CallbackQuery):
    uid = str(call.from_user.id)
    if uid in players:
        players[uid]["scene"] = call.data
        save_players(players)
    if call.data == "home":
        msg = "အိမ်ထဲမှာပဲ နေပြီး ပတ်ဝန်းကျင်ကို လေ့လာလိုက်တယ်။ နောက်ထပ်အပိုင်းတွေကို အဆင့်ဆင့် ဖွင့်ပေးသွားမယ်။"
    else:
        msg = "အပြင်ထွက်လိုက်တော့ လမ်းထိပ်မှာ လူသစ်တစ်ယောက်နဲ့ ဆုံတယ်။ နောက်ထပ်အပိုင်းတွေကို အဆင့်ဆင့် ဖွင့်ပေးသွားမယ်။"
    await call.message.answer(msg, reply_markup=main_menu())
    await call.answer()

@dp.callback_query(F.data == "status")
async def status(call: CallbackQuery):
    p = players.get(str(call.from_user.id), {})
    await call.message.answer(
        f"👤 အမည်: {p.get('name') or 'မသတ်မှတ်ရသေး'}\n"
        f"⚧ Gender: {p.get('gender') or 'မရွေးရသေး'}\n"
        f"📖 Chapter: {p.get('chapter', 1)}"
    )
    await call.answer()

async def health(request):
    return web.Response(text="MY LIFE RPG is running")

async def telegram_webhook(request):
    if request.match_info.get("secret") != WEBHOOK_SECRET:
        raise web.HTTPForbidden()
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return web.Response(text="ok")

async def on_startup(app):
    await bot.set_webhook(f"{PUBLIC_URL}/webhook/{WEBHOOK_SECRET}", drop_pending_updates=True)

async def on_cleanup(app):
    await bot.delete_webhook()
    await bot.session.close()

app = web.Application()
app.router.add_get("/", health)
app.router.add_post("/webhook/{secret}", telegram_webhook)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
