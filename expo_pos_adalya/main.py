from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
from sqlalchemy import func, text
from sqlalchemy.orm import Session

# Поддерживаем оба режима запуска:
# - как пакет: `uvicorn expo_pos_adalya.main:app`
# - из папки: `cd expo_pos_adalya && uvicorn main:app`
try:
    from .database import Base, engine, get_db
    from .models import (
        Order,
        OrderItem,
        OrderStatus,
        Product,
        Session as DbSession,
        Stock,
    )
    from .schemas import OrderCreate, OrderOut, OrderStatusUpdate, ProductOut
except ImportError:  # pragma: no cover
    from database import Base, engine, get_db
    from models import (
        Order,
        OrderItem,
        OrderStatus,
        Product,
        Session as DbSession,
        Stock,
    )
    from schemas import OrderCreate, OrderOut, OrderStatusUpdate, ProductOut
from pathlib import Path
import json
import re

BASE_DIR = Path(__file__).resolve().parent

# Описания ароматов из Flavors ALL TANGIERS
_FLAVOR_DESCRIPTIONS: dict[str, str] = {}
_FLAVOR_BY_BASE: dict[str, str] = {}  # base name -> full key

ADALYA_FLAVOR_DESCRIPTIONS: dict[str, str] = {
    "berrymix": "Ягодный микс. Яркий букет спелых ягод с сочным сладко-кислым профилем.",
    "kaktus": "Кактус. Экзотический свежий вкус с мягкой травянистой ноткой.",
    "karamel": "Карамель. Теплый десертный аромат с насыщенной сладостью.",
    "love66": "Шампанское. Легкий игристый профиль с праздничным настроением.",
    "ledy_killer": "Ананас. Яркий тропический вкус со сладкой сочной подачей.",
    "ledy_banan_milk": "Малина и холодок. Сочная ягода с чистым ледяным финишем.",
    "lemon_pie": "Лимонный пирог. Десертный лимон с мягкой сливочной подложкой.",
    "moloko": "Молоко. Нежный кремовый вкус для мягких сладких миксов.",
    "citrus_mix": "Апельсин. Сочный цитрус с бодрой кисло-сладкой подачей.",
    "strawberry": "Клубника. Классический сладкий ягодный вкус на каждый день.",
    "ice": "Лед. Чистый холод для усиления свежести в любых сочетаниях.",
    "mango_tango": "Манго маракуйя. Тропический дуэт с насыщенным фруктовым телом.",
    "mint": "Мята. Освежающий мятный профиль с чистым прохладным послевкусием.",
}


def _load_flavor_descriptions():
    global _FLAVOR_DESCRIPTIONS, _FLAVOR_BY_BASE
    path = BASE_DIR / "flavor_descriptions.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            _FLAVOR_DESCRIPTIONS = json.load(f)
        for key in _FLAVOR_DESCRIPTIONS:
            base = re.sub(r"\s*\(TC\s+\d+\)\s*$", "", key, flags=re.I).strip()
            if base and base not in _FLAVOR_BY_BASE:
                _FLAVOR_BY_BASE[base] = key


def get_flavor_description(product_name: str) -> str | None:
    if not _FLAVOR_DESCRIPTIONS:
        _load_flavor_descriptions()
    if not product_name:
        return None
    if product_name in _FLAVOR_DESCRIPTIONS:
        return _FLAVOR_DESCRIPTIONS[product_name]
    if product_name in _FLAVOR_BY_BASE:
        return _FLAVOR_DESCRIPTIONS[_FLAVOR_BY_BASE[product_name]]
    # варианты Cool Strawberry N / Pink -> Cool Strawberry
    if "Cool Strawberry" in product_name:
        return _FLAVOR_DESCRIPTIONS.get("Cool Strawberry")
    # Lemon-Lime -> Lemon - Lime
    norm = product_name.replace("-", " - ").replace("  ", " ")
    if norm in _FLAVOR_DESCRIPTIONS:
        return _FLAVOR_DESCRIPTIONS[norm]
    if norm in _FLAVOR_BY_BASE:
        return _FLAVOR_DESCRIPTIONS[_FLAVOR_BY_BASE[norm]]
    return None

app = FastAPI(title="Expo POS Demo")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

# Быстрый выигрыш для мобильных сетей: сжатие ответов.
app.add_middleware(GZipMiddleware, minimum_size=512)


class StaticCacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if (request.url.path or "").startswith("/static/"):
            # Кэшируем статику надолго; версии ассетов контролируются через ?v=...
            response.headers["Cache-Control"] = "public, max-age=2592000, immutable"
        return response


app.add_middleware(StaticCacheControlMiddleware)

templates = Jinja2Templates(directory=BASE_DIR / "templates")

def render_template_html(name: str, request: Request, **context) -> HTMLResponse:
    template = templates.env.get_template(name)
    html = template.render({"request": request, **context})
    return HTMLResponse(content=html)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Иконка сайта для браузера (/favicon.ico)."""
    path = BASE_DIR / "static" / "img" / "favicon.svg"
    return FileResponse(path)


def init_db():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        # Полностью очищаем каталог и остатки для отдельного проекта Adalya
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(Stock).delete()
        db.query(Product).delete()
        db.commit()

        # Только ароматы Adalya, которые ты прислал
        sample_products = [
            {"name": "Berrymix", "code": "berrymix", "price": 750.0, "quantity": 50},
            {"name": "Cactus", "code": "kaktus", "price": 750.0, "quantity": 50},
            {"name": "Caramel", "code": "karamel", "price": 750.0, "quantity": 50},
            {"name": "Champagne", "code": "love66", "price": 750.0, "quantity": 50},
            {"name": "Pineapple", "code": "ledy_killer", "price": 750.0, "quantity": 50},
            {"name": "Ice Raspberry", "code": "ledy_banan_milk", "price": 750.0, "quantity": 50},
            {"name": "Lemon Pie", "code": "lemon_pie", "price": 750.0, "quantity": 50},
            {"name": "Milk", "code": "moloko", "price": 750.0, "quantity": 50},
            {"name": "Orange", "code": "citrus_mix", "price": 750.0, "quantity": 50},
            {"name": "Strawberry", "code": "strawberry", "price": 750.0, "quantity": 50},
            {"name": "Ice", "code": "ice", "price": 750.0, "quantity": 50},
            {"name": "Mango Tango", "code": "mango_tango", "price": 750.0, "quantity": 50},
            {"name": "Mint", "code": "mint", "price": 750.0, "quantity": 50},
        ]

        for idx, p in enumerate(sample_products):
            product = Product(
                name=p["name"],
                code=p["code"],
                price=p["price"],
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


def ensure_order_payment_method_column():
    db = next(get_db())
    try:
        table_exists = db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
        ).fetchone()
        if not table_exists:
            return
        rows = db.execute(text("PRAGMA table_info(orders)")).fetchall()
        columns = {str(r[1]) for r in rows}
        if "payment_method" not in columns:
            db.execute(
                text(
                    "ALTER TABLE orders ADD COLUMN payment_method VARCHAR DEFAULT 'cash'"
                )
            )
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()
    ensure_order_payment_method_column()


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
        desc = ADALYA_FLAVOR_DESCRIPTIONS.get(product.code)
        result.append(
            ProductOut(
                id=product.id,
                name=product.name,
                code=product.code,
                price=product.price,
                quantity=stock.quantity,
                in_stock=stock.quantity > 0,
                description=desc,
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

    payment_method = str(payload.payment_method or "cash").strip().lower()
    if payment_method not in {"cash", "qr"}:
        payment_method = "cash"

    order = Order(
        session_id=session.id,
        status=OrderStatus.NEW.value,
        payment_method=payment_method,
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

    # При отмене возвращаем остатки только один раз.
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
        payment_method=(order.payment_method or "cash"),
        total_amount=order.total_amount,
        created_at=order.created_at,
        items=items,
    )

