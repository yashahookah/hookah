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

function kioskBaseCode(code) {
  if (!code) return "";
  // В БД при коллизиях код дополняется суффиксом `-v2`, `-v3` и т.д.
  // Для фонов используем базовую часть.
  return String(code).replace(/-v\d+$/i, "");
}

function kioskGetAromaMetaByProduct(product) {
  if (!product) return undefined;
  const code = product.code ? String(product.code).trim() : "";
  if (!code) return undefined;
  return kioskAromaMeta[code] || kioskAromaMeta[kioskBaseCode(code)];
}

function kioskAutoBgMetaForProduct(product) {
  const code = product && product.code ? String(product.code).trim().toLowerCase() : "";
  const name = product && product.name ? String(product.name).trim().toLowerCase() : "";
  const text = `${code} ${name}`.toLowerCase();

  // Гастрономический аромат
  if (text.includes("bacon")) {
    return { bgClass: "kiosk-bg--gastronomic" };
  }

  // Миксы/фрукты
  if (
    text.includes("mixed") ||
    text.includes("mix") ||
    text.includes("melange") ||
    text.includes("смеш")
  ) {
    return { bgClass: "kiosk-bg--mixed-fruit" };
  }
  if (text.includes("nectarine")) return { bgClass: "kiosk-bg--nectarine" };
  if (text.includes("strawberry") || text.includes("berry") || text.includes("blueberry") || text.includes("blackberry")) {
    return { bgClass: "kiosk-bg--berry-deep" };
  }

  // Цитрусы/лимонады
  if (
    text.includes("lemon") ||
    text.includes("lime") ||
    text.includes("orange") ||
    text.includes("grapefruit") ||
    text.includes("citrus") ||
    text.includes("sunrise") ||
    text.includes("soda")
  ) {
    return { bgClass: "kiosk-bg--citrus-bright" };
  }

  // Арбузы/кислые арбузы
  if (text.includes("watermelon")) {
    return text.includes("sour") ? { bgClass: "kiosk-bg--sour-watermelon" } : { bgClass: "kiosk-bg--watermelon" };
  }

  // Тропики
  if (text.includes("mango") || text.includes("mang")) return { bgClass: "kiosk-bg--erics-mango" };
  if (text.includes("peach") || text.includes("cobbler") || text.includes("iced tea")) return { bgClass: "kiosk-bg--juicy-peach" };
  if (text.includes("pineapple") || text.includes("passinfruit") || text.includes("passionfruit")) {
    return { bgClass: "kiosk-bg--tropical-punch" };
  }

  // Мята/травы
  if (text.includes("wintergreen") || text.includes("mint") || text.includes("зел") || text.includes("green")) {
    return { bgClass: "kiosk-bg--wintergreen" };
  }
  if (text.includes("cane-mint") || text.includes("cane mint")) return { bgClass: "kiosk-bg--cane-mint" };
  if (text.includes("cucumber") || text.includes("lavender")) return { bgClass: "kiosk-bg--cucumber-lavender" };
  if (text.includes("cilantro") || text.includes("coriander") || text.includes("basil")) {
    return { bgClass: "kiosk-bg--mint-herbal" };
  }

  // Чай/пряности
  if (text.includes("chai") || text.includes("tea")) return { bgClass: "kiosk-bg--tea-aromatic" };
  if (text.includes("kashmir") || text.includes("spice") || text.includes("cinnamon")) return { bgClass: "kiosk-bg--kashmir" };

  // Гастро-десертные/печеньки/тесто
  if (text.includes("cookie") || text.includes("dough") || text.includes("cereal") || text.includes("breakfast")) {
    return { bgClass: "kiosk-bg--dessert-creamy" };
  }

  // Закаты/темные миксы (как дефолт)
  if (text.includes("sunset") || text.includes("muerte")) return { bgClass: "kiosk-bg--cosmic-dark" };

  return { bgClass: "kiosk-bg--berry-deep" };
}

function kioskFallbackDescription(productName) {
  if (!productName) return "";
  const t = String(productName).trim().toLowerCase();

  if (t.includes("bacon")) {
    return "Запеченный бекон: тёплый дымный гастрономический вкус с приятной солоноватой ноткой. Даёт ощущение «с кухни» и добавляет плотную основу миксам.";
  }
  if (t.includes("basil") && t.includes("strawberry")) {
    return "Клубника с травяной глубиной базилика. Сладость ягод мягко уравновешивается свежей зеленью и оставляет чистое, аккуратное послевкусие.";
  }
  if (t.includes("blueberry") && t.includes("grapefruit")) {
    return "Черника и грейпфрут: ягодная сладость встречает бодрую цитрусовую кислинку. Вкус яркий и свежий, запоминается с первой затяжки.";
  }
  if (t.includes("chai")) {
    return "Chai — тёплый пряный чайный вкус с мягкой сладостью. Композиция раскрывается как уютный аромат специй и легко ложится в миксы.";
  }
  if (t.includes("cilantro") || t.includes("coriander") || t.includes("кинза")) {
    return "Кинза: сочная травяная нота и лёгкая пикантность. Вкус свежий, зелёный и хорошо сочетается с цитрусами и ягодами.";
  }
  if ((t.includes("cookie") && t.includes("dough")) || t.includes("cookie dough") || t.includes("доу")) {
    return "Cookie Dough — тёплое сливочное тесто и сладкое печенье. Комфортная гастрономическая сладость делает миксы насыщенными и «домашними».";
  }
  if (t.includes("it's like that one") || t.includes("breakfast") || t.includes("cereal") || t.includes("завтрак")) {
    return "Завтрак в стиле «как тот самый»: овсяные нотки, мягкая выпечная сладость и бодрый цитрусовый акцент. Лёгкий вкус, который приятно «включает» с первой затяжки.";
  }
  if (t.includes("mango") && t.includes("fling")) {
    return "Mango Fling — сочный манго с фруктовым драйвом и лёгкой кислинкой. Вкус тропический, яркий и очень бодрый.";
  }
  if (t.includes("mango")) {
    return "Манго: спелая тропическая сладость и мягкая кислинка. Сочный вкус, который раскрывается легко и оставляет приятное послевкусие.";
  }
  if (t === "mixed" || t.includes("mixed fruit") || t.includes("mixed")) {
    return "Классический фруктовый микс: сладкие ягоды и сочные фрукты в одном направлении. Баланс держится на насыщенном вкусе и аккуратном послевкусии.";
  }
  if (t.includes("muerte")) {
    return "Muerte — тёмный, глубокий микс с ягодной сочностью и пряной атмосферой. Вкус плотный, «бархатный» и долго остаётся в памяти.";
  }
  if (t.includes("papa's f") || (t.includes("papa") && t.includes("foreplay")) || t.includes("foreplay")) {
    return "Papa's F / Foreplay: мягкая фруктовая сладость с тропическим акцентом. Вкус живой, лёгкий и хорошо работает как база для миксов.";
  }
  if (t.includes("passinfruit") || t.includes("passionfruit")) {
    return "Passionfruit / Passinfruit Lemonade: маракуйя и лимонад — тропическая кислинка, пузырьковая свежесть и сладкое послевкусие.";
  }
  if (t.includes("rangoon") && t.includes("sunrise")) {
    return "Rangoon Sunrise: яркая цитрусовая композиция с мягкой сладостью. Вкус солнечный, бодрый и очень «утренний».";
  }
  if (t.includes("static starlight") && (t.includes("зелен") || t.includes("green"))) {
    return "Static Starlight (зелёный): холодная травяная свежесть и лёгкая мятная глубина. Чистый, прохладный и эффектный вкус.";
  }
  if (t.includes("static starlight") || t.includes("starlight")) {
    return "Static Starlight: тёмный космический микс с прохладным характером и мягким сладким завершением.";
  }
  if (t === "sunrise") {
    return "Sunrise — свежий рассвет: цитрусовая яркость и мягкая сладость без резкости. Лёгкий вкус, который заряжает энергией.";
  }
  if (t === "sunset") {
    return "Sunset — закат: тропическая фруктовая волна с тёплым, мягким послевкусием. Сочный вкус, который приятно тянется до конца.";
  }

  return "";
}

function kioskGetMetaForProduct(product) {
  const direct = kioskGetAromaMetaByProduct(product);
  if (direct && direct.bgClass) return direct;
  const auto = kioskAutoBgMetaForProduct(product);
  if (auto && auto.bgClass) return auto;
  return { bgClass: "kiosk-bg--berry-deep" };
}

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
  // гастрономический
  "kiosk-bg--gastronomic": ["Гастрономический"],
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
  "kiosk-bg--gastronomic": "#fefce8",
};

const KIOSK_MERCH_META = {
  "merch-dakimakura-kashmir-peach": {
    title: "Подушка - Kashmir Peach",
    description: "Подушка Kashmir Peach",
  },
  "merch-dakimakura-cane-mint": {
    title: "Подушка - Cane mint",
    description: "Подушка Cane mint",
  },
  "merch-dakimakura-maraschino-cherry": {
    title: "Подушка - Maraschino Cherry",
    description: "Подушка Maraschino Cherry",
  },
  "merch-dakimakura-ololiui": {
    title: "Подушка - Ololiuqui",
    description: "Подушка Ololiuqui",
  },
  "merch-dakimakura-papaya-sorbet": {
    title: "Подушка - Papaya Sorbet",
    description: "Подушка Papaya Sorbet",
  },
  "merch-mouthpiece-noxpipe-x-tangiers": {
    title: "Мундштук",
    description: "NoxPipe x Tangiers",
  },
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
let kioskBooted = false;

function kioskIsVisible() {
  const view = document.getElementById("view-kiosk");
  return !!(view && !view.classList.contains("app-view--hidden"));
}

function kioskEnsureBoot() {
  if (kioskBooted) return;
  kioskBooted = true;
  kioskFetchProducts();
}

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
  // Картинка берётся строго по текущим именам файлов в `static/img`.
  // Если файлов нет — покажется placeholder (а затем можно будет скрыть/починить).
  const name = product && product.name ? String(product.name).trim() : "";
  if (!name) return "/static/img/placeholder-pack.png";
  const v = name === "Мундштук NoxPipe x Tangiers" ? "mouthpiece-20260327" : "";
  return `/static/img/${encodeURIComponent(name)}.png${v ? `?v=${v}` : ""}`;
}

function kioskGetImageCandidates(product) {
  const name = product && product.name ? String(product.name).trim() : "";
  if (!name) return ["/static/img/placeholder-pack.png"];
  // Только точное совпадение с именем файла — никаких "подборов" и переобрезок.
  const v = name === "Мундштук NoxPipe x Tangiers" ? "mouthpiece-20260327" : "";
  return [`/static/img/${encodeURIComponent(name)}.png${v ? `?v=${v}` : ""}`];
}

async function kioskFetchProducts() {
  try {
    const res = await fetch("/api/products");
  if (!res.ok) {
    console.error("Ошибка загрузки товаров");
    return;
  }
    const data = await res.json();

    // Важно: сервер на 8011 может быть старым по логике (мы не можем его убить).
    // Поэтому перезаписываем display/description данными из статического JSON.
    try {
      const ovRes = await fetch("/static/data/tng_products.json", {
        cache: "no-store",
      });
      if (ovRes && ovRes.ok) {
        const ovData = await ovRes.json();
        const items = (ovData && ovData.items) || null;
        if (items && typeof items === "object") {
          data.forEach((p) => {
            const key = p && p.name ? String(p.name).trim().toLowerCase() : "";
            const ov = key && items[key] ? items[key] : null;
            if (ov) {
              p.display_name_en = ov.display_name_en || p.display_name_en || p.name;
              p.description = ov.description || p.description;
            }
          });
        }
      }
    } catch (e) {
      console.warn("TNG overrides apply failed", e);
    }

    // В витрине показываем только то, что есть в наличии.
    const inStockOnly = data.filter((p) => {
      if (typeof p.in_stock === "boolean") return p.in_stock;
      return Number(p.quantity || 0) > 0;
    });
    kioskState.products = inStockOnly.sort((a, b) =>
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
    const code = String((p && p.code) || "").toLowerCase();
    const noClipClass = code.startsWith("merch-mouthpiece")
      ? " kiosk-pack-img--no-clip"
      : "";
    const merchMeta = KIOSK_MERCH_META[code] || null;
    const aromaMeta = merchMeta ? null : kioskGetMetaForProduct(p);
    if (aromaMeta) {
      slide.classList.add("kiosk-aroma");
      if (aromaMeta.themeClass) slide.classList.add(aromaMeta.themeClass);
    }
    const candidates = kioskGetImageCandidates(p);
    const initialSrc =
      (candidates && candidates[0]) || kioskGetImageUrl(p) || "/static/img/placeholder-pack.png";

    const bgClass = aromaMeta && aromaMeta.bgClass ? aromaMeta.bgClass : "kiosk-bg--berry-deep";
    const cats = kioskCategoriesByBg[bgClass] || ["Сладкий"];
    const catsHtml = merchMeta
      ? ""
      : cats.map((c) => `<span class="kiosk-desc-tag">${kioskEscape(c)}</span>`).join("");
    let textColor =
      bgClass === "kiosk-bg--mixed-fruit" || bgClass === "kiosk-bg--nectarine"
        ? "#0f172a"
        : kioskLabelColorByBg[bgClass] || "#f8fafc";
    const desc = merchMeta
      ? String(merchMeta.description || "").trim()
      : ((p.description || "").trim() || kioskFallbackDescription(p.name)).trim();

    slide.innerHTML = `
      <div class="kiosk-slide-inner">
        <div class="kiosk-slide-caption" style="color:${textColor}">
          <div class="kiosk-slide-caption__name">${kioskEscape(
            merchMeta ? merchMeta.title : kioskCanonicalDisplayNameEn(p)
          )}</div>
          ${desc ? `<div class="kiosk-slide-caption__desc">${kioskEscape(desc)}</div>` : ""}
          ${catsHtml ? `<div class="kiosk-desc-tags kiosk-slide-caption__tags">${catsHtml}</div>` : ""}
        </div>

        <div class="kiosk-slide-main">
          <div class="kiosk-pack-visual">
            <img class="kiosk-pack-img${noClipClass}" src="${initialSrc}" alt="${(p.name || "").replace(/"/g, "&quot;")}" />
          </div>
        </div>
      </div>
    `;
    container.appendChild(slide);

    const imgEl = slide.querySelector(".kiosk-pack-img");
    if (imgEl) {
      imgEl.onerror = () => {
        // Если файл всё равно не нашёлся — скрываем пустую карточку.
        imgEl.style.display = "none";
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
  const meta = kioskGetMetaForProduct(active);

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

function kioskGetGiftContext() {
  let tobaccoQty = 0;
  Object.entries(kioskState.cart).forEach(([idStr, qty]) => {
    const id = parseInt(idStr, 10);
    const product = kioskState.products.find((p) => p.id === id);
    if (!product) return;
    const code = String(product.code || "").toLowerCase();
    if (!code.startsWith("merch-")) {
      tobaccoQty += Number(qty || 0);
    }
  });

  const giftProduct = kioskState.products.find((p) => {
    const code = String(p.code || "").toLowerCase();
    const inStock =
      typeof p.in_stock === "boolean" ? p.in_stock : Number(p.quantity || 0) > 0;
    return code.startsWith("merch-dakimakura") && inStock && Number(p.quantity || 0) > 0;
  });

  const eligible = tobaccoQty >= 10 && !!giftProduct;
  return { eligible, tobaccoQty, giftProduct };
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

function kioskCanonicalDisplayNameEn(product) {
  const code = String((product && product.code) || "")
    .trim()
    .toLowerCase();
  const name = String((product && product.name) || "")
    .trim()
    .toLowerCase();
  const disp = String((product && product.display_name_en) || "").trim();
  if (code === "cilantro" || code === "cilantro-pineapple" || name === "cilantro") {
    return "Cilantro pineapple";
  }
  if (code === "muerte" || code === "muerte-por-arroz" || name === "muerte") {
    return "Muerte por Arroz";
  }
  if (code === "mixed" || code === "mixed-fruit" || name === "mixed") {
    return "Mixed Fruit";
  }
  if (
    code === "papas-f" ||
    code === "papas-foreplay" ||
    name === "papa's f" ||
    name === "papas f"
  ) {
    return "Papa's Foreplay";
  }
  return disp || (product && product.name) || "";
}

function kioskUpdateDescription() {
  // Мы показываем описание/расшифровку только в caption под "лицевой" пачкой.
  // Фиксированный блок #kiosk-description отключаем, чтобы не было дублей и “хвостов” от предыдущих ароматов.
  const el = document.getElementById("kiosk-description");
  if (el) el.style.display = "none";
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
    const safeName = kioskCanonicalDisplayNameEn(p) || p.code || "";
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
  const giftCtx = kioskGetGiftContext();
  entries.forEach(([idStr, qty]) => {
    const id = parseInt(idStr, 10);
    const product = kioskState.products.find((p) => p.id === id);
    if (!product) return;
    totalQty += qty;
    totalAmount += product.price * qty;
  });

  summaryText.textContent = `Вы выбрали ${totalQty} шт. на ${totalAmount.toFixed(0)} ₽${
    giftCtx.eligible ? " + подушка в подарок" : ""
  }`;
  openBtn.disabled = false;
  kioskRenderCart();
}

function kioskRenderCart() {
  const itemsEl = document.getElementById("kiosk-cart-items");
  const emptyEl = document.getElementById("kiosk-cart-empty");
  const totalEl = document.getElementById("kiosk-cart-total");
  const submitBtn = document.getElementById("kiosk-submit-order");
  const clearBtn = document.getElementById("kiosk-clear-cart");

  itemsEl.innerHTML = "";

  const entries = Object.entries(kioskState.cart);
  if (!entries.length) {
    emptyEl.style.display = "block";
    submitBtn.disabled = true;
    if (clearBtn) clearBtn.disabled = true;
    totalEl.textContent = "0 ₽";
    return;
  }

  emptyEl.style.display = "none";
  let totalAmount = 0;
  const giftCtx = kioskGetGiftContext();

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
        <div class="kiosk-cart-item-controls">
          <button class="kiosk-cart-qty-btn" data-role="dec" data-id="${product.id}">-</button>
          <span class="kiosk-cart-qty-value">${qty}</span>
          <button class="kiosk-cart-qty-btn" data-role="inc" data-id="${product.id}">+</button>
        </div>
      </div>
      <div class="kiosk-cart-item-amount">${lineAmount.toFixed(0)} ₽</div>
    `;
    itemsEl.appendChild(li);
  });

  if (giftCtx.eligible && giftCtx.giftProduct) {
    const gift = giftCtx.giftProduct;
    const li = document.createElement("li");
    li.className = "kiosk-cart-item";
    li.innerHTML = `
      <div>
        <div class="kiosk-cart-item-name">${gift.name} 🎁</div>
        <div class="kiosk-cart-item-meta">1 × 0 ₽ (подарок за 10 пачек)</div>
      </div>
      <div class="kiosk-cart-item-amount">0 ₽</div>
    `;
    itemsEl.appendChild(li);
  }

  totalEl.textContent = `${totalAmount.toFixed(0)} ₽`;
  submitBtn.disabled = false;
  if (clearBtn) clearBtn.disabled = false;
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

function kioskClearCart() {
  Object.keys(kioskState.cart).forEach((k) => delete kioskState.cart[k]);
  kioskRenderSummary();
}

function kioskGetSelectedPaymentMethod() {
  const selected = document.querySelector(
    'input[name="kiosk-payment-method"]:checked'
  );
  const value = selected ? String(selected.value || "").toLowerCase() : "cash";
  return value === "qr" ? "qr" : "cash";
}

async function kioskSubmitOrder() {
  const entries = Object.entries(kioskState.cart);
  if (!entries.length) return;

  function fetchWithTimeout(url, options = {}, timeoutMs = 30000) {
    const controller = new AbortController();
    const t = setTimeout(() => controller.abort(), timeoutMs);
    const merged = { ...options, signal: controller.signal };
    return fetch(url, merged).finally(() => clearTimeout(t));
  }

  // Сумма нужна для окна оплаты после оформления заказа.
  let totalAmount = 0;
  try {
    entries.forEach(([idStr, qty]) => {
      const id = parseInt(idStr, 10);
      const product = kioskState.products.find((p) => p.id === id);
      if (!product) return;
      totalAmount += Number(product.price || 0) * Number(qty || 0);
    });
  } catch (_) {}

  const items = entries.map(([idStr, qty]) => ({
    product_id: parseInt(idStr, 10),
    quantity: qty,
  }));
  const payment_method = kioskGetSelectedPaymentMethod();
  const giftCtx = kioskGetGiftContext();
  const gift_product_id =
    giftCtx.eligible && giftCtx.giftProduct ? giftCtx.giftProduct.id : null;

  const msgEl = document.getElementById("kiosk-cart-message");
  const btn = document.getElementById("kiosk-submit-order");
  btn.disabled = true;
  msgEl.textContent = "Отправляем заказ…";
  msgEl.className = "kiosk-cart-message";

  try {
    const res = await fetchWithTimeout("/api/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ items, payment_method, gift_product_id }),
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
    // Не блокируем UI на обновлении остатков: /api/products может подвисать на хостинге/БД.
    Promise.resolve()
      .then(() => kioskFetchProducts())
      .catch((e) => console.warn("kioskFetchProducts failed after order", e));
    kioskCloseCart();

    const summaryText = document.getElementById("kiosk-summary-text");
    summaryText.textContent = "Заказ отправлен, подойдите к стойке";
    if (orderId != null && typeof showOrderToast === "function") {
      showOrderToast(orderId, totalAmount);
    }
  } catch (e) {
    console.error(e);
    if (e && (e.name === "AbortError" || /aborted/i.test(String(e.message || "")))) {
      msgEl.textContent = "Сервер долго отвечает. Проверьте связь и попробуйте ещё раз.";
      msgEl.className = "kiosk-cart-message kiosk-cart-message--error";
      return;
    }
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
  if (kioskIsVisible()) kioskEnsureBoot();

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
      const label =
        kioskCanonicalDisplayNameEn(active) || active.code || "пачка";
      const meta = kioskGetMetaForProduct(active);
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
  const clearBtn = document.getElementById("kiosk-clear-cart");
  if (clearBtn) {
    clearBtn.addEventListener("click", kioskClearCart);
  }
  document.getElementById("kiosk-cart-items").addEventListener("click", (e) => {
    const btn = e.target;
    if (!btn || !btn.dataset || !btn.dataset.role) return;
    const id = parseInt(btn.dataset.id, 10);
    if (!Number.isFinite(id)) return;
    if (btn.dataset.role === "inc") {
      kioskChangeQty(id, 1);
    } else if (btn.dataset.role === "dec") {
      kioskChangeQty(id, -1);
    }
  });

  window.addEventListener("pos:view-change", (e) => {
    const viewName = e && e.detail ? String(e.detail) : "";
    if (viewName === "kiosk") {
      kioskEnsureBoot();
      kioskRenderSummary();
    }
  });
});


