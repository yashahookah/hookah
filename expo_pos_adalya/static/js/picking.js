const STATUS_LABELS = {
  new: "Новый",
  picking: "В сборке",
  ready: "Готов",
  paid: "Оплачен",
  canceled: "Отменён",
};

function getSelectedStatuses() {
  return Array.from(document.querySelectorAll(".status-filter:checked")).map(
    (el) => el.value
  );
}

async function fetchOrders() {
  const statuses = getSelectedStatuses();
  const params = new URLSearchParams();
  statuses.forEach((s) => params.append("statuses", s));
  const res = await fetch(`/api/orders?${params.toString()}`);
  if (!res.ok) {
    console.error("Ошибка загрузки заказов");
    return;
  }
  const data = await res.json();
  renderOrders(data);
}

function renderOrders(orders) {
  const container = document.getElementById("orders");
  container.innerHTML = "";
  if (!orders.length) {
    container.innerHTML = '<div class="hint">Пока нет заказов.</div>';
    return;
  }

  orders.forEach((order) => {
    const card = document.createElement("div");
    const statusClass = `order-status--${order.status}`;
    const created = new Date(order.created_at);
    const timeLabel = created.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
    const itemsHtml = order.items
      .map(
        (i) =>
          `<li>${i.product_name}: <strong>${i.quantity}</strong> шт.</li>`
      )
      .join("");

    card.className = "order-card";
    card.innerHTML = `
      <div class="order-card__header">
        <span>#${order.id}</span>
        <span>${timeLabel}</span>
      </div>
      <div class="order-status ${statusClass}">
        ${STATUS_LABELS[order.status] || order.status}
      </div>
      <ul class="order-items">
        ${itemsHtml}
      </ul>
      <div class="order-total">Сумма: ${order.total_amount.toFixed(0)} ₽</div>
      <div class="order-actions">
        ${renderButtons(order)}
      </div>
    `;

    container.appendChild(card);
  });
}

function renderButtons(order) {
  const { status } = order;
  const btns = [];

  if (status === "new") {
    btns.push(
      `<button class="order-btn order-btn--primary" data-action="picking" data-id="${order.id}">Начать сборку</button>`
    );
  } else if (status === "picking") {
    btns.push(
      `<button class="order-btn order-btn--secondary" data-action="ready" data-id="${order.id}">Готов</button>`
    );
  } else if (status === "ready") {
    btns.push(
      `<button class="order-btn order-btn--primary" data-action="paid" data-id="${order.id}">Оплачен</button>`
    );
  }

  if (status !== "paid" && status !== "canceled") {
    btns.push(
      `<button class="order-btn order-btn--ghost" data-action="canceled" data-id="${order.id}">Отменить</button>`
    );
  }

  return btns.join("");
}

async function updateStatus(id, nextStatus) {
  try {
    const res = await fetch(`/api/orders/${id}/status`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ status: nextStatus }),
    });
    if (!res.ok) {
      console.error("Ошибка обновления статуса");
    } else {
      await fetchOrders();
    }
  } catch (e) {
    console.error(e);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fetchOrders();
  setInterval(fetchOrders, 5000);

  document
    .querySelectorAll(".status-filter")
    .forEach((el) => el.addEventListener("change", fetchOrders));

  document
    .getElementById("orders")
    .addEventListener("click", (e) => {
      const btn = e.target;
      if (!btn.dataset || !btn.dataset.action) return;
      const id = parseInt(btn.dataset.id, 10);
      const action = btn.dataset.action;
      updateStatus(id, action);
    });
});

