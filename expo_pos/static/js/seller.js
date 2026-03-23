const state = {
  products: [],
  cart: window.posCart || (window.posCart = {}), // общая корзина с киоском
  search: "",
};

let productsClickBound = false;
let orderToastTimer = null;

const RU_NAME_OVERRIDES = {
  "2005 Blueberry": "Черничный кекс",
  "Blackberry Lime": "Ежевика и лайм",
  Blitzsturm: "Лаванда и мята",
  "Cane Mint": "Мятные леденцы",
  Horchata: "Орчата, рисовый напиток",
};

// Алиасы для поиска: как люди пишут на слух по‑русски
const SEARCH_ALIASES = {
  "кейн минт": "Cane Mint",
  "кане минт": "Cane Mint",
  "кейнминт": "Cane Mint",
  "канеминт": "Cane Mint",
  "кэйн минт": "Cane Mint",
  "кеин минт": "Cane Mint",
  "кейн": "Cane Mint",
  "кей": "Cane Mint",

  "блитцштурм": "Blitzsturm",
  "блитзштурм": "Blitzsturm",
  "блицштурм": "Blitzsturm",
  "блиц шторм": "Blitzsturm",
  "блитз": "Blitzsturm",

  орчата: "Horchata",
  орчатта: "Horchata",
  орчадо: "Horchata",
  хорчата: "Horchata",

  кул: "Cool Strawberry",
  "кул стравбери": "Cool Strawberry",
  "кул стробери": "Cool Strawberry",

  "эрик манго": "Eric's Mango",
  "ерик манго": "Eric's Mango",
  эрик: "Eric's Mango",
  ерик: "Eric's Mango",
};

function sellerNormalizeFilenameKey(s) {
  if (!s) return "";
  return String(s)
    .trim()
    .toLowerCase()
    .replace(/[’']/g, "") // убираем апостроф
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

function sellerGetImageCandidates(product) {
  const code = product && product.code ? String(product.code).trim() : "";
  const name = product && product.name ? String(product.name).trim() : "";
  const out = [];
  if (code) out.push(`/static/img/${code}.png`);
  if (name) out.push(`/static/img/${encodeURIComponent(name)}.png`);
  if (name) {
    const key = sellerNormalizeFilenameKey(name);
    if (key) out.push(`/static/img/${key}.png`);
  }
  return out;
}

function sellerGetImageUrl(product) {
  const candidates = sellerGetImageCandidates(product);
  if (candidates && candidates.length) return candidates[0];
  return "/static/img/placeholder-pack.png";
}

function showOrderToast(orderId) {
  const rootId = "order-toast";
  let root = document.getElementById(rootId);
  if (!root) {
    root = document.createElement("div");
    root.id = rootId;
    root.className = "order-toast";
    root.innerHTML = `
      <div class="order-toast__card">
        <button type="button" class="order-toast__close" data-role="order-toast-close">×</button>
        <div class="order-toast__title">Заказ оформлен</div>
        <div class="order-toast__text">
          Заказ № <span class="order-toast__number" data-role="order-toast-number"></span>
          отправлен на сборку. Пожалуйста, <strong>запомните</strong> или <strong>сделайте скриншот</strong> этого номера — он понадобится на выдаче.
        </div>
      </div>
    `;
    document.body.appendChild(root);
    const closeBtn = root.querySelector("[data-role='order-toast-close']");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        root.classList.remove("order-toast--visible");
        if (orderToastTimer) {
          clearTimeout(orderToastTimer);
          orderToastTimer = null;
        }
      });
    }
  }

  const numEl = root.querySelector("[data-role='order-toast-number']");
  if (numEl) {
    numEl.textContent = orderId != null ? String(orderId) : "—";
  }

  root.classList.add("order-toast--visible");
  if (orderToastTimer) {
    clearTimeout(orderToastTimer);
  }
  orderToastTimer = setTimeout(() => {
    root.classList.remove("order-toast--visible");
    orderToastTimer = null;
  }, 15000);
}

function escapeHtml(s) {
  if (!s) return "";
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

function shortenDescription(text, maxLen = 110) {
  if (!text) return "";
  const s = String(text).trim();
  if (s.length <= maxLen) return s;
  const cut = s.slice(0, maxLen);
  const lastSpace = cut.lastIndexOf(" ");
  const base = lastSpace > maxLen * 0.6 ? cut.slice(0, lastSpace) : cut;
  return base.trim() + "…";
}

function buildRuName(product) {
  const override = RU_NAME_OVERRIDES[product.name];
  if (override) return override;
  const desc = (product.description || "").trim();
  if (!desc) return "";
  let sentence = desc.split(/[.!?]/)[0] || desc;
  sentence = sentence.split("—")[0] || sentence;
  sentence = sentence.trim();
  if (sentence.length > 40) {
    const words = sentence.split(/\s+/).slice(0, 3);
    sentence = words.join(" ");
  }
  return sentence;
}

function normalizeTextForSearch(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/ё/g, "е")
    .replace(/[’']/g, "")
    .replace(/[^a-zа-я0-9]+/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function resolveAliasTarget(normQ) {
  if (!normQ) return null;
  if (SEARCH_ALIASES[normQ]) return SEARCH_ALIASES[normQ];
  for (const key in SEARCH_ALIASES) {
    if (normQ.includes(key)) return SEARCH_ALIASES[key];
  }
  return null;
}

function getAccentColorFromCode(code) {
  const base = String(code || "").toLowerCase() || "default";
  let hash = 0;
  for (let i = 0; i < base.length; i++) {
    hash = (hash * 31 + base.charCodeAt(i)) >>> 0;
  }
  const hue = hash % 360;
  const sat = 80;
  const light = 55;
  return `hsl(${hue}deg ${sat}% ${light}%)`;
}

function getAccentColorForProduct(product) {
  const text = normalizeTextForSearch(
    [product.name, product.code, product.description].filter(Boolean).join(" ")
  );

  // Мята / ментол
  if (text.includes("мят") || text.includes("mint")) {
    return "#22c55e"; // ярко-мятный зелёный
  }

  // Клубника / клубничный
  if (text.includes("клубник") || text.includes("strawberry")) {
    return "#fb7185"; // клубнично-розовый
  }

  // Черника / ежевика / ягоды
  if (
    text.includes("черник") ||
    text.includes("ежевик") ||
    text.includes("ягод") ||
    text.includes("berry")
  ) {
    return "#6366f1"; // ягодный фиолетово-синий
  }

  // Лаванда / фиалка / цветочные
  if (
    text.includes("лаванд") ||
    text.includes("фиалк") ||
    text.includes("flower")
  ) {
    return "#a855f7"; // лавандовый
  }

  // Цитрусы: лимон, лайм, апельсин, грейпфрут
  if (
    text.includes("лимон") ||
    text.includes("лайм") ||
    text.includes("цитрус") ||
    text.includes("orange") ||
    text.includes("grapefruit") ||
    text.includes("citrus")
  ) {
    return "#facc15"; // жёлто-оранжевый цитрусовый
  }

  // Арбуз / дыня / тропики
  if (
    text.includes("арбуз") ||
    text.includes("дын") ||
    text.includes("melon") ||
    text.includes("tropical") ||
    text.includes("манго") ||
    text.includes("mango") ||
    text.includes("персик") ||
    text.includes("peach") ||
    text.includes("гуаява") ||
    text.includes("guava") ||
    text.includes("папая") ||
    text.includes("papaya")
  ) {
    return "#14b8a6"; // бирюзовый тропический / сочные фрукты
  }

  // Кремовые / ваниль / десерт
  if (
    text.includes("ванил") ||
    text.includes("сливоч") ||
    text.includes("десерт") ||
    text.includes("cream")
  ) {
    return "#f97316"; // тёплый кремовый оранжевый
  }

  // Чай / пряные
  if (text.includes("чай") || text.includes("tea") || text.includes("kashmir")) {
    return "#fb923c"; // тёплый пряный
  }

  // Яблоко / груша / виноград — мягкий фруктовый
  if (
    text.includes("яблок") ||
    text.includes("apple") ||
    text.includes("груш") ||
    text.includes("pear") ||
    text.includes("виноград") ||
    text.includes("grape")
  ) {
    return "#4ade80"; // мягкий зелёный фруктовый
  }

  // Фолбэк — хэш по коду, чтобы всё равно был стабильный цвет
  return getAccentColorFromCode(product.code || product.name);
}

// Грубый транслит EN -> RU для поиска по латинским названиям "на слух"
function translitEnToRuForSearch(text) {
  if (!text) return "";
  let s = String(text).toLowerCase();
  s = s
    .replace(/ch/g, "ч")
    .replace(/sh/g, "ш")
    .replace(/sch/g, "щ")
    .replace(/ya/g, "я")
    .replace(/yu/g, "ю")
    .replace(/yo/g, "ё")
    .replace(/ts/g, "ц")
    .replace(/tz/g, "ц")
    .replace(/th/g, "т")
    .replace(/ph/g, "ф")
    .replace(/ee/g, "и")
    .replace(/oo/g, "у");
  const map = {
    a: "а",
    b: "б",
    c: "к",
    d: "д",
    e: "е",
    f: "ф",
    g: "г",
    h: "х",
    i: "и",
    j: "дж",
    k: "к",
    l: "л",
    m: "м",
    n: "н",
    o: "о",
    p: "п",
    q: "к",
    r: "р",
    s: "с",
    t: "т",
    u: "у",
    v: "в",
    w: "в",
    x: "кс",
    y: "и",
    z: "з",
    "-": " ",
  };
  let out = "";
  for (let ch of s) {
    out += map[ch] || ch;
  }
  return out.replace(/\s+/g, " ").trim();
}

// Обратный грубый транслит RU -> EN, чтобы русский запрос мог
// находить латинские названия даже без явных русских слов в описании.
function translitRuToEnForSearch(text) {
  if (!text) return "";
  const map = {
    а: "a",
    б: "b",
    в: "v",
    г: "g",
    д: "d",
    е: "e",
    ё: "e",
    ж: "zh",
    з: "z",
    и: "i",
    й: "y",
    к: "k",
    л: "l",
    м: "m",
    н: "n",
    о: "o",
    п: "p",
    р: "r",
    с: "s",
    т: "t",
    у: "u",
    ф: "f",
    х: "h",
    ц: "ts",
    ч: "ch",
    ш: "sh",
    щ: "sch",
    ъ: "",
    ы: "y",
    ь: "",
    э: "e",
    ю: "yu",
    я: "ya",
  };
  let out = "";
  const src = String(text).toLowerCase();
  for (let i = 0; i < src.length; i++) {
    const ch = src[i];
    out += map[ch] !== undefined ? map[ch] : ch;
  }
  return out.replace(/\s+/g, " ").trim();
}

function productMatchesQuery(product, q) {
  if (!q) return true;
  const normQ = normalizeTextForSearch(q).trim();
  if (!normQ) return true;

  // если запрос совпадает с алиасом (точно или по вхождению) — матчим по имени
  const aliasTarget = resolveAliasTarget(normQ);
  if (aliasTarget) {
    // матчим, если имя содержит базовое название (чтобы ловить Cool Strawberry N, Pink и т.п.)
    const aliasNeedle = String(aliasTarget).toLowerCase();
    return [product.name, product.display_name_en, product.code]
      .filter(Boolean)
      .some((v) => String(v).toLowerCase().includes(aliasNeedle));
  }

  const hasCyr = /[а-я]/.test(normQ);
  const hasLat = /[a-z]/.test(normQ);

  let haystack = normalizeTextForSearch(
    [
      product.name,
      product.display_name_en,
      product.code,
      product.description,
      buildRuName(product),
    ]
      .filter(Boolean)
      .join(" ")
  );

  // если пользователь вводит по‑русски, добавляем грубый транслит латинских имён
  if (hasCyr) {
    const phon = translitEnToRuForSearch(
      `${product.name || ""} ${product.code || ""}`
    );
    if (phon) {
      haystack += " " + phon;
    }
    const qToEn = translitRuToEnForSearch(normQ);
    if (qToEn) {
      haystack += " " + normalizeTextForSearch(qToEn);
    }
  }

  // если пользователь вводит латиницей, добавляем грубый транслит
  // русских полей, чтобы "yagod" находило "ягодный" в описаниях.
  if (hasLat) {
    const ruToEn = translitRuToEnForSearch(
      `${product.description || ""} ${buildRuName(product) || ""}`
    );
    if (ruToEn) {
      haystack += " " + normalizeTextForSearch(ruToEn);
    }
  }

  const tokens = normQ.split(/\s+/).filter(Boolean);
  return tokens.every((token) => {
    // для русских слов делаем поиск по началу слова (общий корень),
    // чтобы "клубника" находила "клубничный", "мята" — "мятный" и т.п.
    const isCyr = /[а-я]/.test(token);
    let needle = token;
    if (isCyr && token.length >= 4) {
      // берём первые 4 буквы как общий корень
      needle = token.slice(0, 4);
    }
    if (haystack.includes(needle)) return true;
    // Допуск в 1 символ для средних/длинных слов,
    // чтобы переживать опечатки: "клубнка" -> "клубника".
    if (needle.length < 5) return false;
    const words = haystack.split(" ");
    for (const w of words) {
      if (Math.abs(w.length - needle.length) > 1) continue;
      let miss = 0;
      const max = Math.min(w.length, needle.length);
      for (let i = 0; i < max; i++) {
        if (w[i] !== needle[i]) {
          miss += 1;
          if (miss > 1) break;
        }
      }
      miss += Math.abs(w.length - needle.length);
      if (miss <= 1) return true;
    }
    return false;
  });
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
  const filtered = state.search
    ? state.products.filter((p) => productMatchesQuery(p, state.search))
    : state.products;

  const sorted = [...filtered].sort((a, b) =>
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
      const fullDesc = (p.description || "").trim();
      const ruName = buildRuName(p);

      // Убираем из описания расшифровку, чтобы не было дублей
      let bodyDesc = fullDesc;
      if (ruName && fullDesc) {
        const norm = (s) => String(s).replace(/\s+/g, " ").trim();
        const d = norm(fullDesc);
        const tag = norm(ruName);
        const lowerD = d.toLowerCase();
        const lowerTag = tag.toLowerCase();

        if (lowerD.startsWith(lowerTag)) {
          bodyDesc = d.slice(tag.length).trim().replace(/^[\s.,–—-]+/, "");
        } else {
          const sentEnd = d.search(/[.!?]/);
          if (sentEnd >= 0) {
            const firstSentence = d.slice(0, sentEnd).trim();
            if (firstSentence.toLowerCase() === lowerTag) {
              bodyDesc = d.slice(sentEnd + 1).trim().replace(/^[\s]+/, "");
            }
          }
        }
      }

      const desc = bodyDesc ? shortenDescription(bodyDesc, 110) : "";
      const card = document.createElement("div");
      card.className = "product-card";
      const accentColor = getAccentColorForProduct(p);
      card.style.setProperty("--accent-color", accentColor);
      card.classList.add("product-card--accent");
      card.innerHTML = `
        <div class="product-card__name">
          <span class="product-card__name-en">${escapeHtml(p.name)}</span>
          ${
            ruName
              ? `<span class="product-card__name-ru">${escapeHtml(ruName)}</span>`
              : ""
          }
        </div>
        ${desc ? `<div class="product-card__desc">${escapeHtml(desc)}</div>` : ""}
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
}

function sellerPlayAddToCartAnimation(product, cardEl) {
  if (!cardEl || !product) return;
  const targetFloatingRight = document.querySelector(
    "#seller-floating-summary .seller-floating-summary__right"
  );
  const targetFloating = document.getElementById("seller-floating-summary");
  const targetCart = document.querySelector(".seller__cart");
  const targetEl = targetFloatingRight || targetFloating || targetCart;
  if (!targetEl) return;

  const cardRect = cardEl.getBoundingClientRect();
  const targetRect = targetEl.getBoundingClientRect();

  // Летит именно упаковка, как в киоске (с фолбэком по имени файла)
  const fly = document.createElement("div");
  fly.classList.add("kiosk-pack-fly");
  const img = document.createElement("img");
  img.className = "kiosk-pack-img";
  const candidates = sellerGetImageCandidates(product);
  img.src = (candidates && candidates[0]) || sellerGetImageUrl(product);
  img.alt = product.name || "";
  fly.appendChild(img);

  if (img && candidates && candidates.length > 1) {
    let idx = 0;
    img.onerror = () => {
      idx += 1;
      if (idx < candidates.length) {
        img.src = candidates[idx];
      } else {
        img.style.display = "none";
      }
    };
  }

  const baseWidth = Math.min(cardRect.width, 180);
  const baseHeight = baseWidth * 1.4;

  fly.style.left = `${cardRect.left + cardRect.width / 2 - baseWidth / 2}px`;
  fly.style.top = `${cardRect.top + cardRect.height / 2 - baseHeight / 2}px`;
  fly.style.width = `${baseWidth}px`;
  fly.style.height = `${baseHeight}px`;
  fly.style.transform = "translate(0, 0) scale(1.08) rotate(0deg)";
  fly.style.opacity = "1";

  document.body.appendChild(fly);

  const translateX =
    targetRect.left +
    targetRect.width / 2 -
    (cardRect.left + cardRect.width / 2);
  const translateY =
    targetRect.top +
    targetRect.height / 2 -
    (cardRect.top + cardRect.height / 2);

  requestAnimationFrame(() => {
    fly.style.transform = `translate(${translateX}px, ${translateY}px) scale(0.22) rotate(12deg)`;
    fly.style.opacity = "0";
  });

  const removeAfter = () => {
    if (fly && fly.parentNode) {
      fly.parentNode.removeChild(fly);
    }
  };

  fly.addEventListener("transitionend", removeAfter, { once: true });
  setTimeout(removeAfter, 1200);
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
  if (delta > 0) {
    const btn = document.querySelector(
      `.qty-btn[data-role="inc"][data-id="${productId}"]`
    );
    const card = btn ? btn.closest(".product-card") : null;
    if (card) {
      sellerPlayAddToCartAnimation(product, card);
    }
  }
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
  msgEl.textContent = "Отправляем заказ…";
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
      throw new Error(data.detail || "Не получилось создать заказ, попробуйте ещё раз.");
    }

    const data = await res.json().catch(() => ({}));
    const orderId = data && typeof data.id === "number" ? data.id : null;

    Object.keys(state.cart).forEach((k) => delete state.cart[k]);
    await fetchProducts();

    msgEl.textContent = "";
    msgEl.className = "cart-message";
    if (orderId != null) {
      showOrderToast(orderId);
    }
  } catch (e) {
    console.error(e);
    msgEl.textContent =
      e && e.message
        ? e.message
        : "Не получилось создать заказ. Попросите бармена помочь — быстро всё решим.";
    msgEl.className = "cart-message cart-message--error";
  } finally {
    btn.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fetchProducts();

  const searchInput = document.getElementById("seller-search");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const value = e.target.value || "";
      state.search = value;
      renderProducts();
    });
  }

  const products = document.getElementById("products");
  if (products && !productsClickBound) {
    productsClickBound = true;
    products.addEventListener("click", (e) => {
      const btn = e.target;
      if (!btn || !btn.dataset || !btn.dataset.role) return;
      const id = parseInt(btn.dataset.id, 10);
      if (!Number.isFinite(id)) return;

      const card = btn.closest(".product-card");
      if (card) {
        card.classList.remove("product-card--flash");
        // force reflow, чтобы анимация могла переиграть
        void card.offsetWidth;
        card.classList.add("product-card--flash");
      }
      btn.classList.add("qty-btn--bump");
      setTimeout(() => btn.classList.remove("qty-btn--bump"), 160);

      if (btn.dataset.role === "inc") {
        addToCart(id, 1);
      } else if (btn.dataset.role === "dec") {
        addToCart(id, -1);
      }
    });
  }

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

