import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from groq import Groq
import httpx
from aiohttp import web

# ВСТАВЛЕННЫЕ КЛЮЧИ
TELEGRAM_BOT_TOKEN = "8712807627:AAGX6o0zYnfFPSERcLsBsFJVFELPhpQZX-c"
GROQ_API_KEY = "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"

# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
groq_client = Groq(api_key=GROQ_API_KEY, http_client=httpx.Client())
chat_histories = {}

# --- Часть для работы на Render (веб-сервер) ---
async def handle(request):
    return web.Response(text="Бот работает!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()

# --- Логика бота ---
@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    await message.answer(f"Привет! Я твой ИИ-помощник. Спрашивай что угодно!")
    chat_histories[message.chat.id] = []

@dp.message()
async def handle_message(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in chat_histories: chat_histories[chat_id] = []
    chat_histories[chat_id].append({"role": "user", "content": message.text})
    try:
        response = groq_client.chat.completions.create(
            messages=chat_histories[chat_id],
            model="llama-3.1-8b-instant",
            temperature=0.7
        )
        ai_res = response.choices[0].message.content
        chat_histories[chat_id].append({"role": "assistant", "content": ai_res})
        await message.answer(ai_res)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

async def main():
    # Запускаем веб-сервер и бота одновременно
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
