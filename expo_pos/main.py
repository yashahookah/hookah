from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Order, OrderItem, OrderStatus, Product, Session as DbSession, Stock
from schemas import OrderCreate, OrderOut, OrderStatusUpdate, ProductOut
from pathlib import Path
import json
import re
import difflib
import csv

BASE_DIR = Path(__file__).resolve().parent

# Индексация картинок упаковок для фильтрации ароматов.
# Хочешь скрывать "пустые" ароматы — проверяем существование файлов в `static/img`.
_STATIC_IMG_DIR = BASE_DIR / "static" / "img"
_STATIC_IMG_FILES_LOWER: set[str] | None = None

# Данные по вкусам (названия/описания) из Excel выгрузки.
_TNG_CSV_PATH = BASE_DIR / "tng_product_info.csv"
_TNG_LOADED = False
_TNG_BY_NORM: dict[str, dict[str, str]] = {}
_TNG_NORM_LIST: list[tuple[str, dict[str, str]]] = []


def _norm_tng_lookup(s: str) -> str:
    """
    Компактный ключ для сопоставления имён:
    - приводим к нижнему регистру
    - приводим ё->е и апострофы
    - оставляем только буквы/цифры (англ/рус)
    """
    s2 = str(s or "").strip().lower()
    s2 = s2.replace("ё", "е").replace("’", "'")
    # убираем служебные суффиксы в названиях упаковок (часто встречаются как "зелёный/зелёный", но на деле это часть стема в картинке)
    s2 = re.sub(r"\b(зелёный|зеленый|green)\b", "", s2, flags=re.I).strip()
    s2 = re.sub(r"[^0-9a-zа-я]+", "", s2, flags=re.I)
    return s2


def _load_tng_product_info() -> None:
    """Загружает CSV с 'Оригинальным наименованием' -> 'русским названием' + 'описанием аромата'."""
    global _TNG_LOADED, _TNG_BY_NORM, _TNG_NORM_LIST
    if _TNG_LOADED:
        return
    _TNG_LOADED = True

    if not _TNG_CSV_PATH.exists():
        return

    with open(_TNG_CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        rows = list(reader)

    header_row_idx = None
    header = None
    for i, row in enumerate(rows[:80]):
        joined = ";".join([c.strip() for c in row])
        if "Оригинальное наименование вкуса" in joined and "Описание аромата" in joined:
            header_row_idx = i
            header = row
            break
    if header is None or header_row_idx is None:
        return

    # Карта индексов
    header_map = {str(c).strip(): idx for idx, c in enumerate(header)}
    idx_original = None
    idx_ru = None
    idx_desc_short = None
    idx_1c_name = None
    idx_pack_info = None
    for k, idx in header_map.items():
        if k == "Оригинальное наименование вкуса":
            idx_original = idx
        elif k == "Перевод / Коммерческое наименование на русском":
            idx_ru = idx
        elif k == "Описание аромата":
            idx_desc_short = idx
        elif k == "Наименование продукции в 1С":
            idx_1c_name = idx
        elif k == "Инфо на пачку для каждого отд. Аромата":
            idx_pack_info = idx

    if idx_original is None or idx_ru is None or idx_desc_short is None:
        return

    by_norm: dict[str, dict[str, str]] = {}
    norm_list: list[tuple[str, dict[str, str]]] = []

    for row in rows[header_row_idx + 1 :]:
        if not row or len(row) <= max(idx_original, idx_ru, idx_desc_short, idx_1c_name or 0, idx_pack_info or 0):
            continue
        original_name = str(row[idx_original]).strip()
        if not original_name:
            continue

        ru_name = str(row[idx_ru]).strip()
        desc_short = str(row[idx_desc_short]).strip()
        desc_1c = (
            str(row[idx_1c_name]).strip() if idx_1c_name is not None and idx_1c_name < len(row) else ""
        )
        desc_pack = (
            str(row[idx_pack_info]).strip()
            if idx_pack_info is not None and idx_pack_info < len(row)
            else ""
        )

        def _is_blank_desc(s: str) -> bool:
            ss = (s or "").strip()
            return not ss or ss in {"---", "--", "–", "-"}

        final_desc = desc_short
        if _is_blank_desc(final_desc):
            if not _is_blank_desc(desc_1c):
                final_desc = desc_1c
            elif not _is_blank_desc(desc_pack):
                final_desc = desc_pack
            else:
                final_desc = ""

        # Креативное короткое маркетинговое описание на русском.
        # Важно: не вставляем расшифровку компонентов текстом (типа "Корица - ..."),
        # а только описываем ощущение от аромата.
        components_raw = final_desc.strip().replace("\n", " ")
        # Для классификации можно использовать компоненты, но в текст — не выводим их.
        t = components_raw.lower()
        rn = (ru_name or "").strip().lower()

        def _cut_sentence(s: str, max_len: int = 150) -> str:
            s = re.sub(r"\s+", " ", s).strip()
            if len(s) <= max_len:
                return s
            # режем по последнему пробелу в пределах лимита
            return s[:max_len].rsplit(" ", 1)[0].strip()

        # 1) Гастрономический Bacon
        if "бекон" in t or "bacon" in t or "бекон" in rn:
            description_ru = (
                "Гастрономический копчёно-солоноватый профиль: плотный, тёплый и очень вкусный в миксах."
            )
            description_ru = _cut_sentence(description_ru)
        # 2) Сливочные/десертные (cookie dough, ваниль, крем, карамель, тесто)
        elif any(k in t for k in ["ваниль", "слив", "крем", "карамел", "тесто", "печень", "cookie", "dough", "cream", "ликер"]):
            description_ru = (
                "Нежная десертная сладость: кремовая мягкость и тёплое, обволакивающее послевкусие без лишней приторности."
            )
            description_ru = _cut_sentence(description_ru)
        # 3) Тёплые пряности/чай/чайные миксы
        elif any(k in t for k in ["чай", "cinnamon", "кориц", "гвоздик", "кардамон", "spice", "специ", "chai", "kashmir"]):
            description_ru = (
                "Тёплый пряный характер: аромат специй раскрывается мягко и дарит уютное, долгое послевкусие."
            )
            description_ru = _cut_sentence(description_ru)
        # 4) Мята/холодные травы
        elif any(k in t for k in ["мята", "mint", "wintergreen", "зелён", "green", "cucumber"]):
            description_ru = (
                "Охлаждающая свежесть: мятный/травяной характер бодрит и оставляет чистое, прохладное послевкусие."
            )
            description_ru = _cut_sentence(description_ru)
        # 5) Цитрусы/кисло-свежие (лимон, лайм, грейпфрут, газировка, рассветы)
        elif any(k in t for k in ["лимон", "лайм", "грейпфрут", "grapefruit", "orange", "апельс", "soda", "sunrise", "passionfruit", "мараку"]):
            description_ru = (
                "Яркая цитрусовая волна: лёгкая кислинка и свежий вкус заряжают с первой затяжки."
            )
            description_ru = _cut_sentence(description_ru)
        # 6) Ягоды/фрукты-ягоды
        elif any(k in t for k in ["клубник", "черник", "ежевик", "малина", "ягод", "berry"]):
            description_ru = (
                "Сочная ягодная сладость с аккуратной кислинкой: вкус насыщенный, но сбалансированный."
            )
            description_ru = _cut_sentence(description_ru)
        # 7) Арбуз/кисель/водянистые
        elif any(k in t for k in ["арбуз", "watermelon", "кисель", "sour water"]):
            description_ru = (
                "Летняя арбузная сочность: вкус прохладный, водянистый и очень освежающий."
            )
            description_ru = _cut_sentence(description_ru)
        # 8) Тропики: манго/ананас/папайя/гуайява/пиня-пунш
        elif any(k in t for k in ["манго", "mango", "ананас", "pineapple", "папай", "papaya", "guajava", "guava", "tropical", "passinfruit", "passion"]):
            description_ru = (
                "Тропическая фруктовая волна: сладко-сочно, ярко и по-настоящему ароматно."
            )
            description_ru = _cut_sentence(description_ru)
        # 9) Кашмир/специи без ярких маркеров
        elif any(k in rn for k in ["кашмир", "kashmir"]) or any(k in t for k in ["специи", "spice"]):
            description_ru = (
                "Глубокий пряный профиль с мягкой сладостью: вкус плотный и запоминающийся."
            )
            description_ru = _cut_sentence(description_ru)
        # 10) Остальное (универсально, но не одинаковое для всех)
        else:
            # Универсальный, но короткий вариант
            description_ru = (
                "Выразительный характер: аромат раскрывается мягко, оставляя приятное и чистое послевкусие."
            )
            description_ru = _cut_sentence(description_ru)

        info = {
            "display_name_en": original_name,
            "description": description_ru,
        }

        norm = _norm_tng_lookup(original_name)
        if not norm:
            continue

        # если вдруг дубль — не перетираем, чтобы не потерять более полный текст
        if norm not in by_norm or (not by_norm[norm]["description"] and desc):
            by_norm[norm] = info

    norm_list = [(k, v) for k, v in by_norm.items()]
    _TNG_BY_NORM = by_norm
    _TNG_NORM_LIST = norm_list


def _get_tng_info_for_stem(stem: str) -> dict[str, str]:
    """Возвращает {'display_name_en': ..., 'description': ...} для конкретного файла/стема."""
    _load_tng_product_info()
    if not stem:
        return {"display_name_en": "", "description": ""}

    # Сначала пробуем несколько кандидатов ключа
    candidates = [
        stem,
        re.sub(r"\b(зелёный|зеленый)\b", "", str(stem), flags=re.I).strip(),
    ]
    for c in candidates:
        norm = _norm_tng_lookup(c)
        if norm in _TNG_BY_NORM:
            return _TNG_BY_NORM[norm]

    # Фаззи-поиск по нормализованным строкам
    norm_stem = _norm_tng_lookup(stem)
    if not norm_stem:
        return {"display_name_en": "", "description": ""}

    best_key = None
    best_ratio = 0.0
    for known_norm, info in _TNG_NORM_LIST:
        r = difflib.SequenceMatcher(None, norm_stem, known_norm).ratio()
        if r > best_ratio:
            best_ratio = r
            best_key = known_norm

    if best_key is not None and best_ratio >= 0.78:
        return _TNG_BY_NORM.get(best_key, {"display_name_en": "", "description": ""})

    return {"display_name_en": "", "description": ""}


def _load_static_img_files_index() -> set[str]:
    """Загружает множество имён файлов (lowercase) из `static/img`."""
    global _STATIC_IMG_FILES_LOWER
    if _STATIC_IMG_FILES_LOWER is not None:
        return _STATIC_IMG_FILES_LOWER

    files: set[str] = set()
    if _STATIC_IMG_DIR.exists() and _STATIC_IMG_DIR.is_dir():
        for p in _STATIC_IMG_DIR.iterdir():
            if p.is_file() and p.name.lower().endswith(".png"):
                files.add(p.name.lower())

    _STATIC_IMG_FILES_LOWER = files
    return _STATIC_IMG_FILES_LOWER


def _normalize_filename_key_py(s: str) -> str:
    """Почти 1-в-1 с JS kiosk/seller `NormalizeFilenameKey` (для kebab-case)."""
    if not s:
        return ""
    s2 = str(s).strip().lower()
    s2 = re.sub(r"[’']", "", s2)  # убираем апостроф
    s2 = re.sub(r"[^a-z0-9]+", "-", s2)
    s2 = re.sub(r"-+", "-", s2)
    s2 = s2.strip("-")
    return s2


def _product_packaging_candidates_exist(product_name: str | None, product_code: str | None) -> bool:
    """Есть ли картинка упаковки хотя бы в одном ожидаемом имени."""
    img_index = _load_static_img_files_index()
    if not img_index:
        return False

    candidates: list[str] = []
    if product_code:
        code = str(product_code).strip()
        if code:
            candidates.append(f"{code}.png")

    if product_name:
        name = str(product_name).strip()
        if name:
            # В JS имя кодируется для URL (encodeURIComponent), но на диске имя "как есть".
            candidates.append(f"{name}.png")
            key = _normalize_filename_key_py(name)
            if key:
                candidates.append(f"{key}.png")

    return any(fn.lower() in img_index for fn in candidates)


def _list_pack_image_stems() -> list[str]:
    """Имя товара = stem PNG-файла в `static/img`."""
    if not _STATIC_IMG_DIR.exists() or not _STATIC_IMG_DIR.is_dir():
        return []

    stems: list[str] = []
    for p in _STATIC_IMG_DIR.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() != ".png":
            continue
        stem = p.stem
        # Заглушки/технические файлы исключаем.
        if stem.lower() in {"placeholder-pack"}:
            continue
        stems.append(stem)

    stems.sort(key=lambda s: s.lower())
    return stems


def _sync_products_with_pack_images(db: Session) -> None:
    """
    Приводит `products`/`stock` в БД к текущему набору упаковок:
    - активирует только те продукты, у которых есть PNG в `static/img/`
    - добавляет новые продукты, если их не было
    - отключает старые (которые отсутствуют на диске)
    """
    pack_stems = _list_pack_image_stems()
    if not pack_stems:
        return

    # name -> code (уникальный для БД, т.к. `Product.code` unique)
    name_by_code: dict[str, str] = {}
    for name in pack_stems:
        base_code = _normalize_filename_key_py(name)
        if not base_code:
            continue

        code = base_code
        # Если нормализация дала коллизию — создаём уникальный variant-код.
        if code in name_by_code:
            i = 2
            while f"{base_code}-v{i}" in name_by_code:
                i += 1
            code = f"{base_code}-v{i}"

        name_by_code[code] = name

    active_codes = set(name_by_code.keys())

    default_price = 3000.0
    default_qty = 50
    default_min_threshold = 5

    products = db.query(Product).all()
    stocks = db.query(Stock).all()
    stock_by_pid = {s.product_id: s for s in stocks}
    product_by_code = {p.code: p for p in products if p.code}

    # Обновляем существующие продукты.
    for p in products:
        p.is_active = bool(p.code in active_codes)
        if p.code in name_by_code:
            p.name = name_by_code[p.code]

    # Добавляем отсутствующие и гарантируем stock.
    # Делаем sort_order стабильным: по алфавиту имён файлов.
    stem_order = {stem: i for i, stem in enumerate(pack_stems)}
    for code in sorted(active_codes, key=lambda c: name_by_code[c].lower()):
        name = name_by_code[code]
        if code in product_by_code:
            p = product_by_code[code]
            # При активации убедимся, что quantity > 0.
            p.sort_order = stem_order.get(name, 0)
            if p.price is None:
                p.price = default_price
            s = stock_by_pid.get(p.id)
            if s is None:
                s = Stock(
                    product_id=p.id,
                    quantity=default_qty,
                    min_threshold=default_min_threshold,
                )
                db.add(s)
            elif s.quantity <= 0:
                s.quantity = default_qty
            continue

        p = Product(
            name=name,
            code=code,
            price=default_price,
            sort_order=stem_order.get(name, 0),
            is_active=True,
        )
        db.add(p)
        db.flush()
        product_by_code[code] = p

        s = stock_by_pid.get(p.id)
        if s is None:
            s = Stock(
                product_id=p.id,
                quantity=default_qty,
                min_threshold=default_min_threshold,
            )
            db.add(s)
        else:
            if s.quantity <= 0:
                s.quantity = default_qty
        db.flush()


# Описания ароматов из Flavors ALL TANGIERS
_FLAVOR_DESCRIPTIONS: dict[str, str] = {}
_FLAVOR_BY_BASE: dict[str, str] = {}  # base name -> full key
_FLAVOR_BY_NORM: dict[str, str] = {}  # normalized name -> full key
_FLAVOR_KEYS_NORM: list[tuple[str, str]] = []  # (norm, full_key)
_FLAVOR_FUZZY_CACHE: dict[str, str | None] = {}


def _normalize_flavor_name(s: str) -> str:
    if s is None:
        return ""
    # Нормализуем пробелы/регистр и убираем частые декоративные штуки.
    out = str(s).replace("’", "'").strip().lower()
    out = re.sub(r"\s+", " ", out)
    return out


def _generate_description_from_name(product_name: str) -> str | None:
    """
    Фолбэк на случай, если в `flavor_descriptions.json` нет конкретного ключа.
    На старте это гарантирует, что в UI всегда будут описания под вкусами.
    """
    if not product_name:
        return None

    t = str(product_name).strip().lower()

    if "bacon" in t:
        return (
            "Запеченный бекон: тёплый дымный гастрономический вкус с приятной солоноватой ноткой. "
            "Даёт ощущение «с кухни» и добавляет плотную основу миксам."
        )

    if "basil strawberry" in t or ("basil" in t and "strawberry" in t):
        return (
            "Клубника с травяной глубиной базилика. Сладость ягод мягко уравновешивается свежей "
            "зеленью и оставляет чистое, аккуратное послевкусие."
        )

    if "blueberry grapefruit" in t or ("blueberry" in t and "grapefruit" in t):
        return (
            "Черника и грейпфрут: ягодная сладость встречает бодрую цитрусовую кислинку. "
            "Вкус яркий и свежий, запоминается с первой затяжки."
        )

    if "chai" in t:
        return (
            "Chai — тёплый пряный чайный вкус с мягкой сладостью. "
            "Композиция раскрывается как уютный аромат специй и легко ложится в миксы."
        )

    if "cilantro" in t or "coriander" in t or "кинза" in t:
        return (
            "Кинза: сочная травяная нота и лёгкая пикантность. "
            "Вкус свежий, зелёный и хорошо сочетается с цитрусами и ягодами."
        )

    if "cookie dough" in t or ("cookie" in t and "dough" in t) or "cookies" in t:
        return (
            "Cookie Dough — тёплое сливочное тесто и сладкое печенье. "
            "Комфортная гастрономическая сладость делает миксы насыщенными и «домашними»."
        )

    if "breakfast" in t or "cereal" in t or "it's like that one" in t:
        return (
            "Завтрак в стиле «как тот самый»: овсяные нотки, мягкая выпечная сладость и бодрый цитрусовый акцент. "
            "Лёгкий вкус, который приятно «включает» с первой затяжки."
        )

    if "mango fling" in t or ("mango" in t and "fling" in t):
        return (
            "Mango Fling — сочный манго с фруктовым драйвом и лёгкой кислинкой. "
            "Вкус тропический, яркий и очень бодрый."
        )
    if "mango" in t:
        return (
            "Манго: спелая тропическая сладость и мягкая кислинка. "
            "Сочный вкус, который раскрывается легко и оставляет приятное послевкусие."
        )

    if t == "mixed" or "mixed fruit" in t or "mixed" in t:
        return (
            "Классический фруктовый микс: сладкие ягоды и сочные фрукты в одном направлении. "
            "Баланс держится на насыщенном вкусе и аккуратном послевкусии."
        )

    if "muerte" in t:
        return (
            "Muerte — тёмный, глубокий микс с ягодной сочностью и пряной атмосферой. "
            "Вкус плотный, «бархатный» и долго остаётся в памяти."
        )

    if "papa's f" in t or "papa" in t or "foreplay" in t:
        return (
            "Papa's F / Foreplay: мягкая фруктовая сладость с тропическим акцентом. "
            "Вкус живой, лёгкий и хорошо работает как база для миксов."
        )

    if "passinfruit" in t or "passionfruit" in t:
        return (
            "Passionfruit / Passinfruit Lemonade: маракуйя и лимонад — тропическая кислинка, "
            "пузырьковая свежесть и сладкое послевкусие."
        )

    if "rangoon sunrise" in t or ("rangoon" in t and "sunrise" in t):
        return (
            "Rangoon Sunrise: яркая цитрусовая композиция с мягкой сладостью. "
            "Вкус солнечный, бодрый и очень «утренний»."
        )

    if "static starlight" in t or "starlight" in t:
        if "зелен" in t or "green" in t:
            return (
                "Static Starlight (зелёный): холодная травяная свежесть и лёгкая мятная глубина. "
                "Чистый, прохладный и эффектный вкус."
            )
        return (
            "Static Starlight: тёмный космический микс с прохладным характером и мягким сладким завершением."
        )

    if t == "sunrise" or t.endswith(" sunrise"):
        return (
            "Sunrise — свежий рассвет: цитрусовая яркость и мягкая сладость без резкости. "
            "Лёгкий вкус, который заряжает энергией."
        )

    if t == "sunset" or t.endswith(" sunset"):
        return (
            "Sunset — закат: тропическая фруктовая волна с тёплым, мягким послевкусием. "
            "Сочный вкус, который приятно тянется до конца."
        )

    return None


def _load_flavor_descriptions():
    global _FLAVOR_DESCRIPTIONS, _FLAVOR_BY_BASE, _FLAVOR_BY_NORM, _FLAVOR_KEYS_NORM
    path = BASE_DIR / "flavor_descriptions.json"
    if path.exists():
        _FLAVOR_BY_BASE = {}
        _FLAVOR_BY_NORM = {}
        with open(path, "r", encoding="utf-8") as f:
            _FLAVOR_DESCRIPTIONS = json.load(f)
        for key in _FLAVOR_DESCRIPTIONS:
            base = re.sub(r"\s*\(TC\s+\d+\)\s*$", "", key, flags=re.I).strip()
            if base and base not in _FLAVOR_BY_BASE:
                _FLAVOR_BY_BASE[base] = key
            norm = _normalize_flavor_name(key)
            if norm and norm not in _FLAVOR_BY_NORM:
                _FLAVOR_BY_NORM[norm] = key

        _FLAVOR_KEYS_NORM = [(_normalize_flavor_name(k), k) for k in _FLAVOR_DESCRIPTIONS]


def get_flavor_description(product_name: str) -> str | None:
    if not _FLAVOR_DESCRIPTIONS:
        _load_flavor_descriptions()
    if not product_name:
        return None
    if product_name in _FLAVOR_DESCRIPTIONS:
        return _FLAVOR_DESCRIPTIONS[product_name]
    if product_name in _FLAVOR_BY_BASE:
        return _FLAVOR_DESCRIPTIONS[_FLAVOR_BY_BASE[product_name]]

    norm1 = _normalize_flavor_name(product_name)
    if norm1 and norm1 in _FLAVOR_BY_NORM:
        return _FLAVOR_DESCRIPTIONS[_FLAVOR_BY_NORM[norm1]]

    # варианты Cool Strawberry N / Pink -> Cool Strawberry
    if "Cool Strawberry" in product_name:
        return _FLAVOR_DESCRIPTIONS.get("Cool Strawberry")
    # Lemon-Lime -> Lemon - Lime
    norm2 = product_name.replace("-", " - ").replace("  ", " ")
    if norm2 in _FLAVOR_DESCRIPTIONS:
        return _FLAVOR_DESCRIPTIONS[norm2]
    if norm2 in _FLAVOR_BY_BASE:
        return _FLAVOR_DESCRIPTIONS[_FLAVOR_BY_BASE[norm2]]

    # Последняя попытка: мягкое сопоставление по нормализованной строке.
    if norm1:
        cached = _FLAVOR_FUZZY_CACHE.get(norm1)
        if cached is not None:
            return cached

    if not _FLAVOR_KEYS_NORM:
        return None

    best_key: str | None = None
    best_ratio = 0.0
    for known_norm, known_key in _FLAVOR_KEYS_NORM:
        r = (
            difflib.SequenceMatcher(None, norm1, known_norm).ratio()
            if norm1
            else 0.0
        )
        if r > best_ratio:
            best_ratio = r
            best_key = known_key

    if best_key and best_ratio >= 0.86:
        desc = _FLAVOR_DESCRIPTIONS.get(best_key)
        _FLAVOR_FUZZY_CACHE[norm1] = desc
        return desc

    if norm1:
        _FLAVOR_FUZZY_CACHE[norm1] = None
    generated = _generate_description_from_name(product_name)
    return generated

app = FastAPI(title="Expo POS Demo")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(directory=BASE_DIR / "templates")

def render_template_html(name: str, request: Request, **context) -> HTMLResponse:
    # Обход несовместимостей TemplateResponse между версиями Starlette.
    template = templates.env.get_template(name)
    html = template.render({"request": request, **context})
    return HTMLResponse(content=html)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Иконка сайта для браузера (/favicon.ico)."""
    # В проекте фавикон лежит в /static (без подпапки img).
    path = BASE_DIR / "static" / "favicon.svg"
    return FileResponse(path)


def init_db():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        existing_codes = {
            c for (c,) in db.query(Product.code).all() if c is not None
        }
        sample_products = [
            # базовые вкусы, которые уже были
            {"name": "Sunrise", "code": "sunrise", "price": 500.0, "quantity": 50},
            {
                "name": "Orange Soda",
                "code": "orange-soda",
                "price": 500.0,
                "quantity": 40,
            },
            {
                "name": "Wintergreen",
                "code": "wintergreen",
                "price": 500.0,
                "quantity": 30,
            },
            {
                "name": "Eric's Mango",
                "code": "erics-mango",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Cool Strawberry N",
                "code": "cool-strawberry-n",
                "price": 500.0,
                "quantity": 25,
            },
            {
                "name": "Double Orange",
                "code": "double-orange",
                "price": 500.0,
                "quantity": 25,
            },
            {
                "name": "Cucumber Lavender",
                "code": "cucumber-lavender",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Cool Strawberry Pink",
                "code": "cool-strawberry-pink",
                "price": 500.0,
                "quantity": 20,
            },
            # полный список ароматов Tangiers из картинок
            {
                "name": "2005 Blueberry",
                "code": "2005-blueberry",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Brambleberry",
                "code": "brambleberry",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Blackberry Lime",
                "code": "blackberry-lime",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Cane Mint",
                "code": "cane-mint",
                "price": 500.0,
                "quantity": 20,
            },
            {"name": "Blitzsturm", "code": "blitzsturm", "price": 500.0, "quantity": 20},
            {"name": "Horchata", "code": "horchata", "price": 500.0, "quantity": 20},
            {
                "name": "Juicy Peach",
                "code": "juicy-peach",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Maraschino Cherry",
                "code": "maraschino-cherry",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Guajava Kiss",
                "code": "guajava-kiss",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "I'm coming to get you Varvara",
                "code": "im-coming-to-get-you-varvara",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Kashmir Black",
                "code": "kashmir-black",
                "price": 500.0,
                "quantity": 20,
            },
            {"name": "Kashmir", "code": "kashmir", "price": 500.0, "quantity": 20},
            {
                "name": "Kashmir Apple",
                "code": "kashmir-apple",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Kashmir Mango",
                "code": "kashmir-mango",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Kashmir Cherry",
                "code": "kashmir-cherry",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Lemon-Lime",
                "code": "lemon-lime",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Melon Blend",
                "code": "melon-blend",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "It's Like That One Breakfast Cereal",
                "code": "its-like-that-one-breakfast-cereal",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Papa's Foreplay",
                "code": "papas-foreplay",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Kashmir Peach",
                "code": "kashmir-peach",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Kashmir Guajava",
                "code": "kashmir-guajava",
                "price": 500.0,
                "quantity": 20,
            },
            {"name": "Mimon", "code": "mimon", "price": 500.0, "quantity": 20},
            {"name": "Ololiuqui", "code": "ololiuqui", "price": 500.0, "quantity": 20},
            {
                "name": "Mixed Fruit",
                "code": "mixed-fruit",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Peach Iced Tea",
                "code": "peach-iced-tea",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Pineapple",
                "code": "pineapple",
                "price": 500.0,
                "quantity": 20,
            },
            {"name": "Nectarine", "code": "nectarine", "price": 500.0, "quantity": 20},
            {
                "name": "Papaya Sorbet",
                "code": "papaya-sorbet",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Passionfruit Lemonade",
                "code": "passionfruit-lemonade",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Static Starlight",
                "code": "static-starlight",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Pinepas",
                "code": "pinepas",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Prince of Gray",
                "code": "prince-of-gray",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Pink Grapefruit",
                "code": "pink-grapefruit",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Schnozzberry",
                "code": "schnozzberry",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Strawberry Lemonade",
                "code": "strawberry-lemonade",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Static Starlight Noir",
                "code": "static-starlight-noir",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Sunset",
                "code": "sunset",
                "price": 500.0,
                "quantity": 20,
            },
            {"name": "Strawberry", "code": "strawberry", "price": 500.0, "quantity": 20},
            {
                "name": "Welsh Cream",
                "code": "welsh-cream",
                "price": 500.0,
                "quantity": 20,
            },
            {"name": "Watermelon", "code": "watermelon", "price": 500.0, "quantity": 20},
            {
                "name": "Sour Watermelon",
                "code": "sour-watermelon",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Surfer's Delight",
                "code": "surfers-delight",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Tropical Punch",
                "code": "tropical-punch",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Tropical Revenge!",
                "code": "tropical-revenge",
                "price": 500.0,
                "quantity": 20,
            },
            {
                "name": "Rangoon Sunrise",
                "code": "rangoon-sunrise",
                "price": 500.0,
                "quantity": 20,
            },
        ]

        # добавляем только те товары, которых ещё нет по коду
        for idx, p in enumerate(sample_products):
            if p["code"] in existing_codes:
                continue
            product = Product(
                name=p["name"],
                code=p["code"],
                price=3000.0,  # единая цена за пачку
                sort_order=idx,
                is_active=True,
            )
            db.add(product)
            db.flush()
            stock = Stock(
                product_id=product.id,
                quantity=p["quantity"],
                min_threshold=5,
            )
            db.add(stock)

        # Приводим набор товаров к тому, что реально есть в `static/img`.
        # Это убирает "старые" ароматы и добавляет "новые" упаковки.
        _sync_products_with_pack_images(db)

        active_session = (
            db.query(DbSession).filter(DbSession.is_active.is_(True)).first()
        )
        if not active_session:
            session = DbSession(
                name="Выставка - день 1",
                starts_at=datetime.utcnow(),
                is_active=True,
            )
            db.add(session)

        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    _load_tng_product_info()
    init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/kiosk", status_code=302)


@app.get("/seller", response_class=HTMLResponse)
def seller_page(request: Request):
    # та же страница, что и киоск, но можно позже добавить initial_view=\"seller\"
    return render_template_html("app.html", request)


@app.get("/picking", response_class=HTMLResponse)
def picking_page(request: Request):
    return render_template_html("picking.html", request)


@app.get("/kiosk", response_class=HTMLResponse)
def kiosk_page(request: Request):
    return render_template_html("app.html", request)

@app.get("/api/products", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = (
        db.query(Product, Stock)
        .join(Stock, Stock.product_id == Product.id)
        .filter(Product.is_active.is_(True))
        .order_by(Product.sort_order, Product.name)
        .all()
    )
    result: List[ProductOut] = []
    for product, stock in products:
        desc = get_flavor_description(product.name)
        tng_info = _get_tng_info_for_stem(product.name)
        display_name_en = tng_info.get("display_name_en") or product.name
        # Явные исправления отображаемых английских названий.
        # Нужны как "последний слой" даже если CSV/БД содержат старый вариант.
        code_key = (product.code or "").strip().lower()
        name_key = (product.name or "").strip().lower()
        if code_key in {"cilantro", "cilantro-pineapple"} or name_key == "cilantro":
            display_name_en = "Cilantro pineapple"
        elif code_key in {"muerte", "muerte-por-arroz"} or name_key == "muerte":
            display_name_en = "Muerte por Arroz"
        elif code_key in {"mixed", "mixed-fruit"} or name_key == "mixed":
            display_name_en = "Mixed Fruit"
        elif code_key in {"papas-f", "papas-foreplay"} or name_key in {"papa's f", "papas f"}:
            display_name_en = "Papa's Foreplay"
        csv_desc = tng_info.get("description") or ""
        # Если в CSV есть описание — используем его (это и есть "фулл список").
        final_desc = csv_desc.strip() or desc
        result.append(
            ProductOut(
                id=product.id,
                name=product.name,
                display_name_en=display_name_en,
                code=product.code,
                price=product.price,
                quantity=stock.quantity,
                in_stock=stock.quantity > 0,
                description=final_desc,
            )
        )
    return result


@app.get("/api/sessions/active")
def get_active_session(db: Session = Depends(get_db)):
    session = db.query(DbSession).filter(DbSession.is_active.is_(True)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")
    return {"id": session.id, "name": session.name}


@app.post("/api/orders", response_model=OrderOut)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must contain items")

    if payload.session_id is not None:
        session = db.query(DbSession).filter(DbSession.id == payload.session_id).first()
    else:
        session = db.query(DbSession).filter(DbSession.is_active.is_(True)).first()

    if not session:
        raise HTTPException(status_code=400, detail="Session not found")

    product_ids = [item.product_id for item in payload.items]
    products = (
        db.query(Product, Stock)
        .join(Stock, Stock.product_id == Product.id)
        .filter(Product.id.in_(product_ids))
        .all()
    )
    products_map = {p.id: (p, s) for p, s in products}

    for item in payload.items:
        if item.product_id not in products_map:
            raise HTTPException(
                status_code=400, detail=f"Product {item.product_id} not found"
            )
        _, stock = products_map[item.product_id]
        if item.quantity <= 0:
            raise HTTPException(
                status_code=400, detail="Quantity must be greater than zero"
            )
        if stock.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {item.product_id}",
            )

    order = Order(
        session_id=session.id,
        status=OrderStatus.NEW.value,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(order)
    db.flush()

    total_amount = 0.0
    order_items: List[OrderItem] = []

    for item in payload.items:
        product, stock = products_map[item.product_id]
        line_amount = product.price * item.quantity
        total_amount += line_amount
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price,
            line_amount=line_amount,
        )
        order_items.append(order_item)
        stock.quantity -= item.quantity
        db.add(stock)

    order.total_amount = total_amount
    db.add_all(order_items)
    db.commit()
    db.refresh(order)

    return _order_to_out(order)


@app.get("/api/orders", response_model=List[OrderOut])
def list_orders(
    statuses: Optional[List[OrderStatus]] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Order)
    if statuses:
        status_values = [s.value for s in statuses]
        query = query.filter(Order.status.in_(status_values))
    orders = query.order_by(Order.created_at.desc()).limit(100).all()
    return [_order_to_out(o) for o in orders]


@app.patch("/api/orders/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)
):
    order: Optional[Order] = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    prev_status = order.status
    next_status = payload.status.value
    if prev_status == next_status:
        return _order_to_out(order)

    # Если заказ отменяют — возвращаем остатки обратно один раз.
    if next_status == OrderStatus.CANCELED.value and prev_status != OrderStatus.CANCELED.value:
        if prev_status == OrderStatus.PAID.value:
            raise HTTPException(status_code=400, detail="Paid order cannot be canceled")
        for item in order.items:
            stock = (
                db.query(Stock).filter(Stock.product_id == item.product_id).first()
            )
            if stock:
                stock.quantity += int(item.quantity or 0)
                db.add(stock)

    order.status = next_status
    order.updated_at = datetime.utcnow()
    db.add(order)
    db.commit()
    db.refresh(order)

    return _order_to_out(order)


def _order_to_out(order: Order) -> OrderOut:
    items = [
        {
            "product_id": item.product_id,
            "product_name": item.product.name if item.product else "",
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "line_amount": item.line_amount,
        }
        for item in order.items
    ]
    return OrderOut(
        id=order.id,
        status=OrderStatus(order.status),
        total_amount=order.total_amount,
        created_at=order.created_at,
        items=items,
    )

