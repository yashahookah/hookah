from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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

BASE_DIR = Path(__file__).resolve().parent

# Описания ароматов из Flavors ALL TANGIERS
_FLAVOR_DESCRIPTIONS: dict[str, str] = {}
_FLAVOR_BY_BASE: dict[str, str] = {}  # base name -> full key


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

templates = Jinja2Templates(directory=BASE_DIR / "templates")


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
    init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/kiosk", status_code=302)


@app.get("/seller", response_class=HTMLResponse)
def seller_page(request: Request):
    # та же страница, что и киоск, но можно позже добавить initial_view=\"seller\"
    return templates.TemplateResponse("app.html", {"request": request})


@app.get("/picking", response_class=HTMLResponse)
def picking_page(request: Request):
    return templates.TemplateResponse("picking.html", {"request": request})


@app.get("/kiosk", response_class=HTMLResponse)
def kiosk_page(request: Request):
    return templates.TemplateResponse("app.html", {"request": request})

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
        result.append(
            ProductOut(
                id=product.id,
                name=product.name,
                code=product.code,
                price=product.price,
                quantity=stock.quantity,
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

    order.status = payload.status.value
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

