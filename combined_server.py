import os
import threading
import asyncio
import uvicorn
import traceback
import sys

def run_bot():
    """Запускаем Discord бота в отдельном потоке"""
    try:
        print("=== DISCORD BOT STARTUP ===")
        
        # Проверяем переменные окружения
        bot_token = os.getenv('BOT_TOKEN')
        user_token = os.getenv('USER_TOKEN')
        guild_id = os.getenv('GUILD_ID')
        channel_id = os.getenv('CHANNEL_ID')
        
        print(f"BOT_TOKEN exists: {bool(bot_token)}")
        print(f"USER_TOKEN exists: {bool(user_token)}")
        print(f"GUILD_ID: {guild_id}")
        print(f"CHANNEL_ID: {channel_id}")
        
        if not bot_token:
            print("ERROR: BOT_TOKEN not found!")
            return
            
        if not user_token:
            print("ERROR: USER_TOKEN not found!")
            return
        
        # Импортируем Discord бота
        print("Importing Discord bot...")
        from task_bot import bot, BOT_TOKEN
        
        print("Setting up event loop...")
        asyncio.set_event_loop(asyncio.new_event_loop())
        
        print("Starting Discord bot...")
        bot.run(BOT_TOKEN)
        
    except Exception as e:
        print(f"Discord bot error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    print("=== COMBINED SERVER STARTING ===")
    
    # Запускаем Discord бота в фоновом потоке
    print("Starting Discord bot thread...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Даем боту время на запуск
    import time
    time.sleep(2)
    
    # Запускаем web сервер в основном потоке
    print("Starting web server...")
    import server
    app = server.api_app
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host='0.0.0.0', port=port)