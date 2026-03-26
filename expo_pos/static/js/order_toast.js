// Глобальный тост после оформления заказа (киоск + продавец).
// Показывает номер заказа, сумму и варианты оплаты (наличные / QR).
(function () {
  const TOAST_ID = "order-toast";
  let timer = null;

  function formatRub(amount) {
    const n = Number(amount || 0);
    if (!Number.isFinite(n)) return "0 ₽";
    return `${Math.round(n).toFixed(0)} ₽`;
  }

  function getStaticQrUrl() {
    // 1) можно выставить глобально: window.POS_STATIC_QR_URL = "/static/img/qr.png"
    // 2) или через meta: <meta name="pos-static-qr" content="/static/img/qr.png">
    try {
      if (window.POS_STATIC_QR_URL) return String(window.POS_STATIC_QR_URL);
      const meta = document.querySelector("meta[name='pos-static-qr']");
      const c = meta && meta.getAttribute ? meta.getAttribute("content") : "";
      return c ? String(c) : "";
    } catch (_) {
      return "";
    }
  }

  function ensureRoot() {
    let root = document.getElementById(TOAST_ID);
    if (root) return root;

    root = document.createElement("div");
    root.id = TOAST_ID;
    root.className = "order-toast";
    root.innerHTML = `
      <div class="order-toast__card">
        <button type="button" class="order-toast__close" data-role="order-toast-close">×</button>
        <div class="order-toast__title">Заказ оформлен</div>

        <div class="order-toast__text">
          Заказ № <span class="order-toast__number" data-role="order-toast-number"></span>
          отправлен на сборку. Пожалуйста, <strong>запомните</strong> или <strong>сделайте скриншот</strong> этого номера — он понадобится на выдаче.
        </div>

        <div class="order-toast__amount">
          К оплате: <span class="order-toast__amount-value" data-role="order-toast-amount"></span>
        </div>

        <div class="order-toast__pay-toggle" role="tablist" aria-label="Оплата">
          <button type="button" class="order-toast__pay-btn is-active" data-role="order-toast-pay-cash">Наличные</button>
          <button type="button" class="order-toast__pay-btn" data-role="order-toast-pay-qr">QR CODE</button>
        </div>

        <div class="order-toast__pay-panel" data-role="order-toast-panel-cash">
          Передайте номер заказа и сумму на стойке — мы быстро примем оплату.
        </div>

        <div class="order-toast__pay-panel" data-role="order-toast-panel-qr" style="display:none;">
          <div class="order-toast__qr" data-role="order-toast-qr"></div>
          <div class="order-toast__qr-hint">Сканируйте QR, чтобы открыть реквизиты/сумму.</div>
        </div>
      </div>
    `;

    document.body.appendChild(root);

    const closeBtn = root.querySelector("[data-role='order-toast-close']");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => hide(root));
    }

    const cashBtn = root.querySelector("[data-role='order-toast-pay-cash']");
    const qrBtn = root.querySelector("[data-role='order-toast-pay-qr']");
    if (cashBtn && qrBtn) {
      cashBtn.addEventListener("click", () => setPayMode(root, "cash"));
      qrBtn.addEventListener("click", () => setPayMode(root, "qr"));
    }

    return root;
  }

  function hide(root) {
    root.classList.remove("order-toast--visible");
    if (timer) {
      clearTimeout(timer);
      timer = null;
    }
  }

  function setPayMode(root, mode) {
    const cashBtn = root.querySelector("[data-role='order-toast-pay-cash']");
    const qrBtn = root.querySelector("[data-role='order-toast-pay-qr']");
    const cashPanel = root.querySelector("[data-role='order-toast-panel-cash']");
    const qrPanel = root.querySelector("[data-role='order-toast-panel-qr']");

    if (cashBtn) cashBtn.classList.toggle("is-active", mode === "cash");
    if (qrBtn) qrBtn.classList.toggle("is-active", mode === "qr");
    if (cashPanel) cashPanel.style.display = mode === "cash" ? "block" : "none";
    if (qrPanel) qrPanel.style.display = mode === "qr" ? "block" : "none";
  }

  function renderQrInto(el) {
    if (!el) return;
    el.innerHTML = "";

    const url = getStaticQrUrl();
    if (!url) {
      const div = document.createElement("div");
      div.className = "order-toast__qr-missing";
      div.textContent = "QR код скоро появится";
      el.appendChild(div);
      return;
    }

    const img = document.createElement("img");
    img.className = "order-toast__qr-img";
    img.alt = "QR код оплаты";
    img.loading = "eager";
    img.decoding = "async";
    img.src = url;
    el.appendChild(img);
  }

  // Глобальная функция для киоска и продавца.
  window.showOrderToast = function showOrderToast(orderId, amountRub) {
    const root = ensureRoot();
    const numEl = root.querySelector("[data-role='order-toast-number']");
    const amtEl = root.querySelector("[data-role='order-toast-amount']");
    if (numEl) numEl.textContent = orderId != null ? String(orderId) : "—";
    if (amtEl) amtEl.textContent = formatRub(amountRub);

    // По умолчанию — Наличные (можно поменять на "qr", если захочешь).
    setPayMode(root, "cash");

    const qrEl = root.querySelector("[data-role='order-toast-qr']");
    renderQrInto(qrEl);

    root.classList.add("order-toast--visible");
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      hide(root);
    }, 30000);
  };
})();

