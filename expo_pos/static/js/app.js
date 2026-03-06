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
})();
