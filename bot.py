import os
import asyncio
import traceback
from aiohttp import web, ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
from supabase import create_client

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://edhbuhkoykocgquwcfop.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVkaGJ1aGtveWtvY2dxdXdjZm9wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjg0MTU0NjksImV4cCI6MjA0Mzk5MTQ2OX0.tuzgyq-quxvy4-ficHyk"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@dp.message(CommandStart())
async def start(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="📱 Открыть GemHunter",
        web_app=WebAppInfo(url="https://your-username.github.io/your-repo/")
    )
    await message.answer_photo(
        photo="https://i.ibb.co/ZpTGYWC6/IMG-7434.jpg",
        caption="⚡️ Добро пожаловать на GemHunter!",
        reply_markup=kb.as_markup()
    )

@dp.message(Command("trepalvork"))
async def create_worker(message: types.Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or f"user_{user_id}"
        
        # Создаем воркера в базе
        response = supabase.table('workers').insert({
            'username': username,
            'referral_code': f'ref_{user_id}'
        }).execute()
        
        if response.data:
            worker = response.data[0]
            referral_link = f"https://t.me/GemHanterRobot/gemhanter?startapp=worker_{worker['id']}"
            
            await message.answer(
                f"✅ Режим воркера активирован!\n\n"
                f"📎 Ваша ссылка:\n`{referral_link}`",
                parse_mode="Markdown"
            )
    except Exception as e:
        await message.answer("❌ Ошибка. Попробуйте позже.")

@dp.message(Command("trepalik"))
async def activate_owner(message: types.Message):
    await message.answer("✅ Режим владельца активирован!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", lambda request: web.Response(text="Bot is alive!"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

# 🕐 Keep-alive каждые 5 минут
async def keep_alive():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        print("⚠️ RENDER_EXTERNAL_URL не найден")
        return
    print(f"🔄 Keep-alive включен: {url}")
    while True:
        try:
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    print(f"🌍 Ping: {resp.status}")
        except Exception as e:
            print(f"⚠️ Keep-alive ошибка: {e}")
        await asyncio.sleep(300)  # 5 минут

# ♻️ Запуск бота с перезапуском
async def run_bot():
    while True:
        try:
            print("✅ Bot starting...")
            await dp.start_polling(bot)
        except Exception as e:
            print(f"⚠️ Bot error: {e}")
            await asyncio.sleep(5)

async def main():
    await asyncio.gather(web_server(), run_bot(), keep_alive())

if __name__ == "__main__":
    asyncio.run(main())
