#!/usr/bin/env python3
"""
Тестовый скрипт для проверки форматирования отчёта без подключения к Telegram
"""

from datetime import datetime, timedelta
from collections import Counter, defaultdict
import pytz

# Импортируем модули форматирования
from telegram_analytics_engine import AnalyticsEngine
from telegram_brand_tracker import BrandTracker
from telegram_digest_builder import DigestBuilder
from telegram_learning_system import LearningSystem
from telegram_trends_analyzer import TrendsAnalyzer

MSK_TZ = pytz.timezone('Europe/Moscow')

def create_mock_data():
    """Создаёт мок-данные для тестирования форматирования"""
    
    # Мок-данные для content_analysis
    content_analysis = {
        'total_messages': 15,
        'total_views': 45000,
        'avg_views_per_message': 3000,
        'media_ratio': 0.6,
        'channels_activity': {
            'Adalya Live': {
                'messages': 5,
                'views': 18000,
                'avg_views': 3600,
                'media_count': 3
            },
            'Fedotov Group': {
                'messages': 4,
                'views': 12000,
                'avg_views': 3000,
                'media_count': 2
            },
            'MT Hook': {
                'messages': 3,
                'views': 9000,
                'avg_views': 3000,
                'media_count': 2
            },
            'Hookah 4 Russian': {
                'messages': 3,
                'views': 6000,
                'avg_views': 2000,
                'media_count': 1
            }
        },
        'topics': Counter([
            'новинки', 'новинки', 'новинки',
            'мероприятия', 'мероприятия',
            'цены', 'цены',
            'обзоры', 'обзоры',
            'релизы'
        ])
    }
    
    # Мок-данные для sentiment_analysis
    sentiment_analysis = {
        'positive': 8,
        'neutral': 5,
        'negative': 2
    }
    
    # Мок-данные для insights
    insights = [
        {'type': 'activity', 'value': 'Adalya Live (5 постов)'},
        {'type': 'engagement', 'value': 'Adalya Live (3600 просмотров/пост)'},
        {'type': 'sentiment', 'value': 'Позитивный'}
    ]
    
    # Мок-данные для trends_data
    trends_data = {
        'top_brands': [
            ('Darkside', 8),
            ('Musthave', 5),
            ('Sebero', 4),
            ('Adalya', 3),
            ('Tangiers', 2),
            ('Jent', 2)
        ],
        'top_products': [
            ('табак', 12),
            ('кальян', 5),
            ('уголь', 3)
        ],
        'top_flavors': [
            ('клубника', 4),
            ('мята', 3),
            ('лимон', 2)
        ],
        'events': [
            {
                'text': '28 марта едем на Новоселье чего-то нового от BLACKBURN',
                'channel': 'KN Expert',
                'time': '10:00'
            },
            {
                'text': 'ХИТ ПАРАД самых любимых ароматов Евгения Федотова',
                'channel': 'KN Expert',
                'time': '14:30'
            }
        ],
        'business_updates': [
            {
                'text': 'Новые поставки табака Darkside в регионы',
                'channel': 'Fedotov Group',
                'time': '09:00'
            }
        ]
    }
    
    # Мок-данные для brand_mentions
    brand_mentions = {
        'adalya': [
            {
                'channel': 'Adalya Live',
                'time': '10:15',
                'context': 'Новая линейка Adalya Black теперь доступна в продаже'
            },
            {
                'channel': 'MT Hook',
                'time': '15:30',
                'context': 'Обзор вкусов Adalya для начинающих'
            }
        ],
        'tangiers': [
            {
                'channel': 'Hookah 4 Russian',
                'time': '12:00',
                'context': 'Original By Tangiers — лучший выбор для профи'
            }
        ]
    }
    
    # Мок-данные для messages_by_channel
    now = datetime.now(MSK_TZ)
    messages_by_channel = {
        'Adalya Live': [
            {
                'text': '🔥 Новая линейка Adalya Black уже в продаже! Цена от 1200₽ за 50г',
                'time_str': (now - timedelta(hours=2)).strftime('%H:%M'),
                'views': 5000,
                'channel': 'Adalya Live'
            },
            {
                'text': '📢 Мероприятие: презентация новых вкусов 15 марта в Москве',
                'time_str': (now - timedelta(hours=4)).strftime('%H:%M'),
                'views': 3000,
                'channel': 'Adalya Live'
            }
        ],
        'Fedotov Group': [
            {
                'text': 'Новинка от Darkside: вкус "Тропический рай" теперь доступен',
                'time_str': (now - timedelta(hours=1)).strftime('%H:%M'),
                'views': 4000,
                'channel': 'Fedotov Group'
            },
            {
                'text': 'Специальное предложение: кальян Hoob за 15000₽',
                'time_str': (now - timedelta(hours=3)).strftime('%H:%M'),
                'views': 2500,
                'channel': 'Fedotov Group'
            }
        ]
    }
    
    return {
        'content_analysis': content_analysis,
        'sentiment_analysis': sentiment_analysis,
        'insights': insights,
        'trends_data': trends_data,
        'brand_mentions': brand_mentions,
        'messages_by_channel': messages_by_channel
    }

def test_report_formatting():
    """Тестирует форматирование отчёта"""
    
    print("🧪 Тестирование форматирования отчёта...\n")
    
    # Создаём мок-данные
    mock_data = create_mock_data()
    
    # Инициализируем системы
    analytics_engine = AnalyticsEngine()
    brand_tracker = BrandTracker()
    digest_builder = DigestBuilder()
    learning_system = LearningSystem()
    
    # Формируем дату
    now = datetime.now(MSK_TZ)
    date_str = now.strftime('%d.%m.%Y')
    time_str = now.strftime('%H:%M')
    
    # Заголовок
    full_summary = f"# 📊 Аналитический отчёт за {date_str}\n\n"
    full_summary += f"_Сформировано в {time_str} МСК_\n\n"
    full_summary += "---\n\n"
    
    # Форматируем brand_mentions_summary
    brand_mentions_summary = brand_tracker.format_brand_mentions_summary(mock_data['brand_mentions'])
    
    # Форматируем аналитический отчёт
    analytics_report = analytics_engine.format_analytics_report(
        mock_data['content_analysis'],
        mock_data['sentiment_analysis'],
        mock_data['insights'],
        brand_mentions_summary,
        trends_data=mock_data['trends_data']
    )
    full_summary += analytics_report
    
    # Добавляем инсайты о рынке
    full_summary += "\n---\n\n"
    full_summary += "## 💡 Что мы знаем о рынке\n\n"
    market_insights = learning_system.get_market_insights()
    if market_insights:
        full_summary += market_insights + "\n"
    
    # Добавляем дайджест
    digest = digest_builder.build_digest(mock_data['messages_by_channel'])
    if digest:
        full_summary += "\n---\n\n"
        full_summary += digest
    
    # Итого
    total_messages = mock_data['content_analysis']['total_messages']
    channels_count = len(mock_data['messages_by_channel'])
    full_summary += "\n---\n\n"
    full_summary += f"**Итого:** проанализировано **{total_messages} сообщений** из **{channels_count} каналов** за {date_str}.\n"
    
    # Выводим результат
    print("=" * 80)
    print("📄 ТЕСТОВЫЙ ОТЧЁТ:")
    print("=" * 80)
    print(full_summary)
    print("=" * 80)
    
    # Сохраняем в файл
    test_file = f"test_report_{date_str.replace('.', '_')}.md"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(full_summary)
    
    print(f"\n✅ Отчёт сохранён в файл: {test_file}")
    print(f"📏 Длина отчёта: {len(full_summary)} символов")
    print(f"📝 Количество строк: {len(full_summary.split(chr(10)))}")
    
    return full_summary

if __name__ == "__main__":
    try:
        test_report_formatting()
        print("\n✅ Тест форматирования завершён успешно!")
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
