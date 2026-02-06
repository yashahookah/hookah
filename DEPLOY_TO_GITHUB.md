# 🚀 Развёртывание в GitHub репозиторий

## Инструкция для загрузки в https://github.com/yashahookah/hookah.git

### Шаг 1: Измени remote репозитория

Выполни в терминале:

```bash
cd /Users/bws

# Удали старый remote
git remote remove origin

# Добавь правильный remote
git remote add origin https://github.com/yashahookah/hookah.git

# Проверь
git remote -v
```

### Шаг 2: Добавь все необходимые файлы

```bash
cd /Users/bws

# Добавь все файлы Telegram аналитики
git add telegram_daily_summary_complete.py
git add telegram_summary_config.py
git add telegram_trends_analyzer.py
git add telegram_learning_system.py
git add telegram_analytics_engine.py
git add telegram_brand_tracker.py
git add telegram_digest_builder.py
git add requirements_telegram.txt
git add .github/workflows/*.yml
git add .gitignore
git add README.md
git add GITHUB_QUICK_START.md
git add github_actions_fix.py

# Проверь что добавилось
git status
```

### Шаг 3: Создай коммит

```bash
git commit -m "Add Telegram analytics system with GitHub Actions"
```

### Шаг 4: Загрузи в GitHub

```bash
git branch -M main
git push -u origin main
```

Если будет запрошен пароль, используй **Personal Access Token** (не пароль от GitHub).

### Шаг 5: Настрой секреты в GitHub

1. Перейди в репозиторий: https://github.com/yashahookah/hookah
2. **Settings** → **Secrets and variables** → **Actions**
3. Нажми **New repository secret**
4. Добавь два секрета:

   **TELEGRAM_API_ID**: `34210053`
   
   **TELEGRAM_API_HASH**: `a529084ee35b02689e70054dee553c40`

### Шаг 6: Первый запуск (настройка сессии)

1. Перейди в **Actions** в репозитории
2. Выбери workflow **Setup Telegram Session**
3. Нажми **Run workflow** → **Run workflow**
4. Дождись завершения
5. Скачай артефакт `telegram-session`
6. Распакуй и загрузи файл `telegram_summary_session.session` в репозиторий:

```bash
# Распакуй архив
unzip telegram-session.zip

# Добавь файл сессии
git add telegram_summary_session.session
git commit -m "Add Telegram session file"
git push
```

### Шаг 7: Проверь работу

1. **Actions** → **Daily Telegram Analytics** → **Run workflow**
2. Дождись завершения
3. Проверь, что отчёт пришёл на **@Analytic_Hookah**

## ✅ Готово!

Теперь аналитика будет запускаться **автоматически каждый день в 10:30 МСК**.

## 📝 Если нужен Personal Access Token

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. **Generate new token (classic)**
3. Выбери scope: `repo` (полный доступ к репозиториям)
4. Скопируй токен и используй его вместо пароля при `git push`
