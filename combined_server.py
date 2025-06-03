import os
import threading
import asyncio
import uvicorn
from task_bot import bot, BOT_TOKEN
import server

def run_bot():
    """Запускаем Discord бота в отдельном потоке"""
    asyncio.set_event_loop(asyncio.new_event_loop())
    bot.run(BOT_TOKEN)

if __name__ == '__main__':
    # Запускаем Discord бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем web сервер в основном потоке
    app = server.api_app
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host='0.0.0.0', port=port)
