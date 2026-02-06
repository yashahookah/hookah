"""
Конфигурация для ежедневной сводки по Telegram каналам
"""

# Настройки каналов
CHANNELS = {
    'adalya_live': {
        'username': '@adalya_live',
        'name': 'Adalya Live',
        'enabled': True,
        'category': 'brand_official',  # Официальный бренд
        'priority': 'high'
    },
    'fedotovgroup': {
        'username': '@fedotovgroup',
        'name': 'Fedotov Group',
        'enabled': True,
        'category': 'business',
        'priority': 'high'
    },
    'mthook': {
        'username': '@mthook',
        'name': 'MT Hook',
        'enabled': True,
        'category': 'community',
        'priority': 'medium'
    },
    'hookah4russian': {
        'username': '@hookah4russian',
        'name': 'Hookah 4 Russian',
        'enabled': True,
        'category': 'community',
        'priority': 'medium'
    },
    'knexpert': {
        'username': '@Knexpert',
        'name': 'KN Expert',
        'enabled': True,
        'category': 'expert',
        'priority': 'high'
    },
    'savinovsays': {
        'username': '@savinovsays',
        'name': 'Savinov Says',
        'enabled': True,
        'category': 'personal',
        'priority': 'medium'
    },
    'mveche': {
        'username': '@mveche',
        'name': 'MVeche',
        'enabled': True,
        'category': 'community',
        'priority': 'medium'
    },
    # Дополнительные кальянные каналы
    'hookahtrade': {
        'username': '@hookahtrade1',
        'name': 'HOOKAHTRADE',
        'enabled': True,
        'category': 'retail',
        'priority': 'medium'
    },
    'itsimplehookah': {
        'username': '@itsimplehookah',
        'name': 'ЭТО просто КАЛЬЯН',
        'enabled': False,  # Отключен по запросу
        'category': 'community',
        'priority': 'low'
    },
    'ivankalyan': {
        'username': '@ivankalyanbot',
        'name': 'Иван Кальян',
        'enabled': False,  # Отключен по запросу
        'category': 'retail',
        'priority': 'low'
    },
    'big_smoke_crew': {
        'username': '@Big_Smoke_Crew',
        'name': 'Big Smoke Crew',
        'enabled': True,
        'category': 'community',
        'priority': 'medium'
    },
    'smoky_trip': {
        'username': '@smoky_trip',
        'name': 'Smoky Trip',
        'enabled': True,
        'category': 'community',
        'priority': 'medium'
    }
}

# Настройки времени
SCHEDULE_TIME = {
    'hour': 10,
    'minute': 30,
    'timezone': 'Europe/Moscow'  # МСК
}

# Настройки получателя сводки
SUMMARY_RECIPIENT = {
    'type': 'user',
    # Куда отправлять аналитику (аккаунт/канал @Analytic_Hookah)
    'username': '@Analytic_Hookah',
    'chat_id': None
}

# Настройки сводки
SUMMARY_SETTINGS = {
    'max_messages_per_channel': 20,  # Максимум сообщений на канал
    'include_media_info': True,  # Показывать информацию о медиа
    'include_views': True,  # Показывать количество просмотров
    'include_comments': True,  # Включать комментарии
    'max_comments_per_post': 5,  # Максимум комментариев на пост
    'include_trends_analysis': True,  # Анализ трендов
    'date_format': '%d.%m.%Y',  # Формат даты
    'time_format': '%H:%M',  # Формат времени
    'save_to_file': True,  # Сохранять сводки в файл для обучения
    'learning_enabled': True,  # Включить систему обучения
}
