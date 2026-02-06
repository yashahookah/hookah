# Telegram Analytics для кальянной индустрии

Автоматическая система аналитики Telegram каналов кальянной индустрии с ежедневными отчётами.

## 🚀 Быстрый старт

### 1. Создай репозиторий на GitHub

Перейди на https://github.com/new и создай новый репозиторий (можно приватный).

### 2. Загрузи файлы

```bash
cd /Users/bws

# Инициализируй git
git init

# Добавь все нужные файлы
git add telegram_*.py
git add telegram_summary_config.py
git add requirements_telegram.txt
git add .github/
git add .gitignore
git add README.md

# Создай коммит
git commit -m "Initial commit: Telegram analytics system"

# Добавь remote (замени на свой репозиторий)
git remote add origin https://github.com/ТВОЙ_USERNAME/telegram-hookah-analytics.git

# Загрузи на GitHub
git branch -M main
git push -u origin main
```

### 3. Настрой секреты в GitHub

1. Перейди в репозиторий → **Settings** → **Secrets and variables** → **Actions**
2. Нажми **New repository secret**
3. Добавь два секрета:

   **TELEGRAM_API_ID**: `34210053`
   
   **TELEGRAM_API_HASH**: `a529084ee35b02689e70054dee553c40`

### 4. Первый запуск (настройка сессии)

1. Перейди в **Actions** → **Setup Telegram Session**
2. Нажми **Run workflow** → **Run workflow**
3. Дождись завершения
4. Скачай артефакт `telegram-session` (файл `telegram_summary_session.session`)
5. Загрузи этот файл обратно в репозиторий (или сохрани как секрет)

### 5. Запуск аналитики

После настройки сессии:

- **Автоматически**: каждый день в 10:30 МСК
- **Вручную**: Actions → Daily Telegram Analytics → Run workflow

## 📊 Что делает система

- Собирает посты из 10 Telegram каналов кальянной индустрии
- Анализирует новинки, мероприятия, цены
- Отслеживает упоминания Adalya и Tangiers
- Формирует красивый аналитический отчёт
- Отправляет на **@Analytic_Hookah**

## 📁 Структура файлов

- `telegram_daily_summary_complete.py` - основной скрипт
- `telegram_summary_config.py` - конфигурация каналов
- `telegram_*.py` - модули анализа
- `.github/workflows/` - GitHub Actions workflows

## 🔧 Настройка

Все настройки в `telegram_summary_config.py`:
- Список каналов
- Получатель отчётов
- Время запуска

## 📝 Логи

Логи выполнения доступны в **Actions** → выбери запуск → посмотри логи.

## ⚠️ Важно

- Сессия Telegram должна быть настроена один раз
- GitHub Actions имеет лимит 2000 минут/месяц (бесплатно)
- Один запуск занимает ~2-5 минут
