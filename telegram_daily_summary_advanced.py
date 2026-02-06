#!/usr/bin/env python3
"""
Ежедневная сводка по Telegram каналам (улучшенная версия)
Запускается в 10:30 МСК каждый день
"""

import asyncio
import schedule
import time
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import Channel
import os
from dotenv import load_dotenv
from telegram_summary_config import (
    CHANNELS, 
    SCHEDULE_TIME, 
    SUMMARY_RECIPIENT,
    SUMMARY_SETTINGS
)

load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = 'telegram_summary_session'

# Импорт timezone для работы с МСК
from datetime import timezone as tz
import pytz

MSK_TZ = pytz.timezone('Europe/Moscow')


async def get_today_messages(client, channel_username, channel_name):
    """
    Получает сообщения из канала за сегодня (до текущего момента)
    """
    messages = []
    try:
        today_start = datetime.now(MSK_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
        now = datetime.now(MSK_TZ)
        
        async for message in client.iter_messages(channel_username, offset_date=now):
            msg_date = message.date.astimezone(MSK_TZ)
            
            # Останавливаемся, если сообщение старше начала дня
            if msg_date < today_start:
                break
            
            # Собираем только сообщения за сегодня
            if msg_date.date() == today_start.date():
                msg_data = {
                    'text': message.text or message.message or '',
                    'date': msg_date,
                    'time_str': msg_date.strftime(SUMMARY_SETTINGS['time_format']),
                    'has_media': bool(message.media),
                    'views': getattr(message, 'views', 0),
                    'id': message.id
                }
                
                # Добавляем информацию о медиа, если есть
                if message.media and SUMMARY_SETTINGS['include_media_info']:
                    media_type = type(message.media).__name__
                    msg_data['media_type'] = media_type.replace('MessageMedia', '')
                
                messages.append(msg_data)
        
        # Сортируем по времени (от старых к новым)
        messages.sort(key=lambda x: x['date'])
        
    except Exception as e:
        print(f"Ошибка при получении сообщений из {channel_username}: {e}")
        return []
    
    return messages


def format_channel_summary(channel_name, messages):
    """
    Форматирует сводку по одному каналу
    """
    if not messages:
        return f"📭 **{channel_name}**\nНет новых сообщений за сегодня\n"
    
    summary = f"📢 **{channel_name}** ({len(messages)} сообщений)\n\n"
    
    # Ограничиваем количество сообщений
    display_messages = messages[-SUMMARY_SETTINGS['max_messages_per_channel']:]
    
    for msg in display_messages:
        time_str = msg['time_str']
        text_preview = msg['text'][:150] + '...' if len(msg['text']) > 150 else msg['text']
        
        # Формируем строку с метаданными
        meta_parts = []
        
        if SUMMARY_SETTINGS['include_views'] and msg['views'] > 0:
            meta_parts.append(f"👁 {msg['views']}")
        
        if msg['has_media']:
            media_indicator = f"📎 {msg.get('media_type', 'Media')}"
            meta_parts.append(media_indicator)
        
        meta_str = f" ({', '.join(meta_parts)})" if meta_parts else ""
        
        summary += f"🕐 {time_str}{meta_str}\n"
        
        if text_preview:
            summary += f"{text_preview}\n\n"
        else:
            summary += "[Медиа без текста]\n\n"
    
    # Если сообщений больше, чем показываем
    if len(messages) > SUMMARY_SETTINGS['max_messages_per_channel']:
        hidden_count = len(messages) - SUMMARY_SETTINGS['max_messages_per_channel']
        summary += f"... и еще {hidden_count} сообщений\n"
    
    return summary


async def create_and_send_summary():
    """
    Создает и отправляет ежедневную сводку
    """
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        await client.start()
        
        now = datetime.now(MSK_TZ)
        date_str = now.strftime(SUMMARY_SETTINGS['date_format'])
        time_str = now.strftime('%H:%M')
        
        # Заголовок сводки
        full_summary = f"📊 **Ежедневная сводка за {date_str}**\n"
        full_summary += f"⏰ Время формирования: {time_str} МСК\n"
        full_summary += "=" * 50 + "\n\n"
        
        # Собираем сообщения из всех активных каналов
        total_messages = 0
        for channel_key, channel_config in CHANNELS.items():
            if not channel_config.get('enabled', True):
                continue
                
            print(f"Обработка канала {channel_config['name']} ({channel_config['username']})...")
            messages = await get_today_messages(
                client, 
                channel_config['username'], 
                channel_config['name']
            )
            
            channel_summary = format_channel_summary(channel_config['name'], messages)
            full_summary += channel_summary + "\n"
            
            total_messages += len(messages)
        
        # Итоговая статистика
        full_summary += "=" * 50 + "\n"
        full_summary += f"📈 Всего сообщений за день: {total_messages}\n"
        
        # Отправляем сводку
        recipient = SUMMARY_RECIPIENT.get('chat_id') or SUMMARY_RECIPIENT['username']
        await client.send_message(recipient, full_summary, parse_mode='markdown')
        print(f"✅ Сводка успешно отправлена! Всего сообщений: {total_messages}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании сводки: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()


def run_summary():
    """
    Запускает создание сводки (синхронная обертка для schedule)
    """
    asyncio.run(create_and_send_summary())


def main():
    """
    Основная функция - настраивает расписание и запускает цикл
    """
    # Настраиваем расписание
    schedule_time = f"{SCHEDULE_TIME['hour']:02d}:{SCHEDULE_TIME['minute']:02d}"
    schedule.every().day.at(schedule_time).do(run_summary)
    
    print(f"✅ Планировщик настроен. Сводка будет отправляться каждый день в {schedule_time} МСК")
    print("Ожидание времени запуска...")
    
    # Запускаем цикл планировщика
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверяем каждую минуту


if __name__ == '__main__':
    # Для тестирования можно запустить сразу
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("Тестовый запуск...")
        asyncio.run(create_and_send_summary())
    else:
        main()
