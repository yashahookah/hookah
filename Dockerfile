# Dockerfile для деплоя Expo POS на Timeweb (проект в подпапке expo_pos)
FROM python:3.11-slim

WORKDIR /app

# Копируем только expo_pos
COPY expo_pos/ .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
