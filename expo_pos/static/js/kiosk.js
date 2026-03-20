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
// Ожидаем картинки с чёрным текстом на белом фоне,
// лежащие в /static/img/labels/
const kioskLabelImages = {
  "2005-blueberry": "/static/img/labels/2005-blueberry.png",
  // сюда позже можно добавить остальные вкусы
};

// Дополнительный декор / фон для ароматов — через фон вокруг пачки
const kioskAromaMeta = {
  // индивидуальные, уже настроенные ароматы
  mimon: {
    themeClass: "kiosk-aroma--mimon",
    bgClass: "kiosk-bg--mimon",
  },
  "mixed-fruit": {
    themeClass: "kiosk-aroma--mixed-fruit",
    bgClass: "kiosk-bg--mixed-fruit",
  },
  nectarine: {
    themeClass: "kiosk-aroma--nectarine",
    bgClass: "kiosk-bg--nectarine",
  },
  // кастомные арты по твоим примерам
  "blackberry-lime": {
    bgClass: "kiosk-bg--blackberry-lime",
  },
  blitzsturm: {
    bgClass: "kiosk-bg--blitzsturm",
  },

  // группы фонов на основе расшифровки ароматов
  // яркие цитрусы
  sunrise: {
    bgClass: "kiosk-bg--citrus-bright",
  },
  "orange-soda": {
    bgClass: "kiosk-bg--citrus-bright",
  },
  "double-orange": {
    bgClass: "kiosk-bg--citrus-bright",
  },
  "lemon-lime": {
    bgClass: "kiosk-bg--citrus-bright",
  },
  "passionfruit-lemonade": {
    bgClass: "kiosk-bg--citrus-bright",
  },
  "strawberry-lemonade": {
    bgClass: "kiosk-bg--citrus-berry",
  },
  "pink-grapefruit": {
    bgClass: "kiosk-bg--citrus-bright",
  },
  sunset: {
    bgClass: "kiosk-bg--citrus-bright",
  },
  "rangoon-sunrise": {
    bgClass: "kiosk-bg--citrus-bright",
  },

  // ягоды / миксы
  "2005-blueberry": {
    bgClass: "kiosk-bg--berry-deep",
  },
  brambleberry: {
    bgClass: "kiosk-bg--berry-deep",
  },
  schnozzberry: {
    bgClass: "kiosk-bg--berry-deep",
  },
  strawberry: {
    bgClass: "kiosk-bg--berry-deep",
  },
  "cool-strawberry-n": {
    bgClass: "kiosk-bg--berry-deep",
  },
  "cool-strawberry-pink": {
    bgClass: "kiosk-bg--berry-deep",
  },

  // тропики / сочные фрукты
  "erics-mango": {
    bgClass: "kiosk-bg--erics-mango",
  },
  "melon-blend": {
    bgClass: "kiosk-bg--melon-blend",
  },
  "juicy-peach": {
    bgClass: "kiosk-bg--juicy-peach",
  },
  "kashmir-peach": {
    bgClass: "kiosk-bg--kashmir-peach",
  },
  "kashmir-guajava": {
    bgClass: "kiosk-bg--kashmir-guajava",
  },
  "guajava-kiss": {
    bgClass: "kiosk-bg--guajava-kiss",
  },
  "maraschino-cherry": {
    bgClass: "kiosk-bg--maraschino-cherry",
  },
  pineapple: {
    bgClass: "kiosk-bg--pineapple",
  },
  "papaya-sorbet": {
    bgClass: "kiosk-bg--papaya-sorbet",
  },
  watermelon: {
    bgClass: "kiosk-bg--watermelon",
  },
  "sour-watermelon": {
    bgClass: "kiosk-bg--sour-watermelon",
  },
  "tropical-punch": {
    bgClass: "kiosk-bg--tropical-punch",
  },
  "tropical-revenge": {
    bgClass: "kiosk-bg--tropical-revenge",
  },
  "surfers-delight": {
    bgClass: "kiosk-bg--surfers-delight",
  },

  // мята / травы / лаванда
  wintergreen: {
    bgClass: "kiosk-bg--wintergreen",
  },
  "cane-mint": {
    bgClass: "kiosk-bg--cane-mint",
  },
  "cucumber-lavender": {
    bgClass: "kiosk-bg--cucumber-lavender",
  },

  // чай / сливочные десерты
  horchata: {
    bgClass: "kiosk-bg--dessert-creamy",
  },
  "welsh-cream": {
    bgClass: "kiosk-bg--dessert-creamy",
  },
  "its-like-that-one-breakfast-cereal": {
    bgClass: "kiosk-bg--dessert-creamy",
  },
  "papas-foreplay": {
    bgClass: "kiosk-bg--dessert-creamy",
  },
  "peach-iced-tea": {
    bgClass: "kiosk-bg--tea-aromatic",
  },
  "prince-of-gray": {
    bgClass: "kiosk-bg--tea-aromatic",
  },

  // пряные / кашмир
  "kashmir-black": {
    bgClass: "kiosk-bg--kashmir-black",
  },
  kashmir: {
    bgClass: "kiosk-bg--kashmir",
  },
  "kashmir-apple": {
    bgClass: "kiosk-bg--kashmir-apple",
  },
  "kashmir-mango": {
    bgClass: "kiosk-bg--kashmir-mango",
  },
  "kashmir-cherry": {
    bgClass: "kiosk-bg--kashmir-cherry",
  },

  // статик / прочие «космические»
  "static-starlight": {
    bgClass: "kiosk-bg--cosmic-dark",
  },
  "static-starlight-noir": {
    bgClass: "kiosk-bg--cosmic-dark",
  },
  pinepas: {
    bgClass: "kiosk-bg--cosmic-dark",
  },

  // экзотические / сложные
  ololiuqui: {
    bgClass: "kiosk-bg--exotic-dark",
  },
  "im-coming-to-get-you-varvara": {
    bgClass: "kiosk-bg--exotic-dark",
  },
};

// Категории вкусов по фону (Сладкий / Кислый / Пряный / Свежий)
// Можно тонко подстроить под реальные ощущения от ароматов.
const kioskCategoriesByBg = {
  // яркие цитрусы, лимонады
  "kiosk-bg--citrus-bright": ["Сладкий", "Кислый"],
  "kiosk-bg--citrus-berry": ["Сладкий", "Кислый"],

  // ягоды
  "kiosk-bg--berry-deep": ["Сладкий"],

  // тропики, манго, персики и т.п.
  "kiosk-bg--erics-mango": ["Сладкий"],
  "kiosk-bg--melon-blend": ["Сладкий", "Свежий"],
  "kiosk-bg--juicy-peach": ["Сладкий"],
  "kiosk-bg--kashmir-peach": ["Сладкий", "Пряный"],
  "kiosk-bg--kashmir-guajava": ["Сладкий", "Пряный"],
  "kiosk-bg--guajava-kiss": ["Сладкий"],
  "kiosk-bg--pineapple": ["Сладкий", "Кислый"],
  "kiosk-bg--papaya-sorbet": ["Сладкий"],
  "kiosk-bg--watermelon": ["Сладкий"],
  "kiosk-bg--sour-watermelon": ["Сладкий", "Кислый"],
  "kiosk-bg--tropical-punch": ["Сладкий"],
  "kiosk-bg--tropical-revenge": ["Сладкий"],
  "kiosk-bg--surfers-delight": ["Сладкий", "Свежий"],

  // мята / травы / свежие
  "kiosk-bg--wintergreen": ["Свежий"],
  "kiosk-bg--cane-mint": ["Свежий"],
  "kiosk-bg--cucumber-lavender": ["Свежий"],
  "kiosk-bg--mint-herbal": ["Свежий"],

  // десерты / сливочные
  "kiosk-bg--dessert-creamy": ["Сладкий"],

  // чай
  "kiosk-bg--tea-aromatic": ["Свежий", "Сладкий"],

  // кашмир / пряные
  "kiosk-bg--kashmir-black": ["Пряный"],
  "kiosk-bg--kashmir": ["Пряный"],
  "kiosk-bg--kashmir-apple": ["Пряный", "Сладкий"],
  "kiosk-bg--kashmir-mango": ["Пряный", "Сладкий"],
  "kiosk-bg--kashmir-cherry": ["Пряный", "Сладкий"],
  "kiosk-bg--spice-kashmir": ["Пряный"],

  // космос / сложные
  "kiosk-bg--cosmic-dark": ["Сладкий", "Свежий"],
  "kiosk-bg--exotic-dark": ["Сладкий", "Пряный"],

  // индивидуальные арты
  "kiosk-bg--mimon": ["Сладкий", "Кислый"],
  "kiosk-bg--mixed-fruit": ["Сладкий", "Кислый"],
  "kiosk-bg--nectarine": ["Сладкий", "Кислый"],
  "kiosk-bg--blackberry-lime": ["Сладкий", "Кислый"],
  "kiosk-bg--blitzsturm": ["Свежий", "Пряный"],
  "kiosk-bg--maraschino-cherry": ["Сладкий", "Пряный"],
};

// Цвет текста описания — светлый на тёмной базе фонов (#020617)
// Все фоны: тёмные полосы + цветные градиенты → светлый текст читается везде
const kioskLabelColorByBg = {
  "kiosk-bg--mimon": "#f8fafc",
  // для очень светлых фонов делаем тёплый светлый текст + тёмную тень
  "kiosk-bg--mixed-fruit": "#fefce8",
  "kiosk-bg--nectarine": "#fefce8",
  "kiosk-bg--blackberry-lime": "#f8fafc",
  "kiosk-bg--blitzsturm": "#f8fafc",
  "kiosk-bg--citrus-bright": "#f8fafc",
  "kiosk-bg--citrus-berry": "#f8fafc",
  "kiosk-bg--berry-deep": "#f8fafc",
  "kiosk-bg--tropical-deep": "#f8fafc",
  "kiosk-bg--erics-mango": "#f8fafc",
  "kiosk-bg--melon-blend": "#f8fafc",
  "kiosk-bg--juicy-peach": "#f8fafc",
  "kiosk-bg--kashmir-peach": "#f8fafc",
  "kiosk-bg--kashmir-guajava": "#f8fafc",
  "kiosk-bg--guajava-kiss": "#f8fafc",
  "kiosk-bg--pineapple": "#f8fafc",
  "kiosk-bg--papaya-sorbet": "#f8fafc",
  "kiosk-bg--watermelon": "#f8fafc",
  "kiosk-bg--sour-watermelon": "#f8fafc",
  "kiosk-bg--tropical-punch": "#f8fafc",
  "kiosk-bg--tropical-revenge": "#f8fafc",
  "kiosk-bg--surfers-delight": "#f8fafc",
  "kiosk-bg--mint-herbal": "#f8fafc",
  "kiosk-bg--wintergreen": "#f8fafc",
  "kiosk-bg--cane-mint": "#f8fafc",
  "kiosk-bg--cucumber-lavender": "#f8fafc",
  "kiosk-bg--dessert-creamy": "#f8fafc",
  "kiosk-bg--tea-aromatic": "#f8fafc",
  "kiosk-bg--spice-kashmir": "#f8fafc",
  "kiosk-bg--kashmir-black": "#f8fafc",
  "kiosk-bg--kashmir": "#f8fafc",
  "kiosk-bg--kashmir-apple": "#f8fafc",
  "kiosk-bg--kashmir-mango": "#f8fafc",
  "kiosk-bg--kashmir-cherry": "#f8fafc",
  "kiosk-bg--cosmic-dark": "#f8fafc",
  "kiosk-bg--exotic-dark": "#f8fafc",
  "kiosk-bg--maraschino-cherry": "#fef3c7",
};

function kioskPlayAddToCartAnimation() {
  const slidesContainer = document.getElementById("kiosk-slides");
  if (!slidesContainer) return;
  const activeImg = slidesContainer.querySelector(
    ".kiosk-slide--pos0 .kiosk-pack-img"
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
  // защита от слишком быстрого пролистывания при жестах по центральной пачке
  if (now - kioskLastChangeAt < 350) return;

  kioskLastChangeAt = now;
  kioskSetActiveIndex(kioskState.activeIndex + delta);
}

function kioskGetImageUrl(product) {
  // Привязываем изображения к коду товара.
  // Ожидаемые файлы:
  // /static/img/sunrise.png
  // /static/img/orange-soda.png
  // /static/img/wintergreen.png
  if (!product.code) return "/static/img/placeholder-pack.png";
  return `/static/img/${product.code}.png`;
}

function kioskNormalizeFilenameKey(s) {
  if (!s) return "";
  return String(s)
    .trim()
    .toLowerCase()
    .replace(/[’']/g, "") // убираем апостроф
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

function kioskGetImageCandidates(product) {
  const code = product && product.code ? String(product.code).trim() : "";
  const name = product && product.name ? String(product.name).trim() : "";
  const out = [];
  if (code) out.push(`/static/img/${code}.png`);
  if (name) out.push(`/static/img/${encodeURIComponent(name)}.png`);
  if (name) {
    const key = kioskNormalizeFilenameKey(name);
    if (key) out.push(`/static/img/${key}.png`);
  }
  return out;
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
    const candidates = kioskGetImageCandidates(p);
    const initialSrc =
      (candidates && candidates[0]) || kioskGetImageUrl(p) || "/static/img/placeholder-pack.png";
    slide.innerHTML = `
      <div class="kiosk-slide-inner">
        <div class="kiosk-slide-main">
          <div class="kiosk-pack-visual">
            <img class="kiosk-pack-img" src="${initialSrc}" alt="${(p.name || "").replace(/"/g, "&quot;")}" />
          </div>
        </div>
      </div>
    `;
    container.appendChild(slide);

    // Если картинки переименовали (например, по имени вместо code),
    // пробуем альтернативные src по onerror.
    const imgEl = slide.querySelector(".kiosk-pack-img");
    if (imgEl && candidates && candidates.length > 1) {
      let idx = 0;
      imgEl.onerror = () => {
        idx += 1;
        if (idx < candidates.length) {
          imgEl.src = candidates[idx];
        } else {
          imgEl.style.display = "none";
        }
      };
    }
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
          // левая половина экрана — обычный, более "тяжёлый" скролл
          if (Math.abs(delta) < 40) return;
          kioskChangeByDelta(delta > 0 ? 1 : -1);
        } else {
          // правая половина — как наше колесо (медленный, но отдельный скролл)
          if (Math.abs(delta) < 40) return;
          const now = Date.now();
          if (now - kioskHaloLastChangeAt < 400) return;
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
        const step = 60; // правая половина — очень медленная прокрутка
        if (Math.abs(diff) < step) return;
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
        const threshold = 60;

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

  slides.forEach((slide, index) => {
    slide.className = "kiosk-slide";
    slide.style.pointerEvents = "none";

    // вычисляем позицию относительно активной с учётом «револьверного» круга
    let delta = index - activeIndex;
    const half = Math.floor(total / 2);
    if (delta > half) delta -= total;
    if (delta < -half) delta += total;

    if (delta === 0) {
      slide.classList.add("kiosk-slide--pos0");
      slide.style.pointerEvents = "auto";
    } else if (delta === 1) {
      slide.classList.add("kiosk-slide--pos1");
    } else if (delta === 2) {
      slide.classList.add("kiosk-slide--pos2");
    } else if (delta === -1) {
      slide.classList.add("kiosk-slide--pos-1");
    } else if (delta === -2) {
      slide.classList.add("kiosk-slide--pos-2");
    } else {
      slide.classList.add("kiosk-slide--far");
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
  const products = kioskState.products;
  if (!products.length) {
    el.innerHTML = "";
    el.style.display = "none";
    return;
  }
  const total = products.length;
  let idx = kioskState.activeIndex;
  idx = ((idx % total) + total) % total;
  const p = products[idx];
  const desc = (p.description || "").trim();
  const name = (p.name || "").trim();
  if (!desc && !name) {
    el.innerHTML = "";
    el.style.display = "none";
    return;
  }
  const meta = p.code ? kioskAromaMeta[p.code] : undefined;
  const bgClass = meta && meta.bgClass ? meta.bgClass : "kiosk-bg--berry-deep";
  let textColor;
  if (
    bgClass === "kiosk-bg--mixed-fruit" ||
    bgClass === "kiosk-bg--nectarine"
  ) {
    textColor = "#0f172a";
  } else {
    textColor = kioskLabelColorByBg[bgClass] || "#f8fafc";
  }

  const cats = kioskCategoriesByBg[bgClass] || ["Сладкий"];

  const catsHtml =
    cats && cats.length
      ? `<div class="kiosk-desc-tags">` +
        cats
          .map(
            (c) =>
              `<span class="kiosk-desc-tag">${kioskEscape(c)}</span>`
          )
          .join("") +
        `</div>`
      : "";
  const html =
    (name
      ? `<span class="kiosk-desc-name">${kioskEscape(name)}</span> `
      : "") +
    (desc ? kioskEscape(desc) : "") +
    catsHtml;

  const dir = kioskState.lastDirection || 1;
  const doUpdate = () => {
    el.innerHTML = html;
    el.style.display = "block";
    el.style.color = textColor;
    el.classList.remove("kiosk-desc-out", "kiosk-desc-out--next", "kiosk-desc-out--prev");
    el.classList.remove("kiosk-desc-in", "kiosk-desc-in--next", "kiosk-desc-in--prev");
    el.classList.add("kiosk-desc-in", dir === 1 ? "kiosk-desc-in--next" : "kiosk-desc-in--prev");
    setTimeout(() => {
      el.classList.remove("kiosk-desc-in", "kiosk-desc-in--next", "kiosk-desc-in--prev");
    }, 800);
  };

  const prevName = el.querySelector(".kiosk-desc-name");
  const prevNameText = prevName ? prevName.textContent : "";
  if (prevNameText && prevNameText !== name) {
    // Клонируем старый текст — сначала вставляем в DOM, потом добавляем классы, чтобы transition сработал
    const clone = el.cloneNode(true);
    clone.id = "";
    clone.classList.remove("kiosk-desc-in", "kiosk-desc-in--next", "kiosk-desc-in--prev");
    clone.classList.add("kiosk-desc-clone");
    clone.style.zIndex = "10";
    document.body.appendChild(clone);
    clone.offsetHeight; // reflow: клон отрендерен в исходной позиции
    clone.classList.add("kiosk-desc-out", dir === 1 ? "kiosk-desc-out--next" : "kiosk-desc-out--prev");
    setTimeout(() => clone.remove(), 750);

    doUpdate();
  } else {
    doUpdate();
  }
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
    const labelSrc = p.code ? kioskLabelImages[p.code] : undefined;
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
        const step = 60; // ещё больше шаг — очень медленная прокрутка
        if (Math.abs(diff) < step) return;
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


