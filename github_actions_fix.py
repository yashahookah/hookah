#!/usr/bin/env python3
"""
Исправление для работы в GitHub Actions
Создаёт сессию Telegram при первом запуске
"""

import os
import sys
from telethon import TelegramClient
from dotenv import load_dotenv

# В GitHub Actions переменные окружения берутся из secrets
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = 'telegram_summary_session'

if not API_ID or not API_HASH:
    print("❌ Ошибка: TELEGRAM_API_ID и TELEGRAM_API_HASH должны быть установлены")
    sys.exit(1)

async def create_session():
    """Создаёт сессию Telegram для GitHub Actions"""
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    
    try:
        await client.start()
        print("✅ Сессия успешно создана!")
        print("📁 Файл сессии:", f"{SESSION_NAME}.session")
        print("\n⚠️  ВАЖНО: Сохрани этот файл как секрет в GitHub или загрузи в репозиторий")
    except Exception as e:
        print(f"❌ Ошибка при создании сессии: {e}")
        sys.exit(1)
    finally:
        await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(create_session())
