/**
 * Единая страница киоска и простого меню.
 * Переключение без перезагрузки, общая корзина.
 */
(function () {
  window.posCart = window.posCart || {};

  const viewKiosk = document.getElementById("view-kiosk");
  const viewSeller = document.getElementById("view-seller");
  const floatingBar = document.getElementById("seller-floating-bar");
  const btnSimple = document.getElementById("app-btn-simple-menu");
  const btnKiosk = document.getElementById("app-btn-kiosk");

  function showView(name) {
    if (!viewKiosk || !viewSeller) return;
    if (name === "kiosk") {
      document.body.classList.add("kiosk-body-lock");
      document.body.classList.remove("view-seller-active");
      viewKiosk.classList.remove("app-view--hidden");
      viewSeller.classList.add("app-view--hidden");
      if (floatingBar) floatingBar.classList.add("seller-floating-bar--hidden");
      if (typeof kioskRenderSummary === "function") kioskRenderSummary();
    } else {
      document.body.classList.remove("kiosk-body-lock");
      document.body.classList.add("view-seller-active");
      viewKiosk.classList.add("app-view--hidden");
      viewSeller.classList.remove("app-view--hidden");
      if (floatingBar) floatingBar.classList.remove("seller-floating-bar--hidden");
      if (typeof renderProducts === "function") renderProducts();
      if (typeof renderCart === "function") renderCart();
    }
    try {
      window.dispatchEvent(new CustomEvent("pos:view-change", { detail: name }));
    } catch (_) {}
  }

  // Стартовый вид: если URL /seller — открываем простое меню, иначе киоск
  try {
    const path = window.location.pathname || "";
    if (path.startsWith("/seller")) {
      showView("seller");
    } else {
      showView("kiosk");
    }
  } catch (_) {
    showView("kiosk");
  }

  if (btnSimple) {
    btnSimple.addEventListener("click", () => showView("seller"));
  }
  if (btnKiosk) {
    btnKiosk.addEventListener("click", () => showView("kiosk"));
  }

  function updateDeviceClass() {
    try {
      const w = window.innerWidth || document.documentElement.clientWidth || 0;
      const h = window.innerHeight || document.documentElement.clientHeight || 0;
      const minSide = Math.min(w, h);
      const isTouch =
        "ontouchstart" in window || (navigator && navigator.maxTouchPoints > 0);
      let type = "desktop";
      if (isTouch && minSide <= 640) {
        type = "phone";
      } else if (isTouch && minSide <= 1024) {
        type = "tablet";
      }
      document.body.dataset.device = type;
    } catch (e) {}
  }

  updateDeviceClass();
  window.addEventListener("resize", updateDeviceClass);

  // Блокируем zoom от дабл-тапа / быстрых тапов на iOS и мобильных
  let lastTouchEnd = 0;
  document.addEventListener(
    "touchend",
    (event) => {
      const now = Date.now();
      if (now - lastTouchEnd <= 300) {
        event.preventDefault();
      }
      lastTouchEnd = now;
    },
    { passive: false }
  );
})();

