# Деплой Expo POS на Timeweb

Есть два варианта: **App Platform** (проще) и **VPS** (надёжнее для SQLite).

---

## Вариант 1: App Platform (быстрый деплой)

Подходит для теста. **Важно:** файловая система может быть эфемерной — данные SQLite могут сбрасываться при перезапуске/редиплое. Для выставки на 1–2 дня обычно хватает.

### Шаг 1. Репозиторий на GitHub

1. Создайте репозиторий на GitHub (например, `expo-pos`).
2. Залейте код из папки `expo_pos`:

```bash
cd /Users/bws/expo_pos
git init
git add .
git commit -m "Expo POS"
git branch -M main
git remote add origin https://github.com/ВАШ_НИК/expo-pos.git
git push -u origin main
```

### Шаг 2. Создание приложения в Timeweb

1. Зайдите на [timeweb.cloud](https://timeweb.cloud) и войдите в аккаунт.
2. Перейдите: **Сервисы** → **App Platform** → **Создать приложение**.
3. Или сразу: [timeweb.cloud/my/apps/create](https://timeweb.cloud/my/apps/create).
4. Выберите **Backend** → **FastAPI**.

### Шаг 3. Подключение репозитория

1. Нажмите **«Добавить аккаунт»** и привяжите GitHub (если ещё не привязан).
2. Укажите репозиторий с Expo POS.
3. Убедитесь, что:
   - **Корневая папка** — корень репозитория (или путь к папке `expo_pos`, если весь проект в одном репо).
   - **Файл приложения** — `main.py`.
   - **Команда запуска** — `uvicorn main:app --host 0.0.0.0` (или `--port 80` при необходимости).

### Шаг 4. Запуск деплоя

1. Нажмите **«Запустить деплой»**.
2. Дождитесь сборки (обычно 5–10 минут).
3. Получите публичную ссылку вида `https://ваш-проект-xxxxx.timeweb.cloud`.

### Шаг 5. Проверка

- Киоск: `https://ваш-проект-xxxxx.timeweb.cloud/kiosk`
- Продавец: `https://ваш-проект-xxxxx.timeweb.cloud/seller`
- Сборка: `https://ваш-проект-xxxxx.timeweb.cloud/picking`

---

## Вариант 2: VPS (постоянное хранение данных)

Подходит для продакшена: SQLite хранится на диске, данные не теряются при перезапуске.

### Шаг 1. Создание VPS

1. [timeweb.cloud](https://timeweb.cloud) → **Сервисы** → **VDS/VPS** → **Создать сервер**.
2. Выберите **Ubuntu 22.04** (или 24.04).
3. Тариф: **Cloud MSK 15** (477 ₽/мес) или выше.
4. Регион: Москва (или ближайший).
5. Создайте сервер и дождитесь письма с IP и паролем (или SSH-ключом).

### Шаг 2. Подключение по SSH

```bash
ssh root@ВАШ_IP
# или
ssh ubuntu@ВАШ_IP
```

### Шаг 3. Установка зависимостей

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx git
```

### Шаг 4. Загрузка проекта

**Вариант А — из GitHub:**

```bash
cd /var/www
sudo git clone https://github.com/ВАШ_НИК/expo-pos.git
sudo mv expo-pos expo_pos
cd expo_pos
```

**Вариант Б — через SCP с вашего компьютера:**

```bash
# На вашем компьютере:
scp -r /Users/bws/expo_pos root@ВАШ_IP:/var/www/
```

### Шаг 5. Настройка Python и приложения

```bash
cd /var/www/expo_pos
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 6. Проверка запуска

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Откройте в браузере `http://ВАШ_IP:8000/kiosk`. Если всё работает — остановите (Ctrl+C).

### Шаг 7. Systemd-сервис (автозапуск)

```bash
sudo nano /etc/systemd/system/expo-pos.service
```

Вставьте:

```ini
[Unit]
Description=Expo POS FastAPI
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/expo_pos
Environment="PATH=/var/www/expo_pos/venv/bin"
ExecStart=/var/www/expo_pos/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Сохраните (Ctrl+O, Enter, Ctrl+X).

```bash
sudo systemctl daemon-reload
sudo systemctl enable expo-pos
sudo systemctl start expo-pos
sudo systemctl status expo-pos
```

### Шаг 8. Nginx (прокси на порт 80)

```bash
sudo nano /etc/nginx/sites-available/expo-pos
```

Вставьте (замените `ВАШ_ДОМЕН` на IP или домен):

```nginx
server {
    listen 80;
    server_name ВАШ_ДОМЕН;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/expo-pos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Шаг 9. Файрвол (если включён)

```bash
sudo ufw allow 80
sudo ufw allow 22
sudo ufw enable
```

### Шаг 10. Готово

Откройте в браузере:

- `http://ВАШ_IP/kiosk`
- `http://ВАШ_IP/seller`
- `http://ВАШ_IP/picking`

---

## Переменные окружения (опционально)

Для VPS или App Platform можно задать:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DB_PATH` | Путь к файлу SQLite | `/var/www/expo_pos/data/expo_pos.db` |

На VPS в systemd-сервис добавьте:

```ini
Environment="DB_PATH=/var/www/expo_pos/data/expo_pos.db"
```

И создайте папку:

```bash
mkdir -p /var/www/expo_pos/data
```

---

## Полезные ссылки

- [Timeweb App Platform — создание приложения](https://timeweb.cloud/my/apps/create)
- [Деплой FastAPI в App Platform](https://timeweb.cloud/docs/apps/deploying-backend-applications/fastapi)
- [Установка FastAPI на VDS](https://timeweb.cloud/tutorials/python/ustanovka-sajta-na-fastapi-na-vds)
