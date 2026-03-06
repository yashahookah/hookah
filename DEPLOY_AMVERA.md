# Деплой Expo POS на Amvera Cloud

Пошаговая инструкция по развёртыванию приложения на [Amvera Cloud](https://cloud.amvera.ru/).

---

## 1. Подготовка репозитория

Убедитесь, что в корне репозитория есть:

- `Dockerfile` — уже есть, собирает приложение из `expo_pos/`
- `amvera.yml` — конфигурация Amvera (создан в корне)
- `expo_pos/` — папка с приложением

---

## 2. Создание приложения в Amvera

1. Зайдите на [cloud.amvera.ru](https://cloud.amvera.ru/) и авторизуйтесь.
2. Нажмите **«Создать проект»**.
3. Выберите тип сервиса **«Приложение»**.
4. Укажите название (например, `expo-pos`) и тарифный план.
5. Нажмите **«Далее»**.

---

## 3. Подключение репозитория

### Вариант А: GitHub (рекомендуется)

1. В разделе **«Загрузка данных»** выберите **«Подключить GitHub»**.
2. Авторизуйте Amvera в GitHub (OAuth).
3. Выберите репозиторий `yashahookah/hookah`.
4. Укажите ветку `main` (или `master`).

### Вариант Б: Репозиторий Amvera

1. Amvera создаст пустой git-репозиторий.
2. Склонируйте его:
   ```bash
   git clone https://git.amvera.ru/<username>/<service-slug>
   cd <service-slug>
   ```
3. Скопируйте в папку:
   - `expo_pos/` (вся папка)
   - `Dockerfile`
   - `amvera.yml`
4. Закоммитьте и запушьте:
   ```bash
   git add .
   git commit -m "Add Expo POS"
   git push origin main
   ```

---

## 4. Переменные окружения

В настройках приложения добавьте переменную:

| Имя     | Значение           | Описание                          |
|---------|--------------------|-----------------------------------|
| `DB_PATH` | `/data/expo_pos.db` | Путь к SQLite (в постоянном хранилище) |

Без этой переменной база будет в рабочей директории и может теряться при перезапуске.

---

## 5. Конфигурация (amvera.yml)

Файл `amvera.yml` в корне репозитория уже настроен:

- **persistenceMount: /data** — постоянное хранилище для SQLite
- **containerPort: 80** — порт приложения
- **dockerfile: Dockerfile** — путь к Dockerfile

---

## 6. Деплой

После `git push` в ветку `main` (или `master`):

1. Amvera автоматически соберёт образ по `Dockerfile`.
2. Запустит контейнер.
3. Примонтирует `/data` как постоянное хранилище.

Сборка и запуск занимают обычно 2–5 минут.

---

## 7. Проверка

1. В личном кабинете откройте приложение.
2. Перейдите по ссылке (например, `https://expo-pos-xxx.amvera.ru`).
3. Должен открыться интерфейс Expo POS.

---

## Обновление приложения

```bash
git add .
git commit -m "Update Expo POS"
git push origin main
```

Amvera пересоберёт и перезапустит приложение автоматически.

---

## Возможные проблемы

| Проблема | Решение |
|----------|---------|
| База сбрасывается при перезапуске | Проверьте `DB_PATH=/data/expo_pos.db` и `persistenceMount: /data` |
| Ошибка сборки | Проверьте логи сборки в личном кабинете |
| 502 Bad Gateway | Дождитесь завершения запуска (1–2 мин) или проверьте, что uvicorn слушает порт 80 |

---

## Полезные ссылки

- [Документация Amvera](https://docs.amvera.ru/)
- [Быстрый старт](https://docs.amvera.ru/applications/quick-start.html)
- [Docker-конфигурация](https://docs.amvera.ru/applications/configuration/docker.html)
- [Подключение GitHub](https://docs.amvera.ru/applications/git/webhooks.html)
- Поддержка: support@amvera.ru
