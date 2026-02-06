# 📋 Структура шаблона отчёта

## Порядок формирования отчёта

Отчёт формируется в файле `telegram_daily_summary_complete.py` в функции `create_and_send_summary()`.

### Последовательность сборки:

1. **Заголовок** → `telegram_daily_summary_complete.py` (строки 205-207)
2. **Что происходило сегодня** → `telegram_analytics_engine.py` → `format_analytics_report()` (строки 252-309)
3. **В цифрах** → `telegram_analytics_engine.py` → `format_analytics_report()` (строки 311-321)
4. **Кто и как писал** → `telegram_analytics_engine.py` → `format_analytics_report()` (строки 323-340)
5. **О чём говорили** → `telegram_analytics_engine.py` → `format_analytics_report()` (строки 342-349)
6. **Что в тренде** → `telegram_analytics_engine.py` → `format_analytics_report()` (строки 351-396)
7. **Настроение аудитории** → `telegram_analytics_engine.py` → `format_analytics_report()` (строки 398-411)
8. **Фокус: Adalya и Tangiers** → `telegram_brand_tracker.py` → `format_brand_mentions_summary()` (строки 185-227)
9. **Что конкретно писали блогеры** → `telegram_digest_builder.py` → `build_digest()` (строки 212-241)
10. **Что мы знаем о рынке** → `telegram_learning_system.py` → `get_market_insights()` (строки 155-186)
11. **Итого** → `telegram_daily_summary_complete.py` (строки 283-285)

---

## Детальная структура каждого раздела

### 1. Заголовок
**Файл:** `telegram_daily_summary_complete.py`  
**Строки:** 205-207

```python
full_summary = f"# 📊 Аналитический отчёт за {date_str}\n\n"
full_summary += f"_Сформировано в {time_str} МСК_\n\n"
full_summary += "---\n\n"
```

**Можно изменить:**
- Эмодзи в заголовке
- Формат даты
- Текст подзаголовка

---

### 2. Что происходило сегодня
**Файл:** `telegram_analytics_engine.py`  
**Функция:** `format_analytics_report()`  
**Строки:** 252-309

**Структура:**
```python
report_lines.append("## 📖 Что происходило сегодня\n\n")

# Если нет постов:
report_lines.append("Сегодня в отслеживаемых каналах было тихо...")

# Если есть посты:
story_parts = []
story_parts.append(f"За сегодня в кальянном инфополе появилось **{total_msgs} новых постов**...")
story_parts.append(f"Самым активным оказался канал **{channel_name}**.")
story_parts.append(f"В лентах чаще всего мелькали бренды: {brands_text}.")
story_parts.append(f"Общий настрой обсуждений — **{sentiment_text}**.")

report_lines.append(" ".join(story_parts) + "\n")
```

**Можно изменить:**
- Текст вступления
- Порядок предложений
- Формулировки

---

### 3. В цифрах
**Файл:** `telegram_analytics_engine.py`  
**Функция:** `format_analytics_report()`  
**Строки:** 311-321

**Структура:**
```python
report_lines.append("## 📊 В цифрах\n\n")

report_lines.append(
    f"Всего собрано **{total_msgs} постов**, которые набрали **{total_views:,} просмотров**. "
    f"В среднем каждый пост получил **{avg_views:.0f} просмотров**.\n\n"
)

if media_ratio > 0:
    report_lines.append(
        f"**{media_ratio:.0f}%** контента — это фото и видео, остальное — текстовые посты.\n"
    )
```

**Можно изменить:**
- Формулировки описания метрик
- Порядок показа информации

---

### 4. Кто и как писал
**Файл:** `telegram_analytics_engine.py`  
**Функция:** `format_analytics_report()`  
**Строки:** 323-340

**Структура:**
```python
report_lines.append("## 📱 Кто и как писал\n\n")

for idx, (channel, stats) in enumerate(sorted_channels, 1):
    media_info = f", из них {stats['media_count']} с фото/видео" if stats['media_count'] > 0 else ""
    line = (
        f"**{idx}. {channel}** опубликовал {stats['messages']} постов{media_info}. "
        f"Средняя вовлечённость — {stats['avg_views']:.0f} просмотров на пост.\n\n"
    )
    report_lines.append(line)
```

**Можно изменить:**
- Формат описания каналов
- Порядок информации (сначала просмотры, потом посты и т.д.)

---

### 5. О чём говорили
**Файл:** `telegram_analytics_engine.py`  
**Функция:** `format_analytics_report()`  
**Строки:** 342-349

**Структура:**
```python
report_lines.append("## 💬 О чём говорили\n\n")

topics_list = []
for topic, count in top_topics:
    topics_list.append(f"**{topic}** ({count} раз)")

report_lines.append("Основные темы дня: " + ", ".join(topics_list) + ".\n")
```

**Можно изменить:**
- Формат списка тем
- Количество показываемых тем

---

### 6. Что в тренде
**Файл:** `telegram_analytics_engine.py`  
**Функция:** `format_analytics_report()`  
**Строки:** 351-396

**Структура:**
```python
report_lines.append("## 🎯 Что в тренде\n\n")

# Бренды
if competitor_brands:
    top_brands_list = [f"**{b.title()}** ({c})" for b, c in competitor_brands[:5]]
    report_lines.append(f"**Бренды дня:** {', '.join(top_brands_list)}.\n\n")

# Продукты
if products:
    products_list = [f"**{p.title()}** ({c})" for p, c in products[:5]]
    report_lines.append(f"**Продукты:** {', '.join(products_list)}.\n\n")

# Вкусы
if flavors:
    flavors_list = [f"**{f.title()}** ({c})" for f, c in flavors[:5]]
    report_lines.append(f"**Вкусы:** {', '.join(flavors_list)}.\n\n")

# События
if events:
    report_lines.append("**События и мероприятия:**\n\n")
    for ev in events[:3]:
        ev_text = ev['text'][:120].strip()
        report_lines.append(f"• [{ev['channel']}] {ev_text}\n")

# Бизнес-новости
if business_updates:
    report_lines.append("**Бизнес-новости:**\n\n")
    for bu in business_updates[:3]:
        bu_text = bu['text'][:120].strip()
        report_lines.append(f"• [{bu['channel']}] {bu_text}\n")
```

**Можно изменить:**
- Формат списков (запятые, точки, списки)
- Количество показываемых элементов
- Формат описания событий

---

### 7. Настроение аудитории
**Файл:** `telegram_analytics_engine.py`  
**Функция:** `format_analytics_report()`  
**Строки:** 398-411

**Структура:**
```python
report_lines.append("## 😊 Настроение аудитории\n\n")

sentiment_parts = []
for sentiment, count in sentiment_analysis.items():
    if count > 0:
        pct = (count / total * 100) if total > 0 else 0
        label = {
            "positive": "позитивных",
            "negative": "негативных",
            "neutral": "нейтральных",
        }.get(sentiment, sentiment)
        sentiment_parts.append(f"**{pct:.0f}%** {label}")

report_lines.append("Тон обсуждений: " + ", ".join(sentiment_parts) + ".\n")
```

**Можно изменить:**
- Формулировки (позитивных, негативных и т.д.)
- Формат отображения процентов

---

### 8. Фокус: Adalya и Tangiers
**Файл:** `telegram_brand_tracker.py`  
**Функция:** `format_brand_mentions_summary()`  
**Строки:** 185-227

**Структура:**
```python
summary = "## 🎯 Фокус: Adalya и Tangiers\n\n"

# Adalya
if total_adalya > 0:
    summary += f"**Adalya** упоминалась **{total_adalya} раз** за сегодня.\n\n"
    
    if len(by_channel) == 1:
        summary += f"Все упоминания были в канале **{channel}**.\n\n"
    else:
        summary += f"Упоминания распределены по {len(by_channel)} каналам: "
        channels_list = [f"**{ch}** ({len(msgs)})" for ch, msgs in by_channel.items()]
        summary += ", ".join(channels_list) + ".\n\n"
    
    # Примеры упоминаний
    for mention in mentions_data['adalya'][:2]:
        context = mention['context'][:100].strip()
        summary += f"• [{mention['channel']}, {mention['time']}] {context}...\n\n"

# Аналогично для Tangiers
```

**Можно изменить:**
- Формат описания упоминаний
- Количество примеров
- Длину контекста

---

### 9. Что конкретно писали блогеры
**Файл:** `telegram_digest_builder.py`  
**Функция:** `build_digest()`  
**Строки:** 212-241

**Структура:**
```python
lines.append("## 📌 Что конкретно писали блогеры\n\n")

# Новинки
if novelties:
    lines.append(f"### 🆕 Новинки и релизы ({len(novelties)} постов)\n\n")
    for idx, item in enumerate(novelties_sorted[:8], 1):
        brand_part = f"**{item['brand']}** представил: " if item["brand"] else ""
        lines.append(f"{idx}. [{item['channel']}, {item['time']}] {brand_part}{text_snippet}\n\n")

# Мероприятия
if events:
    lines.append(f"### 🎪 Мероприятия и события ({len(events)} постов)\n\n")
    for idx, item in enumerate(events_sorted[:8], 1):
        lines.append(f"{idx}. [{item['channel']}, {item['time']}] {text_snippet}\n\n")

# Цены
if prices:
    lines.append(f"### 💰 Цены и предложения ({len(prices)} постов)\n\n")
    for idx, item in enumerate(prices_sorted[:8], 1):
        lines.append(f"{idx}. [{item['channel']}, {item['time']}] {brand_part}— {price_str}\n\n")
```

**Можно изменить:**
- Формат нумерации
- Количество показываемых постов
- Формат описания (канал, время, текст)

---

### 10. Что мы знаем о рынке
**Файл:** `telegram_learning_system.py`  
**Функция:** `get_market_insights()`  
**Строки:** 155-186

**Структура:**
```python
insights.append("## 💡 Что мы знаем о рынке\n\n")

# Цены
price_info = []
for label, keys in groups.items():
    price_info.append(f"**{label}** — обычно **~{median:.0f}₽** (от {min_price}₽ до {max_price}₽)")

if price_info:
    insights.append("**Цены на рынке:** " + ", ".join(price_info) + ".\n\n")

# Бренды
brands_list = [f"**{brand.title()}** ({data['mentions']})" for brand, data in sorted_brands]
insights.append("**Самые активные бренды:** " + ", ".join(brands_list) + ".\n\n")

# События
insights.append("**Ближайшие события:**\n\n")
for event in recent_events[:3]:
    insights.append(f"• [{event['channel']}] {event_text}\n")
```

**Можно изменить:**
- Формат описания цен
- Формат списка брендов
- Формат событий

---

### 11. Итого
**Файл:** `telegram_daily_summary_complete.py`  
**Строки:** 283-285

**Структура:**
```python
full_summary += "\n---\n\n"
full_summary += f"**Итого:** проанализировано **{total_messages} сообщений** из **{len(messages_by_channel)} каналов** за {date_str}.\n"
```

**Можно изменить:**
- Формат итоговой строки
- Добавить дополнительную информацию

---

## Как редактировать

### Вариант 1: Редактировать напрямую в файлах

1. Открой нужный файл (см. выше)
2. Найди нужную функцию
3. Измени текст форматирования
4. Сохрани и закоммить

### Вариант 2: Создать отдельный файл шаблона

Можно вынести все текстовые шаблоны в отдельный файл `report_templates.py` и импортировать оттуда.

---

## Примеры изменений

### Изменить заголовок:
**Файл:** `telegram_daily_summary_complete.py`, строки 205-207

```python
# Было:
full_summary = f"# 📊 Аналитический отчёт за {date_str}\n\n"

# Стало:
full_summary = f"# 🔥 Что творилось в кальянной индустрии {date_str}\n\n"
```

### Изменить формат метрик:
**Файл:** `telegram_analytics_engine.py`, строки 311-321

```python
# Было:
report_lines.append(f"Всего собрано **{total_msgs} постов**...")

# Стало:
report_lines.append(f"📱 За день появилось **{total_msgs} постов**...")
```

### Изменить формат брендов:
**Файл:** `telegram_analytics_engine.py`, строки 368-371

```python
# Было:
top_brands_list = [f"**{b.title()}** ({c})" for b, c in competitor_brands[:5]]
report_lines.append(f"**Бренды дня:** {', '.join(top_brands_list)}.\n\n")

# Стало:
top_brands_list = [f"{b.title()} — {c} упоминаний" for b, c in competitor_brands[:5]]
report_lines.append("**Топ брендов:**\n")
for brand in top_brands_list:
    report_lines.append(f"- {brand}\n")
report_lines.append("\n")
```

---

## Где что находится — краткая справка

| Раздел | Файл | Функция | Строки |
|--------|------|---------|--------|
| Заголовок | `telegram_daily_summary_complete.py` | `create_and_send_summary()` | 205-207 |
| Что происходило | `telegram_analytics_engine.py` | `format_analytics_report()` | 252-309 |
| В цифрах | `telegram_analytics_engine.py` | `format_analytics_report()` | 311-321 |
| Кто писал | `telegram_analytics_engine.py` | `format_analytics_report()` | 323-340 |
| О чём говорили | `telegram_analytics_engine.py` | `format_analytics_report()` | 342-349 |
| Что в тренде | `telegram_analytics_engine.py` | `format_analytics_report()` | 351-396 |
| Настроение | `telegram_analytics_engine.py` | `format_analytics_report()` | 398-411 |
| Фокус бренды | `telegram_brand_tracker.py` | `format_brand_mentions_summary()` | 185-227 |
| Дайджест постов | `telegram_digest_builder.py` | `build_digest()` | 212-241 |
| Инсайты рынка | `telegram_learning_system.py` | `get_market_insights()` | 155-186 |
| Итого | `telegram_daily_summary_complete.py` | `create_and_send_summary()` | 283-285 |

---

## Советы по редактированию

1. **Сохраняй структуру Markdown** — используй `##` для заголовков, `**` для жирного текста
2. **Не меняй переменные** — `{total_msgs}`, `{date_str}` и т.д. должны остаться
3. **Тестируй изменения** — запускай локально перед загрузкой в GitHub
4. **Сохраняй читаемость** — не делай слишком длинные строки

---

## Быстрый старт редактирования

1. Открой файл из таблицы выше
2. Найди нужную функцию
3. Измени текст между кавычками
4. Сохрани и закоммить:
   ```bash
   git add <файл>
   git commit -m "Update report template"
   git push
   ```
