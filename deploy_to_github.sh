#!/bin/bash

# Скрипт для загрузки Telegram аналитики в GitHub репозиторий
# https://github.com/yashahookah/hookah.git

set -e

echo "🚀 Развёртывание в GitHub репозиторий..."
echo ""

cd /Users/bws

# Шаг 1: Изменяем remote
echo "📡 Настройка remote репозитория..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/yashahookah/hookah.git
echo "✅ Remote настроен: https://github.com/yashahookah/hookah.git"
echo ""

# Шаг 2: Добавляем все файлы
echo "📦 Добавление файлов..."
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
echo "✅ Файлы добавлены"
echo ""

# Шаг 3: Проверяем статус
echo "📊 Статус репозитория:"
git status --short
echo ""

# Шаг 4: Коммит
echo "💾 Создание коммита..."
git commit -m "Add Telegram analytics system with GitHub Actions" || echo "⚠️  Нет изменений для коммита"
echo ""

# Шаг 5: Push
echo "⬆️  Загрузка в GitHub..."
echo "⚠️  Если запросит авторизацию, используй Personal Access Token (не пароль)"
echo ""
git branch -M main
git push -u origin main

echo ""
echo "✅ Готово! Файлы загружены в https://github.com/yashahookah/hookah"
echo ""
echo "📝 Следующие шаги:"
echo "1. Перейди в репозиторий: https://github.com/yashahookah/hookah"
echo "2. Settings → Secrets → Actions → добавь TELEGRAM_API_ID и TELEGRAM_API_HASH"
echo "3. Actions → Setup Telegram Session → Run workflow"
echo "4. После настройки сессии: Actions → Daily Telegram Analytics → Run workflow"
echo ""
echo "📖 Подробная инструкция в файле DEPLOY_TO_GITHUB.md"
