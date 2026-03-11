const kioskState = {
  products: [],
  cart: window.posCart || (window.posCart = {}), // общая корзина с простым меню
  activeIndex: 0,
};

const KIOSK_RU_TAG_OVERRIDES = {
  "2005 Blueberry": "Черничный кекс",
  "Blackberry Lime": "Ежевика и лайм",
  Blitzsturm: "Лаванда и мята",
  "Cane Mint": "Мятные леденцы",
  Horchata: "Орчата, рисовый напиток",
  "Cool Strawberry": "Засахаренная клубника",
};

// Костыль для фирменных надписей (лого-вкусов)
// Для Adalya используем готовые арты пачек,
// лежащие в /static/img/labels/
const kioskLabelImages = {
  // Коды товаров (product.code) → файл с картинкой пачки Adalya
  "ledy_killer": "/static/img/labels/ledy_killer.png",
  "ledy_banan_milk": "/static/img/labels/ledy_banan_milk.png",
  moloko: "/static/img/labels/moloko.png",
  karamel: "/static/img/labels/karamel.png",
  love66: "/static/img/labels/love66.png",
  citrus_mix: "/static/img/labels/citrus_mix.png",
  kaktus: "/static/img/labels/kaktus.png",
  lemon_pie: "/static/img/labels/lemon_pie.png",
};

// Дополнительный декор / фон для ароматов — для Adalya делаем свои фоны
const kioskAromaMeta = {
  ledy_killer: {
    bgClass: "kiosk-bg--adalya-ledy-killer",
  },
  ledy_banan_milk: {
    bgClass: "kiosk-bg--adalya-banana-ice",
  },
  moloko: {
    bgClass: "kiosk-bg--adalya-milk",
  },
  karamel: {
    bgClass: "kiosk-bg--adalya-caramel",
  },
  love66: {
    bgClass: "kiosk-bg--adalya-love66",
  },
  citrus_mix: {
    bgClass: "kiosk-bg--adalya-citrus-mix",
  },
  kaktus: {
    bgClass: "kiosk-bg--adalya-cactus",
  },
  // Lemon Pie — поддерживаем несколько вариантов кода
  lemon_pie: {
    bgClass: "kiosk-bg--adalya-lemon-pie",
  },
  "lemon-pie": {
    bgClass: "kiosk-bg--adalya-lemon-pie",
  },
  "Lemon pie": {
    bgClass: "kiosk-bg--adalya-lemon-pie",
  },
};

// Категории вкусов по фону (Сладкий / Кислый / Пряный / Свежий)
// Можно тонко подстроить под реальные ощущения от ароматов.
const kioskCategoriesByBg = {};

// Цвет текста описания — светлый на тёмной базе фонов (#020617)
// Все фоны: тёмные полосы + цветные градиенты → светлый текст читается везде
const kioskLabelColorByBg = {};

function kioskPlayAddToCartAnimation() {
  const slidesContainer = document.getElementById("kiosk-slides");
  if (!slidesContainer) return;
  const activeImg = slidesContainer.querySelector(
    ".kiosk-slide--active .kiosk-pack-img"
  );
  if (!activeImg) return;

  const cartBar = document.getElementById("kiosk-bottom-bar");
  const cartBtn = document.getElementById("kiosk-open-cart");
  const targetEl = cartBtn || cartBar;
  if (!targetEl) return;

  const imgRect = activeImg.getBoundingClientRect();
  const targetRect = targetEl.getBoundingClientRect();

  const fly = activeImg.cloneNode(true);
  fly.classList.add("kiosk-pack-fly");
  fly.style.left = `${imgRect.left}px`;
  fly.style.top = `${imgRect.top}px`;
  fly.style.width = `${imgRect.width}px`;
  fly.style.height = `${imgRect.height}px`;
  fly.style.transform = "translate(0, 0) scale(1.08) rotate(0deg)";
  fly.style.opacity = "1";

  document.body.appendChild(fly);

  const translateX =
    targetRect.left + targetRect.width / 2 - (imgRect.left + imgRect.width / 2);
  const translateY =
    targetRect.top + targetRect.height / 2 - (imgRect.top + imgRect.height / 2);

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
  setTimeout(removeAfter, 1500);
}

let kioskScrollInitialized = false;
let kioskHaloScrollInitialized = false;
let kioskLastChangeAt = 0;
let kioskHaloLastChangeAt = 0;
let kioskLastDeltaSign = 0;

function kioskSetActiveIndex(nextIndex) {
  if (!kioskState.products.length) return;
  const total = kioskState.products.length;
  let idx = ((nextIndex % total) + total) % total;
  if (idx === kioskState.activeIndex) return;
  const prevIdx = kioskState.activeIndex;
  const delta = nextIndex - prevIdx;
  if (delta !== 0) kioskState.lastDirection = delta > 0 ? 1 : -1;
  kioskState.activeIndex = idx;
  kioskUpdateActiveStack();
}

function kioskChangeByDelta(delta) {
  if (!kioskState.products.length) return;
  const now = Date.now();
  const sign = delta > 0 ? 1 : -1;
  // сильно «притупляем» реакцию:
  // один жест пальца = максимум один шаг примерно раз в 700мс
  if (now - kioskLastChangeAt < 700 && sign === kioskLastDeltaSign) return;

  kioskLastChangeAt = now;
  kioskLastDeltaSign = sign;
  kioskSetActiveIndex(kioskState.activeIndex + sign);
}

function kioskGetImageUrl(product) {
  // Для Adalya всегда используем фирменные пачки из /static/img/labels/
  if (!product || !product.code) return "/static/img/placeholder-pack.png";
  const code = String(product.code);
  const fromMap =
    kioskLabelImages[code] || kioskLabelImages[code.toLowerCase()] || null;
  if (fromMap) return fromMap;
  return "/static/img/placeholder-pack.png";
}

async function kioskFetchProducts() {
  try {
    const res = await fetch("/api/products");
  if (!res.ok) {
    console.error("Ошибка загрузки товаров");
    return;
  }
    const data = await res.json();
    // сортируем пачки по имени, чтобы иерархия была логичной
    kioskState.products = data.sort((a, b) =>
      (a.name || "").localeCompare(b.name || "", "ru")
    );
    kioskState.activeIndex = 0;
    kioskRenderSlides();
    kioskRenderSummary();
  } catch (e) {
    console.error(e);
  }
}

function kioskRenderSlides() {
  const container = document.getElementById("kiosk-slides");
  container.innerHTML = "";
  kioskState.products.forEach((p) => {
    const slide = document.createElement("section");
    slide.className = "kiosk-slide";
    const aromaMeta = p.code ? kioskAromaMeta[p.code] : undefined;
    if (aromaMeta) {
      slide.classList.add("kiosk-aroma", aromaMeta.themeClass);
    }
    slide.innerHTML = `
      <div class="kiosk-slide-inner">
        <div class="kiosk-slide-main">
          <div class="kiosk-pack-visual">
            <img class="kiosk-pack-img" src="${kioskGetImageUrl(
              p
            )}" alt="${(p.name || "").replace(/"/g, "&quot;")}" />
          </div>
        </div>
      </div>
    `;
    container.appendChild(slide);
  });

  if (!kioskScrollInitialized) {
    // Управление сменой активной пачки как «кассет на полке»
    let touchStartY = null;
    let touchStartX = null;
    let touchLastY = null;
    let touchSide = "left"; // "left" | "right"

    container.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        const midX = window.innerWidth / 2;
        const isRight = e.clientX >= midX;
        const delta = e.deltaY;
        if (!isRight) {
          // левая половина экрана — обычный, но сильно замедленный скролл
          if (Math.abs(delta) < 80) return;
          kioskChangeByDelta(delta > 0 ? 1 : -1);
        } else {
          // правая половина — «колесо»: тоже с большим порогом
          if (Math.abs(delta) < 80) return;
          const now = Date.now();
          if (now - kioskHaloLastChangeAt < 700) return;
          kioskHaloLastChangeAt = now;
          const direction = delta > 0 ? 1 : -1;
          kioskSetActiveIndex(kioskState.activeIndex + direction);
        }
      },
      { passive: false }
    );

    container.addEventListener(
      "touchstart",
      (e) => {
        if (e.touches.length !== 1) return;
        const t = e.touches[0];
        touchStartY = t.clientY;
        touchLastY = t.clientY;
        touchStartX = t.clientX;
        const midX = window.innerWidth / 2;
        touchSide = t.clientX >= midX ? "right" : "left";
      },
      { passive: true }
    );

    container.addEventListener(
      "touchmove",
      (e) => {
        if (touchStartY == null) return;
        if (touchSide !== "right") return;
        const t = e.touches[0];
        const y = t.clientY;
        if (touchLastY == null) {
          touchLastY = y;
          return;
        }
        const diff = y - touchLastY;
        const step = 150; // компромисс: нужно уверенное, но не гигантское движение
        if (Math.abs(diff) < step) return;
        const now = Date.now();
        if (now - kioskHaloLastChangeAt < 650) return;
        kioskHaloLastChangeAt = now;
        const direction = diff < 0 ? 1 : -1;
        kioskSetActiveIndex(kioskState.activeIndex + direction);
        touchLastY = y;
      },
      { passive: true }
    );

    container.addEventListener(
      "touchend",
      (e) => {
        if (touchStartY == null) return;
        const endY = e.changedTouches[0].clientY;
        const diff = endY - touchStartY;
        const threshold = 90; // по центральной пачке — только длинный, осознанный свайп

        if (touchSide === "left") {
          // левая половина — обычный свайп по пачке
          touchStartY = null;
          touchLastY = null;
          if (Math.abs(diff) < threshold) return;
          // свайп вверх – следующая пачка, вниз – предыдущая
          kioskChangeByDelta(diff < 0 ? 1 : -1);
        } else {
          // правая половина — завершаем жест быстрой прокрутки
          touchStartY = null;
          touchLastY = null;
        }
      },
      { passive: true }
    );

    window.addEventListener("resize", kioskUpdateActiveStack);

    kioskScrollInitialized = true;
  }

  kioskUpdateActiveStack();
}

function kioskApplyAromaBackground() {
  const root = document.getElementById("kiosk-root");
  if (!root) return;
  const products = kioskState.products;
  if (!products.length) {
    root.className = "kiosk";
    return;
  }
  const total = products.length;
  let idx = kioskState.activeIndex;
  idx = ((idx % total) + total) % total;
  const active = products[idx];
  const meta = active && active.code ? kioskAromaMeta[active.code] : undefined;

  // базовый класс
  root.className = "kiosk";
  if (meta && meta.bgClass) {
    root.classList.add("kiosk-bg", meta.bgClass);
  }

  // маскот слева — только для выбранных ароматов
  const code = active && active.code ? String(active.code).toLowerCase() : "";
  const showMascot =
    code === "karamel" ||
    code === "lemon_pie" ||
    code === "lemon-pie" ||
    code === "lemon pie";
  root.classList.toggle("kiosk--mascot-left", showMascot);
}

function kioskChangeQty(productId, delta) {
  const product = kioskState.products.find((p) => p.id === productId);
  if (!product) return;
  const current = kioskState.cart[productId] || 0;
  let next = current + delta;
  if (next < 0) next = 0;
  if (next > product.quantity) next = product.quantity;

  if (next === 0) {
    delete kioskState.cart[productId];
  } else {
    kioskState.cart[productId] = next;
  }

  kioskRenderSlides();
  kioskRenderSummary();
}

function kioskUpdateActiveStack() {
  const container = document.getElementById("kiosk-slides");
  const slides = Array.from(container.querySelectorAll(".kiosk-slide"));
  if (!slides.length) return;

  const total = slides.length;
  // нормализуем индекс в диапазон [0, total)
  let activeIndex = kioskState.activeIndex;
  activeIndex = ((activeIndex % total) + total) % total;

  const direction = kioskState.lastDirection || 1;

  slides.forEach((slide, index) => {
    slide.className = "kiosk-slide";
    slide.style.pointerEvents = "none";

    if (index === activeIndex) {
      // активная пачка — едет в центр как поезд
      slide.classList.add("kiosk-slide--active");
      slide.style.pointerEvents = "auto";

      // сбрасываем прошлую анимацию
      slide.classList.remove(
        "kiosk-slide--enter-from-left",
        "kiosk-slide--enter-from-right"
      );
      // форсируем reflow, чтобы анимация могла переиграть
      void slide.offsetWidth;

      slide.classList.add(
        direction >= 0
          ? "kiosk-slide--enter-from-left"
          : "kiosk-slide--enter-from-right"
      );
    }
  });

  kioskApplyAromaBackground();
  kioskUpdateAromaHalo();
  kioskUpdateDescription();
}

function kioskEscape(s) {
  if (!s) return "";
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

function kioskUpdateDescription() {
  const el = document.getElementById("kiosk-description");
  if (!el) return;
  // В Adalya не показываем названия и описания — только пачки
  el.innerHTML = "";
  el.style.display = "none";
}

function kioskUpdateAromaHalo() {
  const halo = document.getElementById("kiosk-aroma-halo");
  if (!halo) return;
  halo.style.pointerEvents = "auto";
  const itemsRoot =
    document.getElementById("kiosk-aroma-halo-items") || halo;
  const products = kioskState.products;
  if (!products.length) {
    itemsRoot.innerHTML = "";
    return;
  }

  const total = products.length;
  let activeIndex = kioskState.activeIndex;
  activeIndex = ((activeIndex % total) + total) % total;

  // показываем три аромата: предыдущий, текущий и следующий
  const offsets = [-1, 0, 1];
  const roles = ["prev", "current", "next"];

  itemsRoot.innerHTML = "";

  // расставляем подписи по дуге вокруг центра halo
  const isMobile = window.innerWidth <= 640;
  const radius = isMobile ? 56 : 70;
  const anglesDeg = [-40, 0, 40]; // градусы для трёх позиций

  offsets.forEach((offset, i) => {
    if (total < 2 && offset !== 0) return;
    let idx = activeIndex + offset;
    idx = ((idx % total) + total) % total;
    const p = products[idx];
    const el = document.createElement("div");
    el.className = `kiosk-aroma-halo__item kiosk-aroma-halo__item--${roles[i]}`;
    // базовое позиционирование в центре контейнера, дальше сдвиг по кругу
    el.style.left = "50%";
    el.style.top = "50%";
    const angleRad = (anglesDeg[i] * Math.PI) / 180;
    const x = Math.cos(angleRad) * radius;
    const y = Math.sin(angleRad) * radius;
    // сдвигаем дугу ближе к правому краю
    const horizontalShift = isMobile ? 64 : 76;
    el.style.transform = `translate(${x + horizontalShift}px, ${y}px)`;
    const code = p.code ? String(p.code) : "";
    const labelSrc =
      code && (kioskLabelImages[code] || kioskLabelImages[code.toLowerCase()])
        ? kioskLabelImages[code] || kioskLabelImages[code.toLowerCase()]
        : undefined;
    const safeName = p.name || p.code || "";
    const labelHtml = labelSrc
      ? `
          <img
            src="${labelSrc}"
            alt="${safeName}"
            class="kiosk-aroma-label-img"
            onerror="this.style.display='none'; this.nextElementSibling.style.display='inline-block';"
          />
          <span class="kiosk-aroma-halo__item-label" style="display: none;">
            ${safeName}
          </span>
        `
      : `<span class="kiosk-aroma-halo__item-label">${safeName}</span>`;

    el.innerHTML = `
      <span class="kiosk-aroma-halo__tick"></span>
      ${labelHtml}
    `;
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      kioskSetActiveIndex(idx);
    });
    itemsRoot.appendChild(el);
  });

  if (!kioskHaloScrollInitialized) {
    let touchStartY = null;
    let lastY = null;

    halo.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        if (Math.abs(e.deltaY) < 40) return;
        const now = Date.now();
        if (now - kioskHaloLastChangeAt < 400) return;
        kioskHaloLastChangeAt = now;
        const direction = e.deltaY > 0 ? 1 : -1;
        kioskSetActiveIndex(kioskState.activeIndex + direction);
      },
      { passive: false }
    );

    halo.addEventListener(
      "touchstart",
      (e) => {
        if (e.touches.length !== 1) return;
        touchStartY = e.touches[0].clientY;
        lastY = touchStartY;
      },
      { passive: true }
    );

    halo.addEventListener(
      "touchmove",
      (e) => {
        if (touchStartY == null) return;
        const y = e.touches[0].clientY;
        if (lastY == null) {
          lastY = y;
          return;
        }
        const diff = y - lastY;
        const step = 150; // колесу тоже даём «среднюю» чувствительность
        if (Math.abs(diff) < step) return;
        const now = Date.now();
        if (now - kioskHaloLastChangeAt < 650) return;
        kioskHaloLastChangeAt = now;
        const direction = diff < 0 ? 1 : -1;
        kioskSetActiveIndex(kioskState.activeIndex + direction);
        lastY = y;
      },
      { passive: true }
    );

    halo.addEventListener(
      "touchend",
      () => {
        touchStartY = null;
        lastY = null;
      },
      { passive: true }
    );

    kioskHaloScrollInitialized = true;
  }
}

function kioskRenderSummary() {
  const entries = Object.entries(kioskState.cart);
  const summaryText = document.getElementById("kiosk-summary-text");
  const openBtn = document.getElementById("kiosk-open-cart");

  if (!entries.length) {
    summaryText.textContent = "Корзина пуста";
    openBtn.disabled = true;
    kioskRenderCart();
    return;
  }

  let totalQty = 0;
  let totalAmount = 0;
  entries.forEach(([idStr, qty]) => {
    const id = parseInt(idStr, 10);
    const product = kioskState.products.find((p) => p.id === id);
    if (!product) return;
    totalQty += qty;
    totalAmount += product.price * qty;
  });

  summaryText.textContent = `Вы выбрали ${totalQty} шт. на ${totalAmount.toFixed(
    0
  )} ₽`;
  openBtn.disabled = false;
  kioskRenderCart();
}

function kioskRenderCart() {
  const itemsEl = document.getElementById("kiosk-cart-items");
  const emptyEl = document.getElementById("kiosk-cart-empty");
  const totalEl = document.getElementById("kiosk-cart-total");
  const submitBtn = document.getElementById("kiosk-submit-order");

  itemsEl.innerHTML = "";

  const entries = Object.entries(kioskState.cart);
  if (!entries.length) {
    emptyEl.style.display = "block";
    submitBtn.disabled = true;
    totalEl.textContent = "0 ₽";
    return;
  }

  emptyEl.style.display = "none";
  let totalAmount = 0;

  entries.forEach(([idStr, qty]) => {
    const id = parseInt(idStr, 10);
    const product = kioskState.products.find((p) => p.id === id);
    if (!product) return;
    const lineAmount = product.price * qty;
    totalAmount += lineAmount;
    const li = document.createElement("li");
    li.className = "kiosk-cart-item";
    li.innerHTML = `
      <div>
        <div class="kiosk-cart-item-name">${product.name}</div>
        <div class="kiosk-cart-item-meta">${qty} × ${product.price.toFixed(
          0
        )} ₽</div>
      </div>
      <div class="kiosk-cart-item-amount">${lineAmount.toFixed(0)} ₽</div>
    `;
    itemsEl.appendChild(li);
  });

  totalEl.textContent = `${totalAmount.toFixed(0)} ₽`;
  submitBtn.disabled = false;
}

function kioskOpenCart() {
  document.getElementById("kiosk-cart-overlay").classList.add("is-open");
  const fab = document.getElementById("kiosk-add-active");
  if (fab) {
    fab.classList.add("kiosk-fab-global--hidden");
  }
}

function kioskCloseCart() {
  document.getElementById("kiosk-cart-overlay").classList.remove("is-open");
  const fab = document.getElementById("kiosk-add-active");
  if (fab) {
    fab.classList.remove("kiosk-fab-global--hidden");
  }
}

async function kioskSubmitOrder() {
  const entries = Object.entries(kioskState.cart);
  if (!entries.length) return;

  const items = entries.map(([idStr, qty]) => ({
    product_id: parseInt(idStr, 10),
    quantity: qty,
  }));

  const msgEl = document.getElementById("kiosk-cart-message");
  const btn = document.getElementById("kiosk-submit-order");
  btn.disabled = true;
  msgEl.textContent = "Отправляем заказ…";
  msgEl.className = "kiosk-cart-message";

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
      throw new Error(
        data.detail || "Не получилось создать заказ, попробуйте ещё раз."
      );
    }

    const data = await res.json().catch(() => ({}));
    const orderId = data && typeof data.id === "number" ? data.id : null;

    Object.keys(kioskState.cart).forEach((k) => delete kioskState.cart[k]);
    await kioskFetchProducts();
    kioskCloseCart();

    const summaryText = document.getElementById("kiosk-summary-text");
    summaryText.textContent = "Заказ отправлен, подойдите к стойке";
    if (orderId != null && typeof showOrderToast === "function") {
      showOrderToast(orderId);
    }
  } catch (e) {
    console.error(e);
    msgEl.textContent =
      e && e.message
        ? e.message
        : "Не получилось создать заказ. Позовите бармена — он поможет.";
    msgEl.className = "kiosk-cart-message kiosk-cart-message--error";
  } finally {
    btn.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  kioskFetchProducts();

  const addActiveBtn = document.getElementById("kiosk-add-active");
  if (addActiveBtn) {
    let fabToastTimer = null;

    addActiveBtn.addEventListener("click", () => {
      const products = kioskState.products;
      if (!products.length) return;
      const total = products.length;
      let idx = kioskState.activeIndex;
      idx = ((idx % total) + total) % total;
      const active = products[idx];
      kioskChangeQty(active.id, 1);

      // мини-подсказка "+ <название> в корзине"
      let toast = document.getElementById("kiosk-fab-toast");
      if (!toast) {
        toast = document.createElement("div");
        toast.id = "kiosk-fab-toast";
        toast.className = "kiosk-fab-toast";
        document.body.appendChild(toast);
      }
      const label = active.name || active.code || "пачка";
      const meta =
        active && active.code ? kioskAromaMeta[active.code] : undefined;
      let nameColor = "#facc15";
      if (meta && meta.bgClass && kioskLabelColorByBg[meta.bgClass]) {
        nameColor = kioskLabelColorByBg[meta.bgClass];
      }
      toast.innerHTML = `+ <span style="color:${nameColor}">${label}</span> в корзине`;
      toast.classList.add("kiosk-fab-toast--visible");

      if (fabToastTimer) clearTimeout(fabToastTimer);
      fabToastTimer = setTimeout(() => {
        toast.classList.remove("kiosk-fab-toast--visible");
      }, 1200);

      // анимация «пачка летит в корзину»
      kioskPlayAddToCartAnimation();
    });
  }

  const upBtn = document.getElementById("kiosk-flavor-up");
  const downBtn = document.getElementById("kiosk-flavor-down");
  if (upBtn) {
    upBtn.addEventListener("click", () => kioskChangeByDelta(-1));
  }
  if (downBtn) {
    downBtn.addEventListener("click", () => kioskChangeByDelta(1));
  }

  document
    .getElementById("kiosk-open-cart")
    .addEventListener("click", kioskOpenCart);
  document
    .getElementById("kiosk-close-cart")
    .addEventListener("click", kioskCloseCart);
  document
    .getElementById("kiosk-cart-overlay")
    .addEventListener("click", (e) => {
      if (e.target.id === "kiosk-cart-overlay") {
        kioskCloseCart();
      }
    });
  document
    .getElementById("kiosk-submit-order")
    .addEventListener("click", kioskSubmitOrder);
});


