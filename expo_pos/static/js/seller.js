const state = {
  products: [],
  cart: window.posCart || (window.posCart = {}), // общая корзина с киоском
};

function escapeHtml(s) {
  if (!s) return "";
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

async function fetchProducts() {
  const res = await fetch("/api/products");
  if (!res.ok) {
    console.error("Ошибка загрузки товаров");
    return;
  }
  const data = await res.json();
  state.products = data;
  renderProducts();
  renderCart();
}

function renderProducts() {
  const container = document.getElementById("products");
  container.innerHTML = "";

  // сортируем по имени и разбиваем по группам A–Z
  const groups = {};
  const sorted = [...state.products].sort((a, b) =>
    (a.name || "").localeCompare(b.name || "", "en")
  );

  sorted.forEach((p) => {
    const first = (p.name || p.code || "").trim().charAt(0).toUpperCase();
    const letter = first.match(/[A-ZА-Я]/) ? first : "#";
    if (!groups[letter]) groups[letter] = [];
    groups[letter].push(p);
  });

  const letters = Object.keys(groups).sort((a, b) => a.localeCompare(b, "en"));

  letters.forEach((letter) => {
    const groupEl = document.createElement("section");
    groupEl.className = "products-group";
    groupEl.id = `group-${letter}`;

    const header = document.createElement("div");
    header.className = "products-group__header";
    header.textContent = letter === "#" ? "Прочее" : letter;
    groupEl.appendChild(header);

    const list = document.createElement("div");
    list.className = "products-group__list";

    groups[letter].forEach((p) => {
      const qty = state.cart[p.id] || 0;
      const desc = (p.description || "").trim();
      const card = document.createElement("div");
      card.className = "product-card";
      card.innerHTML = `
        ${desc ? `<div class="product-card__desc">${escapeHtml(desc)}</div>` : ""}
        <div class="product-card__name">${escapeHtml(p.name)}</div>
        <div class="product-card__price">${p.price.toFixed(0)} ₽</div>
        <div class="product-card__stock">Остаток: ${p.quantity}</div>
        <div class="product-card__controls">
          <button class="qty-btn" data-role="dec" data-id="${p.id}">-</button>
          <span class="qty-value">${qty}</span>
          <button class="qty-btn" data-role="inc" data-id="${p.id}">+</button>
        </div>
      `;
      list.appendChild(card);
    });

    groupEl.appendChild(list);
    container.appendChild(groupEl);
  });

  buildAlphaNav(letters);

  container.addEventListener("click", (e) => {
    const btn = e.target;
    if (!btn.dataset || !btn.dataset.role) return;
    const id = parseInt(btn.dataset.id, 10);
    if (btn.dataset.role === "inc") {
      addToCart(id, 1);
    } else if (btn.dataset.role === "dec") {
      addToCart(id, -1);
    }
  });
}

function buildAlphaNav(letters) {
  const nav = document.getElementById("seller-alpha-nav");
  if (!nav) return;
  nav.innerHTML = "";

  const used = letters
    .filter((ch) => ch !== "#")
    .sort((a, b) => a.localeCompare(b, "en"));

  used.forEach((ch, index) => {
    const el = document.createElement("button");
    el.type = "button";
    el.textContent = ch;
    el.className = "seller-alpha-nav__letter";
    if (index === 0) {
      el.classList.add("seller-alpha-nav__letter--active");
    }
    el.addEventListener("click", () => {
      document
        .querySelectorAll(".seller-alpha-nav__letter")
        .forEach((btn) => btn.classList.remove("seller-alpha-nav__letter--active"));
      el.classList.add("seller-alpha-nav__letter--active");

      const target = document.getElementById(`group-${ch}`);
      if (target && target.scrollIntoView) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
    nav.appendChild(el);
  });
}

function addToCart(productId, delta) {
  const product = state.products.find((p) => p.id === productId);
  if (!product) return;
  const current = state.cart[productId] || 0;
  let next = current + delta;
  if (next < 0) next = 0;
  if (next > product.quantity) next = product.quantity;
  state.cart[productId] = next;
  if (next === 0) {
    delete state.cart[productId];
  }
  renderProducts();
  renderCart();
}

function renderCart() {
  const itemsEl = document.getElementById("cart-items");
  const emptyEl = document.getElementById("cart-empty");
  const totalEl = document.getElementById("cart-total");
  const submitBtn = document.getElementById("submit-order");
  const msgEl = document.getElementById("cart-message");
  const floating = document.getElementById("seller-floating-summary");
  const floatingValue = document.getElementById("seller-floating-total");

  itemsEl.innerHTML = "";
  msgEl.textContent = "";
  msgEl.className = "cart-message";

  const entries = Object.entries(state.cart);
  if (entries.length === 0) {
    emptyEl.style.display = "block";
    submitBtn.disabled = true;
    totalEl.textContent = "0 ₽";
    if (floating && floatingValue) {
      floating.style.display = "flex";
      floatingValue.textContent = "0 шт · 0 ₽";
    }
    return;
  }

  emptyEl.style.display = "none";
  let total = 0;
  let totalQty = 0;

  entries.forEach(([idStr, qty]) => {
    const id = parseInt(idStr, 10);
    const product = state.products.find((p) => p.id === id);
    if (!product) return;
    const lineAmount = product.price * qty;
    total += lineAmount;
    totalQty += qty;
    const li = document.createElement("li");
    li.className = "cart-item";
    li.innerHTML = `
      <div>
        <div class="cart-item__name">${product.name}</div>
        <div class="cart-item__meta">${qty} × ${product.price.toFixed(
          0
        )} ₽</div>
      </div>
      <div>${lineAmount.toFixed(0)} ₽</div>
    `;
    itemsEl.appendChild(li);
  });

  totalEl.textContent = `${total.toFixed(0)} ₽`;
  submitBtn.disabled = false;

  if (floating && floatingValue) {
    floating.style.display = "flex";
    floatingValue.textContent = `${totalQty} шт · ${total.toFixed(0)} ₽`;
  }
}

async function submitOrder() {
  const entries = Object.entries(state.cart);
  if (entries.length === 0) return;

  const items = entries.map(([idStr, qty]) => ({
    product_id: parseInt(idStr, 10),
    quantity: qty,
  }));

  const msgEl = document.getElementById("cart-message");
  const btn = document.getElementById("submit-order");
  btn.disabled = true;
  msgEl.textContent = "Отправка заказа...";
  msgEl.className = "cart-message";

  try {
    const res = await fetch("/api/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ items }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Ошибка создания заказа");
    }

    Object.keys(state.cart).forEach((k) => delete state.cart[k]);
    await fetchProducts();

    msgEl.textContent = "Заказ создан. Можно собирать.";
    msgEl.className = "cart-message cart-message--ok";
  } catch (e) {
    console.error(e);
    msgEl.textContent = e.message || "Ошибка";
    msgEl.className = "cart-message cart-message--error";
  } finally {
    btn.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fetchProducts();
  document
    .getElementById("submit-order")
    .addEventListener("click", submitOrder);

  const floating = document.getElementById("seller-floating-summary");
  if (floating) {
    floating.addEventListener("click", () => {
      // при клике плавно скроллим к блоку корзины
      const cart = document.querySelector(".seller__cart");
      if (cart && cart.scrollIntoView) {
        cart.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }
});

