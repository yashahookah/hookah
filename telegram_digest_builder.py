"""
Формирует человекочитаемый дайджест по конкретным постам за период.
Фокус: новинки, события, цены/офферы, что и кто писал.
"""

import re
from typing import Dict, List, Any


class DigestBuilder:
    def __init__(self) -> None:
        # Ключевые слова для выявления типов постов
        self.novelty_keywords = [
            "новинка",
            "новый вкус",
            "новый аромат",
            "новая линейка",
            "новый табак",
            "новый продукт",
            "дроп",
            "релиз",
            "запуск",
        ]
        self.event_keywords = [
            "фестиваль",
            "фест",
            "мероприятие",
            "ивент",
            "выставка",
            "прогрев",
            "fest",
            "event",
            "meetup",
        ]

        # Бренды, которые будем пытаться подсветить в тексте
        self.brand_keywords = [
            # Основные российские бренды табака
            "adalya", "адалия", "адалья",
            "darkside", "дарксайд", "ds",
            "musthave", "мастхейв", "мх",
            "duft", "дуфт",
            "blackburn", "блэкберн",
            "burn", "берн",
            "satyr", "сатир",
            "element", "элемент",
            "holster", "холстер",
            "hit", "h.i.t", "h i t", "хит",
            "hookain", "хукаин",
            "sebero", "себеро",
            "karma", "карма",
            "spectrum", "спектрум",
            "overdose", "overdoze", "overdoz", "овердоз",
            "overdose hookah", "overdoze hookah", "overdoz hookah",
            
            # Международные бренды табака
            "tangiers", "тангирс", "тангиерс",
            "original by tangiers", "obt",
            "serbetli", "сербетли",
            "al fakher", "аль факхер", "af",
            "afzal", "афзал",
            "nakhla", "нахла",
            "starbuzz", "старбазз",
            "fumari", "фумари",
            "azure", "азур",
            "social smoke", "сошиал смоук",
            "zomo", "зомо",
            "trifecta", "трифекта",
            "ugly", "агли",
            "chaos", "хаос",
            "eternal smoke", "этернал смоук",
            "haze", "хейз",
            "hydro", "хайдро",
            "lavoo", "лаву",
            "mazaya", "мазая",
            "nirvana", "нирвана",
            "pure", "пьюр",
            
            # Бренды кальянов и аксессуаров
            "alpha hookah", "альфа кальян",
            "amy deluxe", "ами делюкс",
            "amira", "амира",
            "b2 hookah", "б2 кальян",
            "dsh hookah", "dsh кальян", "дш кальян",
            "kaloud", "калуд",
            "mig", "миг", "mig hookah", "mig кальян",
            "moze", "мозе", "moze hookah", "moze кальян",
            "oduman", "одуман",
            "regal hookah", "ригал кальян",
            "shishabucks", "шишабакс",
            "starbuzz hookah", "starbuzz hookahs", "starbuzz stems",
            "union hookah", "union", "юнион кальян",
            "wookah", "вука",
            "aeon", "эон", "aeon hookah",
            "mason", "мейсон", "mason hookah",
            "hookah john", "хука джон",
            "kaloud lotus", "lotus", "лотос",
            "provost", "провост",
            "stratus", "стратус",
            "samsaris", "самсарис",
            "vitria", "витрия",
            "ignis", "игнис",
            "hmd", "хмд",
            "heat management", "heat management device",
        ]

        # Паттерны для поиска цен
        self.price_patterns = [
            r"(\d+)\s*₽",
            r"(\d+)\s*руб",
            r"(\d+)\s*rub",
        ]

        # Базовые продуктовые ключи
        self.product_keywords = [
            "табак",
            "кальян",
            "уголь",
            "чаша",
            "аксессуар",
            "микс",
            "вкус",
        ]

        # Месяца по‑русски, чтобы вытащить дату мероприятия
        self.month_words = [
            "январ",
            "феврал",
            "март",
            "апрел",
            "мая",
            "июн",
            "июл",
            "август",
            "сентябр",
            "октябр",
            "ноябр",
            "декабр",
        ]

    def _find_brand(self, text_lower: str) -> str:
        # Сначала ищем точные совпадения известных брендов
        for brand in self.brand_keywords:
            # Используем границы слов для точного поиска
            pattern = r'\b' + re.escape(brand) + r'\b'
            if re.search(pattern, text_lower):
                # Нормализуем название бренда
                if brand == 'h.i.t' or brand == 'h i t':
                    return 'HIT'
                return brand.title()
        
        # Дополнительный поиск по паттернам (аббревиатуры, заглавные буквы)
        # Ищем аббревиатуры типа HIT, OBT, DS и т.д.
        abbrev_pattern = r'\b([A-Z]{2,4})\b'
        matches = re.finditer(abbrev_pattern, text_lower)
        for match in matches:
            abbrev = match.group(1).upper()
            # Исключаем общие аббревиатуры
            exclude = ['THE', 'AND', 'FOR', 'WITH', 'THIS', 'THAT', 'FROM', 'INTO', 'OVER']
            if abbrev not in exclude and len(abbrev) >= 2:
                # Проверяем контекст - если рядом есть слова про табак/кальян, это может быть бренд
                context_start = max(0, match.start() - 20)
                context_end = min(len(text_lower), match.end() + 20)
                context = text_lower[context_start:context_end]
                brand_context_words = ['табак', 'кальян', 'вкус', 'аромат', 'бренд', 'tobacco', 'hookah', 'flavor', 'brand']
                if any(word in context for word in brand_context_words):
                    return abbrev
        
        return ""

    def _find_prices(self, text: str) -> List[int]:
        prices: List[int] = []
        for pattern in self.price_patterns:
            for m in re.findall(pattern, text.lower()):
                try:
                    value = int(m)
                    prices.append(value)
                except ValueError:
                    continue
        return prices

    def _find_date_fragment(self, text: str) -> str:
        # Ищем что‑то похожее на дату: 28.03, 28/03, 28 марта и т.п.
        m = re.search(r"\b(\d{1,2}[./]\d{1,2}(\.\d{2,4})?)", text)
        if m:
            return m.group(1)
        lower = text.lower()
        for month in self.month_words:
            idx = lower.find(month)
            if idx != -1:
                start = max(0, idx - 5)
                end = min(len(text), idx + 10)
                return text[start:end].strip()
        return ""

    def build_digest(self, messages_by_channel: Dict[str, List[Dict[str, Any]]]) -> str:
        """Строит дайджест по постам за период."""
        total_msgs = sum(len(v) for v in messages_by_channel.values())
        if total_msgs == 0:
            return ""

        novelties = []
        events = []
        prices = []

        for channel, messages in messages_by_channel.items():
            for msg in messages:
                text = msg.get("text") or ""
                if not text:
                    continue
                text_lower = text.lower()
                time_str = msg.get("time_str", "")
                views = msg.get("views", 0) or 0

                # Новинки / релизы
                if any(k in text_lower for k in self.novelty_keywords):
                    brand = self._find_brand(text_lower)
                    snippet = text.strip().replace("\n", " ")
                    if len(snippet) > 160:
                        snippet = snippet[:157] + "..."
                    novelties.append(
                        {
                            "channel": channel,
                            "time": time_str,
                            "brand": brand,
                            "text": snippet,
                            "views": views,
                        }
                    )

                # События / мероприятия
                if any(k in text_lower for k in self.event_keywords):
                    date_frag = self._find_date_fragment(text)
                    snippet = text.strip().replace("\n", " ")
                    if len(snippet) > 160:
                        snippet = snippet[:157] + "..."
                    events.append(
                        {
                            "channel": channel,
                            "time": time_str,
                            "date": date_frag,
                            "text": snippet,
                            "views": views,
                        }
                    )

                # Цены / офферы
                found_prices = self._find_prices(text)
                if found_prices:
                    brand = self._find_brand(text_lower)
                    # Пытаемся понять контекст продукта
                    product = ""
                    for kw in self.product_keywords:
                        if kw in text_lower:
                            product = kw
                            break
                    snippet = text.strip().replace("\n", " ")
                    if len(snippet) > 160:
                        snippet = snippet[:157] + "..."
                    prices.append(
                        {
                            "channel": channel,
                            "time": time_str,
                            "brand": brand,
                            "product": product,
                            "prices": found_prices,
                            "text": snippet,
                            "views": views,
                        }
                    )

        lines: List[str] = []
        lines.append("## 📌 Дайджест по конкретным постам\n")

        # Новинки и релизы
        if novelties:
            lines.append("### 🆕 Новинки и релизы\n\n")
            # Сортируем по просмотрам
            novelties_sorted = sorted(novelties, key=lambda x: x["views"], reverse=True)
            for item in novelties_sorted[:10]:
                brand_part = f"{item['brand']}: " if item["brand"] else ""
                lines.append(
                    f"- [{item['channel']}] {item['time']} — {brand_part}{item['text']}\n"
                )
            lines.append("")

        # Мероприятия
        if events:
            lines.append("### 🎪 Мероприятия и активность\n\n")
            events_sorted = sorted(events, key=lambda x: x["views"], reverse=True)
            for item in events_sorted[:10]:
                date_part = f" ({item['date']})" if item["date"] else ""
                lines.append(
                    f"- [{item['channel']}] {item['time']}{date_part} — {item['text']}\n"
                )
            lines.append("")

        # Цены и офферы
        if prices:
            lines.append("### 💸 Цены и офферы\n\n")
            prices_sorted = sorted(prices, key=lambda x: x["views"], reverse=True)
            for item in prices_sorted[:10]:
                brand_part = f"{item['brand']} " if item["brand"] else ""
                product_part = f"{item['product']} " if item["product"] else ""
                # Берём уникальные цены
                uniq_prices = sorted(set(item["prices"]))
                price_str = ", ".join(f"{p}₽" for p in uniq_prices[:3])
                extra = "…" if len(uniq_prices) > 3 else ""
                lines.append(
                    f"- [{item['channel']}] {item['time']} — {brand_part}{product_part}за {price_str}{extra}. {item['text']}\n"
                )
            lines.append("")

        # Если ничего не нашли — не засоряем отчёт
        useful_sections = any([novelties, events, prices])
        if not useful_sections:
            return ""

        return "\n".join(lines)

