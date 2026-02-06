# 💾 Резервное копирование проекта Telegram Analytics

## 📋 Статус проекта

**Дата последнего обновления:** 06.02.2026  
**Репозиторий:** https://github.com/yashahookah/hookah.git  
**Ветка:** main

## ✅ Все изменения закоммичены

Последние коммиты:
- `1b33eee` - Fix brand and product detection issues
- `a4b7dab` - Add report template documentation and fix duplicate header
- `fddb518` - Improve report formatting: make it more readable, narrative style like longread
- `a07ecbc` - Complete brand integration: add all 76+ brands to learning system
- `80e7586` - Add brands from historical analysis

## 📁 Ключевые файлы проекта

### Основные скрипты:
- `telegram_daily_summary_complete.py` - Главный скрипт для ежедневной аналитики
- `telegram_analytics_engine.py` - Движок аналитики и форматирования отчётов
- `telegram_trends_analyzer.py` - Анализатор трендов и брендов
- `telegram_brand_tracker.py` - Трекер упоминаний брендов (Adalya, Tangiers)
- `telegram_digest_builder.py` - Построитель дайджеста постов
- `telegram_learning_system.py` - Система обучения на основе данных
- `telegram_summary_config.py` - Конфигурация каналов и настроек

### Конфигурация:
- `.github/workflows/daily-summary.yml` - GitHub Actions workflow для ежедневного запуска
- `.github/workflows/setup-session.yml` - Workflow для настройки сессии
- `requirements_telegram.txt` - Зависимости Python
- `.env` - Переменные окружения (API_ID, API_HASH) - **НЕ коммитится в git**

### Документация:
- `REPORT_TEMPLATE_STRUCTURE.md` - Структура шаблона отчёта
- `report_template_example.py` - Примеры шаблонов
- `test_report_formatting.py` - Тестовый скрипт для проверки форматирования
- `README.md` - Основная документация
- Множество других MD файлов с инструкциями

### Данные (сохраняются автоматически):
- `telegram_summary_session.session` - Сессия Telegram (коммитится в git)
- `knowledge_base.json` - База знаний о рынке
- `brand_mentions.json` - Упоминания брендов
- `analytics_data.json` - Аналитические данные
- `trending_topics.json` - История трендов
- `summaries/` - Папка с сохранёнными отчётами

## 🚀 Как загрузить изменения в GitHub

```bash
cd /Users/bws
git push
```

Если запросит авторизацию, используй Personal Access Token с правами `repo` и `workflow`.

## 🔐 Важные секреты (хранятся в GitHub Secrets)

В GitHub репозитории должны быть настроены секреты:
- `TELEGRAM_API_ID` - API ID из https://my.telegram.org
- `TELEGRAM_API_HASH` - API Hash из https://my.telegram.org

## 📊 Что делает проект

1. **Ежедневная аналитика** - собирает данные из 12 Telegram каналов кальянной индустрии
2. **Анализ трендов** - отслеживает бренды, продукты, вкусы, события
3. **Отслеживание брендов** - специальный фокус на Adalya и Tangiers
4. **Система обучения** - накапливает знания о рынке, ценах, брендах
5. **Красивые отчёты** - формирует читабельные аналитические отчёты в стиле лонгрида
6. **Автоматическая отправка** - отправляет отчёты в @Analytic_Hookah каждый день в 10:30 МСК

## 🎯 Отслеживаемые каналы

1. @adalya_live - Adalya Live
2. @fedotovgroup - Fedotov Group
3. @mthook - MT Hook
4. @hookah4russian - Hookah 4 Russian
5. @Knexpert - KN Expert
6. @savinovsays - Savinov Says
7. @mveche - MVeche
8. @hookahtrade1 - HOOKAHTRADE
9. @Big_Smoke_Crew - Big Smoke Crew
10. @smoky_trip - Smoky Trip

Отключены:
- @ivankalyanbot - Иван Кальян
- @itsimplehookah - ЭТО просто КАЛЬЯН

## 🏷️ Отслеживаемые бренды (76+)

### Российские бренды табака:
Adalya, Darkside, Musthave, Duft, Blackburn, Burn, Satyr, Element, Holster, HIT, Hookain, Sebero, Karma, Spectrum, Overdose, Jent, NUR, Sarma, Edelveis, Nano Smoke, Big Maks, Bonche, Chabacco, **Troffimov's**, Werkbund, Antagonist, Bezdna, Big Smoke, Doha

### Международные бренды:
Tangiers, Original By Tangiers (OBT), Serbetli, Al Fakher, Afzal, Nakhla, Starbuzz, Fumari, Azure, Social Smoke, Zomo, Trifecta, Ugly, Eternal Smoke, Haze, Hydro, Lavoo, Mazaya, Nirvana, Pure

### Бренды кальянов и аксессуаров:
Alpha Hookah, Amy Deluxe, Amira, B2 Hookah, DSH Hookah, Kaloud, MIG, Moze, Oduman, Regal Hookah, Shishabucks, Starbuzz Hookah, Union Hookah, Wookah, Aeon, Mason, Hookah John, Hoob, Cosmobowl

## 🔧 Как восстановить проект

1. **Клонировать репозиторий:**
   ```bash
   git clone https://github.com/yashahookah/hookah.git
   cd hookah
   ```

2. **Установить зависимости:**
   ```bash
   pip install -r requirements_telegram.txt
   ```

3. **Настроить переменные окружения:**
   ```bash
   cp .env.example .env
   # Отредактировать .env и добавить TELEGRAM_API_ID и TELEGRAM_API_HASH
   ```

4. **Настроить сессию Telegram:**
   ```bash
   python3 setup_telegram_session.py
   # Или использовать существующую сессию из репозитория
   ```

5. **Проверить работу:**
   ```bash
   python3 telegram_daily_summary_complete.py --test
   ```

6. **Настроить GitHub Actions:**
   - Убедиться, что секреты `TELEGRAM_API_ID` и `TELEGRAM_API_HASH` настроены
   - Проверить, что файл `telegram_summary_session.session` загружен в репозиторий
   - Workflow запускается автоматически каждый день в 10:30 МСК

## 📝 Последние улучшения

1. ✅ Исправлена детекция брендов - исключены слова из названий каналов
2. ✅ Добавлен бренд Troffimov's и варианты
3. ✅ Исправлена детекция продуктов - исключены общие категории
4. ✅ Улучшено форматирование отчётов - стиль лонгрида
5. ✅ Добавлена документация по структуре шаблона отчёта
6. ✅ Создан тестовый скрипт для проверки форматирования

## ⚠️ Важно помнить

- Файл `.env` с API credentials **НЕ коммитится** в git
- Сессия `telegram_summary_session.session` **коммитится** в git для GitHub Actions
- Все данные сохраняются в JSON файлах локально
- GitHub Actions использует секреты из Settings → Secrets

## 🔗 Полезные ссылки

- Репозиторий: https://github.com/yashahookah/hookah
- Telegram API: https://my.telegram.org
- GitHub Actions: https://github.com/yashahookah/hookah/actions

---

**Проект полностью сохранён и готов к работе!** 🎉
