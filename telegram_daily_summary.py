#!/usr/bin/env python3
"""
Ежедневная сводка по Telegram каналам
Запускается в 10:30 МСК каждый день
"""

import asyncio
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient, events
from telethon.tl.types import Channel
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = 'telegram_summary_session'

# Каналы для отслеживания (замените на ваши)
CHANNELS = [
    '@channel1',  # Замените на реальные каналы
    '@channel2',
]

# Куда отправлять сводку
SUMMARY_RECIPIENT = '@your_username'  # Ваш Telegram username или ID

# Временная зона МСК (UTC+3)
MSK_TZ = timezone(timedelta(hours=3))


async def get_channel_messages(client, channel_username, date):
    """
    Получает сообщения из канала за указанную дату
    """
    messages = []
    try:
        async for message in client.iter_messages(channel_username, offset_date=date):
            # Проверяем, что сообщение за нужную дату
            msg_date = message.date.astimezone(MSK_TZ)
            if msg_date.date() == date.date():
                messages.append({
                    'text': message.text or message.message or '',
                    'date': msg_date.strftime('%H:%M'),
                    'has_media': bool(message.media),
                    'views': getattr(message, 'views', 0)
                })
            elif msg_date.date() < date.date():
                break
    except Exception as e:
        print(f"Ошибка при получении сообщений из {channel_username}: {e}")
    
    return messages


def format_summary(channel_name, messages):
    """
    Форматирует сводку по каналу
    """
    if not messages:
        return f"📭 **{channel_name}**\nНет новых сообщений за сегодня\n"
    
    summary = f"📢 **{channel_name}** ({len(messages)} сообщений)\n\n"
    
    for msg in messages[:10]:  # Показываем до 10 последних сообщений
        time_str = msg['date']
        text_preview = msg['text'][:100] + '...' if len(msg['text']) > 100 else msg['text']
        media_indicator = '📎' if msg['has_media'] else ''
        views_str = f" 👁 {msg['views']}" if msg['views'] > 0 else ""
        
        summary += f"🕐 {time_str}{views_str} {media_indicator}\n"
        summary += f"{text_preview}\n\n"
    
    if len(messages) > 10:
        summary += f"... и еще {len(messages) - 10} сообщений\n"
    
    return summary


async def send_daily_summary():
    """
    Формирует и отправляет ежедневную сводку
    """
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        await client.start()
        
        today = datetime.now(MSK_TZ)
        summary_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        
        full_summary = f"📊 **Ежедневная сводка за {today.strftime('%d.%m.%Y')}**\n"
        full_summary += f"⏰ Время формирования: {today.strftime('%H:%M МСК')}\n"
        full_summary += "=" * 50 + "\n\n"
        
        # Собираем сообщения из всех каналов
        for channel in CHANNELS:
            print(f"Обработка канала {channel}...")
            messages = await get_channel_messages(client, channel, summary_date)
            channel_summary = format_summary(channel, messages)
            full_summary += channel_summary + "\n"
        
        # Отправляем сводку
        await client.send_message(SUMMARY_RECIPIENT, full_summary, parse_mode='markdown')
        print("Сводка успешно отправлена!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await client.disconnect()


if __name__ == '__main__':
    asyncio.run(send_daily_summary())
