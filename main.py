import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from groq import Groq
import httpx
from aiohttp import web

# КЛЮЧИ (Уже вставлены для вас)
TELEGRAM_BOT_TOKEN = "8712807627:AAGX6o0zYnfFPSERcLsBsFJVFELPhpQZX-c"
GROQ_API_KEY = "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"

# Инициализация
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
groq_client = Groq(api_key=GROQ_API_KEY, http_client=httpx.Client())
chat_histories = {}

# Веб-сервер для Render
async def handle(request): return web.Response(text="Бот онлайн!")
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    chat_histories[message.chat.id] = []
    await message.answer("Привет! Я твой ИИ-помощник. Я обновил свои мозги и готов к работе! Спрашивай что угодно.")

@dp.message()
async def handle_msg(message: types.Message):
    cid = message.chat.id
    if cid not in chat_histories: chat_histories[cid] = []
    
    chat_histories[cid].append({"role": "user", "content": message.text})
    if len(chat_histories[cid]) > 10: chat_histories[cid] = chat_histories[cid][-10:]

    try:
        # ИСПОЛЬЗУЕМ НОВУЮ МОДЕЛЬ (llama-3.1-8b-instant)
        response = groq_client.chat.completions.create(
            messages=chat_histories[cid],
            model="llama-3.1-8b-instant",
            temperature=0.7
        )
        answer = response.choices[0].message.content
        chat_histories[cid].append({"role": "assistant", "content": answer})
        await message.answer(answer)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

async def main():
    print("Запуск...")
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
