import asyncio, json, os, logging
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import aiosqlite

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN', '').strip()
DB_PATH = os.getenv('DB_PATH', 'my_life_rpg.sqlite3')
STORY_PATH = Path('stories/chapter_01.json')
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('my-life-rpg')
dp = Dispatcher()
bot = None

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY, name TEXT NOT NULL, gender TEXT NOT NULL,
            node TEXT NOT NULL DEFAULT 'start', money INTEGER NOT NULL DEFAULT 100,
            energy INTEGER NOT NULL DEFAULT 100, health INTEGER NOT NULL DEFAULT 100)''')
        await db.commit()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📖 Continue Story', callback_data='continue')],
        [InlineKeyboardButton(text='👤 Character', callback_data='character'), InlineKeyboardButton(text='📊 Status', callback_data='status')]
    ])

async def get_player(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute('SELECT name,gender,node,money,energy,health FROM players WHERE user_id=?', (user_id,))
        return await cur.fetchone()

async def show_node(target, user_id, node_id=None):
    player = await get_player(user_id)
    if not player:
        return
    current = node_id or player[2]
    story = json.loads(STORY_PATH.read_text(encoding='utf-8'))
    node = story['nodes'].get(current)
    if not node:
        node = story['nodes']['start']
        current = 'start'
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE players SET node=? WHERE user_id=?', (current, user_id))
        await db.commit()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=choice['text'], callback_data='choice:'+choice['next'])]
        for choice in node.get('choices', [])
    ] or [[InlineKeyboardButton(text='🏠 Menu', callback_data='menu')]])
    text = f"*{node['title']}*\n\n{node['text']}"
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb, parse_mode='Markdown')
        await target.answer()
    else:
        await target.answer(text, reply_markup=kb, parse_mode='Markdown')

@dp.message(CommandStart())
async def start(message: Message):
    player = await get_player(message.from_user.id)
    if player:
        await message.answer(f"Welcome back, {player[0]}! 🎮", reply_markup=main_menu())
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='♂ Male', callback_data='gender:Male'), InlineKeyboardButton(text='♀ Female', callback_data='gender:Female')]])
    await message.answer('🎮 *MY LIFE RPG*\n\nChoose your main character:', reply_markup=kb, parse_mode='Markdown')

@dp.callback_query(F.data.startswith('gender:'))
async def gender_pick(call: CallbackQuery):
    gender = call.data.split(':',1)[1]
    await call.message.edit_text(f'You selected {gender}. Now send your character name.')
    await call.answer()
    dp.workflow_data.setdefault('pending_names', {})[call.from_user.id] = gender

@dp.message(F.text)
async def name_input(message: Message):
    pending = dp.workflow_data.setdefault('pending_names', {})
    gender = pending.pop(message.from_user.id, None)
    if not gender:
        return
    name = message.text.strip()[:24]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT OR REPLACE INTO players(user_id,name,gender,node) VALUES(?,?,? ,?)', (message.from_user.id,name,gender,'start'))
        await db.commit()
    await message.answer(f'✨ Welcome, {name}! Your adventure begins now.', reply_markup=main_menu())

@dp.callback_query(F.data == 'continue')
async def continue_story(call: CallbackQuery):
    await show_node(call, call.from_user.id)

@dp.callback_query(F.data.startswith('choice:'))
async def choose(call: CallbackQuery):
    await show_node(call, call.from_user.id, call.data.split(':',1)[1])

@dp.callback_query(F.data == 'menu')
async def menu(call: CallbackQuery):
    await call.message.edit_text('MY LIFE RPG Menu', reply_markup=main_menu())
    await call.answer()

@dp.callback_query(F.data == 'character')
async def character(call: CallbackQuery):
    p = await get_player(call.from_user.id)
    await call.message.edit_text(f'👤 *{p[0]}*\nGender: {p[1]}', reply_markup=main_menu(), parse_mode='Markdown')
    await call.answer()

@dp.callback_query(F.data == 'status')
async def status(call: CallbackQuery):
    p = await get_player(call.from_user.id)
    await call.message.edit_text(f'📊 *{p[0]} Status*\n💰 Money: ${p[3]}\n⚡ Energy: {p[4]}\n❤️ Health: {p[5]}', reply_markup=main_menu(), parse_mode='Markdown')
    await call.answer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot
    await init_db()
    if TOKEN:
        bot = Bot(TOKEN)
        asyncio.create_task(dp.start_polling(bot))
        log.info('Telegram polling started')
    else:
        log.warning('BOT_TOKEN missing; web health endpoint is active but bot is not running')
    yield
    if bot:
        await bot.session.close()

app = FastAPI(title='MY LIFE RPG', lifespan=lifespan)

@app.get('/')
async def home():
    return {'app':'MY LIFE RPG','status':'online','telegram_bot':'running' if bot else 'BOT_TOKEN not configured'}

@app.get('/health')
async def health():
    return {'status':'ok'}
