# 🚀 Быстрый старт: GitHub Actions

## Пошаговая инструкция

### Шаг 1: Создай репозиторий

1. Перейди на https://github.com/new
2. Назови репозиторий (например: `telegram-hookah-analytics`)
3. Выбери **Private** (рекомендуется)
4. Нажми **Create repository**

### Шаг 2: Загрузи файлы

Выполни в терминале:

```bash
cd /Users/bws

# Инициализируй git
git init

# Добавь файлы
git add telegram_daily_summary_complete.py
git add telegram_summary_config.py
git add telegram_trends_analyzer.py
git add telegram_learning_system.py
git add telegram_analytics_engine.py
git add telegram_brand_tracker.py
git add telegram_digest_builder.py
git add requirements_telegram.txt
git add .github/
git add .gitignore
git add README.md

# Коммит
git commit -m "Initial commit"

# Добавь remote (ЗАМЕНИ ТВОЙ_USERNAME на свой GitHub username)
git remote add origin https://github.com/ТВОЙ_USERNAME/telegram-hookah-analytics.git

# Загрузи
git branch -M main
git push -u origin main
```

### Шаг 3: Настрой секреты

1. В репозитории на GitHub: **Settings** → **Secrets and variables** → **Actions**
2. Нажми **New repository secret**
3. Добавь:

   **Name**: `TELEGRAM_API_ID`  
   **Secret**: `34210053`

4. Ещё раз **New repository secret**:

   **Name**: `TELEGRAM_API_HASH`  
   **Secret**: `a529084ee35b02689e70054dee553c40`

### Шаг 4: Первый запуск (настройка сессии)

1. Перейди в **Actions** в репозитории
2. Выбери workflow **Setup Telegram Session**
3. Нажми **Run workflow** → **Run workflow**
4. Дождись завершения (может занять 1-2 минуты)
5. В разделе **Artifacts** скачай `telegram-session`
6. Распакуй и загрузи файл `telegram_summary_session.session` обратно в репозиторий:

```bash
# Распакуй архив
unzip telegram-session.zip

# Добавь файл сессии в репозиторий
git add telegram_summary_session.session
git commit -m "Add Telegram session"
git push
```

**Альтернатива**: Можно сохранить содержимое файла сессии как секрет `TELEGRAM_SESSION` и восстанавливать его в workflow.

### Шаг 5: Проверь работу

1. Перейди в **Actions** → **Daily Telegram Analytics**
2. Нажми **Run workflow** → **Run workflow**
3. Дождись завершения
4. Проверь, что отчёт пришёл на **@Analytic_Hookah**

## ✅ Готово!

Теперь аналитика будет запускаться **автоматически каждый день в 10:30 МСК**.

## 🔍 Проверка

- **Логи**: Actions → выбери запуск → смотри логи
- **Артефакты**: Сводки сохраняются как артефакты (30 дней)
- **Ручной запуск**: В любой момент можно запустить через **Run workflow**

## ⚠️ Если что-то не работает

1. Проверь секреты в Settings → Secrets
2. Посмотри логи в Actions
3. Убедись, что сессия Telegram настроена
4. Проверь, что все файлы загружены в репозиторий
