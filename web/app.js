const STORAGE_KEY = 'omni-erp-web-data-v1';

const seedData = {
  inventory: [
    { warehouse: 'WH-HCM', sku: 'SKU-RED', quantity: 18, value: 216000 },
    { warehouse: 'WH-HCM', sku: 'SKU-BLUE', quantity: 7, value: 98000 },
    { warehouse: 'WH-HN', sku: 'SKU-RED', quantity: 5, value: 62500 },
    { warehouse: 'WH-HN', sku: 'SKU-GREEN', quantity: 3, value: 45000 },
  ],
  orders: [
    { date: '2026-07-01', platform: 'Shopee', orderId: 'SHP-1001', sku: 'SKU-RED', revenue: 240000, cogs: 110000 },
    { date: '2026-07-02', platform: 'TikTok Shop', orderId: 'TT-1001', sku: 'SKU-BLUE', revenue: 320000, cogs: 145000 },
    { date: '2026-07-03', platform: 'Lazada', orderId: 'LZD-1001', sku: 'SKU-GREEN', revenue: 180000, cogs: 76000 },
    { date: '2026-07-04', platform: 'Shopee', orderId: 'SHP-1002', sku: 'SKU-RED', revenue: 135000, cogs: 62000 },
  ],
  automations: [
    { task: 'Sync marketplace orders', schedule: 'Daily 07:00', status: 'Ready' },
    { task: 'Refresh dashboard', schedule: 'Daily 07:15', status: 'Ready' },
    { task: 'Create backup', schedule: 'Daily 23:30', status: 'Ready' },
  ],
};

let state = structuredClone(seedData);

function loadBrowserState() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return structuredClone(seedData);
  try {
    return JSON.parse(raw);
  } catch {
    return structuredClone(seedData);
  }
}

async function loadState() {
  if (window.location.protocol === 'file:') {
    state = loadBrowserState();
    return;
  }

  try {
    const response = await fetch('/api/state');
    const serverState = await response.json();
    state = hasStateData(serverState) ? serverState : structuredClone(seedData);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    if (!hasStateData(serverState)) await saveState();
  } catch {
    state = loadBrowserState();
  }
}

async function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  if (window.location.protocol === 'file:') return;

  try {
    await fetch('/api/state', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state),
    });
  } catch {
    // Browser localStorage remains the fallback if the local server is interrupted.
  }
}

function hasStateData(value) {
  return value && Array.isArray(value.orders) && Array.isArray(value.inventory) && Array.isArray(value.automations);
}

function money(value) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(value);
}

function profit(order) {
  return order.revenue - order.cogs;
}

function summarize() {
  const totalRevenue = state.orders.reduce((sum, order) => sum + order.revenue, 0);
  const totalProfit = state.orders.reduce((sum, order) => sum + profit(order), 0);
  const totalStock = state.inventory.reduce((sum, row) => sum + row.quantity, 0);
  return { totalRevenue, totalProfit, totalStock, orders: state.orders.length };
}

function renderDashboard() {
  const summary = summarize();
  document.querySelector('#kpi-revenue').textContent = money(summary.totalRevenue);
  document.querySelector('#kpi-profit').textContent = money(summary.totalProfit);
  document.querySelector('#kpi-orders').textContent = summary.orders.toString();
  document.querySelector('#kpi-stock').textContent = summary.totalStock.toString();

  const platformRows = groupByPlatform();
  document.querySelector('#platform-summary').innerHTML = platformRows
    .map(([platform, values]) => `<div class="metric-row"><strong>${platform}</strong><span>${money(values.revenue)} / ${money(values.profit)}</span></div>`)
    .join('');

  drawRevenueChart();
}

function groupByPlatform() {
  const grouped = new Map();
  state.orders.forEach((order) => {
    const current = grouped.get(order.platform) || { revenue: 0, profit: 0 };
    current.revenue += order.revenue;
    current.profit += profit(order);
    grouped.set(order.platform, current);
  });
  return Array.from(grouped.entries()).sort((a, b) => a[0].localeCompare(b[0]));
}

function chartPoints() {
  const grouped = new Map();
  state.orders.forEach((order) => {
    const current = grouped.get(order.date) || { date: order.date, revenue: 0, profit: 0 };
    current.revenue += order.revenue;
    current.profit += profit(order);
    grouped.set(order.date, current);
  });
  return Array.from(grouped.values()).sort((a, b) => a.date.localeCompare(b.date));
}

function drawRevenueChart() {
  const canvas = document.querySelector('#revenue-chart');
  const ctx = canvas.getContext('2d');
  const points = chartPoints();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const padding = 44;
  const maxValue = Math.max(...points.flatMap((point) => [point.revenue, point.profit]), 1);
  const plotWidth = canvas.width - padding * 2;
  const plotHeight = canvas.height - padding * 2;

  ctx.strokeStyle = '#d9e0e7';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i += 1) {
    const y = padding + (plotHeight / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(canvas.width - padding, y);
    ctx.stroke();
  }

  drawLine(ctx, points, 'revenue', maxValue, padding, plotWidth, plotHeight, '#116466');
  drawLine(ctx, points, 'profit', maxValue, padding, plotWidth, plotHeight, '#c7633a');

  ctx.fillStyle = '#687385';
  ctx.font = '12px Arial';
  points.forEach((point, index) => {
    const x = padding + (plotWidth / Math.max(points.length - 1, 1)) * index;
    ctx.fillText(point.date.slice(5), x - 14, canvas.height - 14);
  });
  document.querySelector('#chart-range').textContent = points.length ? `${points[0].date} - ${points[points.length - 1].date}` : '';
}

function drawLine(ctx, points, key, maxValue, padding, plotWidth, plotHeight, color) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 3;
  ctx.beginPath();
  points.forEach((point, index) => {
    const x = padding + (plotWidth / Math.max(points.length - 1, 1)) * index;
    const y = padding + plotHeight - (point[key] / maxValue) * plotHeight;
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

function renderInventory() {
  document.querySelector('#inventory-count').textContent = `${state.inventory.length} dong`;
  document.querySelector('#inventory-table').innerHTML = state.inventory
    .map((row) => {
      const warning = row.quantity <= 5 ? '<span class="low-stock">Sap het</span>' : 'OK';
      return `<tr><td>${row.warehouse}</td><td>${row.sku}</td><td>${row.quantity}</td><td>${money(row.value)}</td><td>${warning}</td></tr>`;
    })
    .join('');
}

function renderOrders() {
  const rows = [...state.orders].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 20);
  document.querySelector('#orders-table').innerHTML = rows
    .map((order) => `<tr><td>${order.date}</td><td>${order.platform}</td><td>${order.orderId}</td><td>${order.sku}</td><td>${money(profit(order))}</td></tr>`)
    .join('');
}

function filteredOrders() {
  const start = document.querySelector('#filter-start').value;
  const end = document.querySelector('#filter-end').value;
  const platform = document.querySelector('#filter-platform').value;
  return state.orders.filter((order) => {
    if (start && order.date < start) return false;
    if (end && order.date > end) return false;
    if (platform && order.platform !== platform) return false;
    return true;
  });
}

function renderReports() {
  document.querySelector('#report-table').innerHTML = filteredOrders()
    .map((order) => `<tr><td>${order.date}</td><td>${order.platform}</td><td>${order.orderId}</td><td>${money(order.revenue)}</td><td>${money(order.cogs)}</td><td>${money(profit(order))}</td></tr>`)
    .join('');
}

function renderOperations() {
  document.querySelector('#automation-list').innerHTML = state.automations
    .map((task) => `<div class="metric-row"><strong>${task.task}</strong><span>${task.schedule} - ${task.status}</span></div>`)
    .join('');
}

function renderAll() {
  renderDashboard();
  renderInventory();
  renderOrders();
  renderReports();
  renderOperations();
}

function switchView(viewId) {
  document.querySelectorAll('.view').forEach((view) => view.classList.toggle('active-view', view.id === viewId));
  document.querySelectorAll('.nav-item').forEach((item) => item.classList.toggle('active', item.dataset.view === viewId));
  document.querySelector('#view-title').textContent = document.querySelector(`[data-view="${viewId}"]`).textContent;
}

function downloadCsv() {
  const header = ['date', 'platform', 'order_id', 'sku', 'revenue', 'cogs', 'profit'];
  const rows = filteredOrders().map((order) => [order.date, order.platform, order.orderId, order.sku, order.revenue, order.cogs, profit(order)]);
  const csv = [header, ...rows].map((row) => row.join(',')).join('\n');
  downloadFile('omni-report.csv', `\ufeff${csv}`, 'text/csv;charset=utf-8');
}

function downloadJson() {
  downloadFile('omni-erp-data.json', JSON.stringify(state, null, 2), 'application/json');
}

function downloadFile(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

document.querySelectorAll('.nav-item').forEach((item) => {
  item.addEventListener('click', () => switchView(item.dataset.view));
});

document.querySelector('#order-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  state.orders.push({
    date: form.get('orderDate'),
    platform: form.get('platform'),
    orderId: form.get('orderId'),
    sku: form.get('sku'),
    revenue: Number(form.get('revenue')),
    cogs: Number(form.get('cogs')),
  });
  saveState();
  event.currentTarget.reset();
  renderAll();
});

document.querySelector('#import-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const file = form.get('orderFile');
  const platform = form.get('platform');
  const status = document.querySelector('#import-status');

  if (!file || !file.name) {
    status.textContent = 'Chua chon file.';
    return;
  }

  if (window.location.protocol === 'file:') {
    status.textContent = 'Hay chay scripts/start-web.ps1 roi mo http://127.0.0.1:8765 de import XLSX.';
    return;
  }

  status.textContent = 'Dang import...';
  try {
    const response = await fetch(`/api/import/orders?platform=${encodeURIComponent(platform)}`, {
      method: 'POST',
      headers: { 'X-Filename': file.name },
      body: file,
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || 'Import failed');
    }
    state.orders.push(...payload.orders);
    saveState();
    renderAll();
    status.textContent = `Da import ${payload.count} dong don hang.`;
    event.currentTarget.reset();
  } catch (error) {
    status.textContent = `Loi import: ${error.message}`;
  }
});

document.querySelector('#reset-data').addEventListener('click', () => {
  state = structuredClone(seedData);
  saveState();
  renderAll();
});

document.querySelector('#export-json').addEventListener('click', downloadJson);
document.querySelector('#download-csv').addEventListener('click', downloadCsv);
document.querySelectorAll('#filter-start, #filter-end, #filter-platform').forEach((input) => {
  input.addEventListener('change', renderReports);
});

loadState().then(renderAll);
