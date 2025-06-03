import os
import threading
import asyncio
import uvicorn
import traceback
import sys
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

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

def run_web():
    """Запускаем web сервер"""
    try:
        print("=== WEB SERVER STARTUP ===")
        
        # Импортируем server
        print("Importing server...")
        import server
        
        # ТЕСТИРУЕМ TASKQUEUE
        print("=== TESTING TASKQUEUE ===")
        try:
            from util._queue import taskqueue
            print(f"TaskQueue imported successfully!")
            print(f"TaskQueue concur_size: {taskqueue.concur_size()}")
            print(f"TaskQueue wait_size: {taskqueue.wait_size()}")
            
            # Тестируем добавление задачи
            print("Testing TaskQueue.put()...")
            def test_function(*args, **kwargs):
                print(f"TEST TASK EXECUTED: args={args}, kwargs={kwargs}")
                return "test_result"
            
            taskqueue.put("test_trigger", test_function, "test_arg", test_kwarg="test_value")
            print("Test task added to queue successfully!")
            
        except Exception as e:
            print(f"TaskQueue error: {e}")
            traceback.print_exc()
        
        # Проверяем импорт discord.generate
        print("=== TESTING DISCORD.GENERATE ===")
        try:
            from lib.api.discord import generate
            print("discord.generate imported successfully!")
        except Exception as e:
            print(f"discord.generate import error: {e}")
            traceback.print_exc()
        
        app = server.api_app
        port = int(os.environ.get("PORT", 8080))
        
        print(f"Starting web server on port {port}...")
        uvicorn.run(app, host='0.0.0.0', port=port)
        
    except Exception as e:
        print(f"Web server error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    print("=== COMBINED SERVER STARTING ===")
    
    # Показываем все переменные окружения (кроме токенов)
    env_vars = dict(os.environ)
    safe_vars = {k: ('***' if 'TOKEN' in k else v) for k, v in env_vars.items() 
                 if k in ['BOT_TOKEN', 'USER_TOKEN', 'GUILD_ID', 'CHANNEL_ID', 'DRAW_VERSION', 'PORT']}
    print(f"Environment variables: {safe_vars}")
    
    # Запускаем Discord бота в фоновом потоке
    print("Starting Discord bot thread...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    # bot_thread.start()
    
    # Даем боту время на запуск
    print("Waiting 2 seconds for Discord bot...")
    time.sleep(2)
    
    # Запускаем web сервер в основном потоке
    print("Starting web server...")
    run_web()