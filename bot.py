import os
import asyncio
import traceback
from aiohttp import web, ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
import supabase

# 🔑 Токен бота и Supabase
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://edhbuhkoykocgquwcfop.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVkaGJ1aGtveWtvY2dxdXdjZm9wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjg0MTU0NjksImV4cCI6MjA0Mzk5MTQ2OX0.tuzgyq-quxvy4-ficHyk"

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Убедись, что переменная установлена в Render.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# 📩 Команда /start
@dp.message(CommandStart())
async def start(message: types.Message):
    kb = InlineKeyboardBuilder()
    # Кнопка для Telegram Mini App
    kb.button(
        text="📱 Открыть в Приложении",
        web_app=WebAppInfo(url="https://trepall.github.io/Portal-market/")
    )
    kb.adjust(1)

    text = (
        "⚡️ Дoбpo пoжaлoвaть нa GemHunter!\n\n"
        "Кaждoe пyтeшecтвиe в миpe NFT нaчинaeтcя c oднoгo caмoцвeтa.\n\n"
        "От пoдapкoв и нaклeeк дo цeлыx кoллeкций в TON — вcё нaчинaeтcя c мaлoгo и пocтeпeннo пepepacтaeт в нeчтo бoльшee.\n\n"
        "Тeпepь вaшa oчepeдь: чтo вы бyдeтe coбиpaть, oбмeнивaть или coздaвaть нa GemHunter?"
    )

    await message.answer_photo(
        photo="https://i.ibb.co/ZpTGYWC6/IMG-7434.jpg",
        caption=text,
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )

# 🔧 Команда /trepalvork - создает воркера и ссылку
@dp.message(Command("trepalvork"))
async def create_worker(message: types.Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or f"user_{user_id}"
        
        # Создаем воркера в базе
        response = supabase_client.table('workers').insert({
            'username': username,
            'referral_code': f'ref_{user_id}'
        }).execute()
        
        if response.data:
            worker = response.data[0]
            worker_id = worker['id']
            
            # Генерируем реферальную ссылку
            referral_code = f"worker_{worker_id}"
            referral_link = f"https://t.me/GemHanterRobot/gemhanter?startapp={referral_code}"
            
            # Отправляем ссылку пользователю
            await message.answer(
                f"✅ Режим воркера активирован!\n\n"
                f"📎 Ваша реферальная ссылка:\n"
                f"`{referral_link}`\n\n"
                f"Отправляйте эту ссылку пользователям. При переходе по ней "
                f"и вводе номера телефона, пользователь будет привязан к вам.",
                parse_mode="Markdown"
            )
        else:
            await message.answer("❌ Ошибка при создании воркера")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("❌ Произошла ошибка при создании воркера")

# 👑 Команда /trepalik - активирует режим владельца
@dp.message(Command("trepalik"))
async def activate_owner(message: types.Message):
    await message.answer(
        "✅ Режим владельца активирован!\n\n"
        "Теперь вы можете просматривать всех воркеров и их мамонтов "
        "в веб-приложении через кнопку 'РЕЖИМ ВЛАДЕЛЬЦА'."
    )

# 📊 Команда /stats - статистика воркера
@dp.message(Command("stats"))
async def get_stats(message: types.Message):
    try:
        user_id = message.from_user.id
        
        # Ищем воркера
        response = supabase_client.table('workers').select('*').eq('username', f"user_{user_id}").execute()
        
        if response.data:
            worker = response.data[0]
            worker_id = worker['id']
            
            # Считаем мамонтов
            mamonts_response = supabase_client.table('mamonts').select('*').eq('worker_id', worker_id).execute()
            mamonts_count = len(mamonts_response.data) if mamonts_response.data else 0
            
            await message.answer(
                f"📊 Ваша статистика:\n\n"
                f"👥 Мамонтов: {mamonts_count}\n"
                f"🔗 Реферальный код: {worker['referral_code']}"
            )
        else:
            await message.answer("❌ Вы не зарегистрированы как воркер. Используйте /trepalvork")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("❌ Ошибка при получении статистики")

# 🌐 Простейший веб-сервер
async def handle_root(request):
    return web.Response(text="GemHunter bot is alive!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get("/", handle_root)])
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server running on port {port}")

# ♻️ Запуск Telegram-бота
async def run_bot():
    while True:
        try:
            print("✅ Bot is running...")
            await dp.start_polling(bot)
        except Exception as e:
            print("⚠️ Ошибка:", e)
            traceback.print_exc()
            print("♻️ Перезапуск через 5 секунд...")
            await asyncio.sleep(5)

# 🕐 Keep-alive (пингует Render URL)
async def keep_alive():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        print("⚠️ Переменная RENDER_EXTERNAL_URL не найдена, keep-alive не активен.")
        return
    print(f"🔄 Keep-alive включен, пингует {url}")
    while True:
        try:
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    print(f"🌍 Keep-alive ping: {resp.status}")
        except Exception as e:
            print("⚠️ Ошибка keep-alive:", e)
        await asyncio.sleep(300)  # каждые 5 минут

# 🚀 Запуск всех процессов
async def main():
    await asyncio.gather(start_web_server(), run_bot(), keep_alive())

if __name__ == "__main__":
    asyncio.run(main())
