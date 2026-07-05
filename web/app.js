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
  orderHeaders: ['Ngay', 'San', 'Ma don', 'SKU', 'Doanh thu', 'Gia von', 'Loi nhuan'],
  orderRows: [
    { Ngay: '2026-07-01', San: 'Shopee', 'Ma don': 'SHP-1001', SKU: 'SKU-RED', 'Doanh thu': 240000, 'Gia von': 110000, 'Loi nhuan': 130000 },
    { Ngay: '2026-07-02', San: 'TikTok Shop', 'Ma don': 'TT-1001', SKU: 'SKU-BLUE', 'Doanh thu': 320000, 'Gia von': 145000, 'Loi nhuan': 175000 },
    { Ngay: '2026-07-03', San: 'Lazada', 'Ma don': 'LZD-1001', SKU: 'SKU-GREEN', 'Doanh thu': 180000, 'Gia von': 76000, 'Loi nhuan': 104000 },
    { Ngay: '2026-07-04', San: 'Shopee', 'Ma don': 'SHP-1002', SKU: 'SKU-RED', 'Doanh thu': 135000, 'Gia von': 62000, 'Loi nhuan': 73000 },
  ],
  automations: [
    { task: 'Sync marketplace orders', schedule: 'Daily 07:00', status: 'Ready' },
    { task: 'Refresh dashboard', schedule: 'Daily 07:15', status: 'Ready' },
    { task: 'Create backup', schedule: 'Daily 23:30', status: 'Ready' },
  ],
};

const headerAliases = {
  date: ['order_date', 'date', 'ngay', 'Ngày đặt hàng', 'Order Creation Date', 'Created Time', 'createTime'],
  platform: ['platform', 'san', 'marketplace'],
  orderId: ['order_id', 'orderId', 'ma_don', 'Mã đơn hàng', 'Order ID', 'orderItemId'],
  sku: ['sku', 'internal_sku', 'SKU phân loại hàng', 'SKU sản phẩm', 'SKU Reference No.', 'Seller SKU', 'sellerSku', 'Tên phân loại hàng', 'Tên sản phẩm'],
  revenue: [
    'revenue',
    'gross_revenue',
    'doanh_thu',
    'Product Subtotal',
    'Subtotal',
    'itemPrice',
    'Order Total',
    'Order Amount',
    'paidPrice',
    'Tổng giá trị đơn hàng (VND)',
    'Tổng số tiền Người mua thanh toán',
    'Tổng số tiền người mua thanh toán',
  ],
  cogs: ['cogs', 'cost_of_goods_sold', 'gia_von', 'Gia von'],
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

function ensureStateShape() {
  state.orderHeaders = Array.isArray(state.orderHeaders) ? state.orderHeaders : structuredClone(seedData.orderHeaders);
  state.orderRows = Array.isArray(state.orderRows) ? state.orderRows : rowsFromNormalizedOrders(state.orders);
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
  ensureStateShape();
  document.querySelector('#orders-table-head').innerHTML = `<tr>${state.orderHeaders.map((header) => `<th>${escapeHtml(header)}</th>`).join('')}</tr>`;
  document.querySelector('#orders-table').innerHTML = state.orderRows
    .map((row) => `<tr>${state.orderHeaders.map((header) => `<td>${escapeHtml(row[header] ?? '')}</td>`).join('')}</tr>`)
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
  appendOrderTableRows({
    headers: seedData.orderHeaders,
    rows: [
      {
        Ngay: form.get('orderDate'),
        San: form.get('platform'),
        'Ma don': form.get('orderId'),
        SKU: form.get('sku'),
        'Doanh thu': Number(form.get('revenue')),
        'Gia von': Number(form.get('cogs')),
        'Loi nhuan': Number(form.get('revenue')) - Number(form.get('cogs')),
      },
    ],
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

  status.textContent = 'Dang import...';
  try {
    const importResult = await importOrderFile(file, platform);
    const importedOrders = importResult.orders;
    state.orders.push(...importedOrders);
    appendOrderTableRows(importResult);
    saveState();
    renderAll();
    status.textContent = `Da import ${importedOrders.length} dong don hang (${importResult.mode}).`;
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

async function importOrderFile(file, platform) {
  try {
    return { ...(await importOrderFileInBrowser(file, platform)), mode: 'browser' };
  } catch (browserError) {
    if (window.location.protocol === 'file:') {
      throw browserError;
    }

    try {
      return { ...(await importOrderFileOnServer(file, platform)), mode: 'server fallback' };
    } catch {
      throw browserError;
    }
  }
}

async function importOrderFileOnServer(file, platform) {
  const response = await fetch(`/api/import/orders?platform=${encodeURIComponent(platform)}`, {
    method: 'POST',
    headers: { 'X-Filename': file.name },
    body: file,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || 'Import failed');
  }
  return {
    orders: payload.orders || [],
    headers: payload.headers || [],
    rows: payload.rows || [],
  };
}

async function importOrderFileInBrowser(file, platform) {
  const lowerName = file.name.toLowerCase();
  if (lowerName.endsWith('.csv')) {
    const parsed = parseCsv(await file.text());
    return { ...parsed, orders: normalizeRows(parsed.rows, platform) };
  }
  if (lowerName.endsWith('.xlsx')) {
    const parsed = await parseXlsx(await file.arrayBuffer());
    return { ...parsed, orders: normalizeRows(parsed.rows, platform) };
  }
  throw new Error('Chi ho tro file .xlsx hoac .csv');
}

function parseCsv(text) {
  const lines = text.replace(/^\ufeff/, '').split(/\r?\n/).filter((line) => line.trim());
  if (!lines.length) return { headers: [], rows: [] };
  const headers = splitCsvLine(lines[0]);
  const rows = lines.slice(1).map((line) => {
    const values = splitCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, values[index] || '']));
  });
  return { headers, rows };
}

function splitCsvLine(line) {
  const values = [];
  let value = '';
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"' && line[index + 1] === '"') {
      value += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === ',' && !quoted) {
      values.push(value.trim());
      value = '';
    } else {
      value += char;
    }
  }
  values.push(value.trim());
  return values;
}

async function parseXlsx(arrayBuffer) {
  const entries = await unzipEntries(arrayBuffer);
  const sharedStrings = parseSharedStrings(entries.get('xl/sharedStrings.xml') || '');
  const sheetXml = sheetWithMostRows(entries);
  if (!sheetXml) throw new Error('File XLSX khong co worksheet');

  const doc = new DOMParser().parseFromString(sheetXml, 'application/xml');
  const rowNodes = Array.from(doc.getElementsByTagNameNS('*', 'row'));
  const rows = rowNodes.map((rowNode) => {
    const values = [];
    Array.from(rowNode.getElementsByTagNameNS('*', 'c')).forEach((cell) => {
      const cellRef = cell.getAttribute('r') || '';
      const index = columnIndex(cellRef);
      values[index] = cellValue(cell, sharedStrings);
    });
    return values.map((value) => value || '');
  });

  if (!rows.length) return { headers: [], rows: [] };
  const headers = rows[0].map((header) => header.trim());
  return {
    headers,
    rows: rows.slice(1).map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] || '']).filter(([header]) => header))),
  };
}

function sheetWithMostRows(entries) {
  const sheets = Array.from(entries.entries()).filter(([name]) => name.startsWith('xl/worksheets/') && name.endsWith('.xml'));
  if (!sheets.length) return '';
  return sheets.sort((a, b) => countRows(b[1]) - countRows(a[1]))[0][1];
}

function countRows(xml) {
  return (xml.match(/<row\b/g) || []).length;
}

function parseSharedStrings(xml) {
  if (!xml) return [];
  const doc = new DOMParser().parseFromString(xml, 'application/xml');
  return Array.from(doc.getElementsByTagNameNS('*', 'si')).map((item) =>
    Array.from(item.getElementsByTagNameNS('*', 't'))
      .map((node) => node.textContent || '')
      .join(''),
  );
}

function cellValue(cell, sharedStrings) {
  const type = cell.getAttribute('t');
  if (type === 'inlineStr') {
    return Array.from(cell.getElementsByTagNameNS('*', 't'))
      .map((node) => node.textContent || '')
      .join('');
  }
  const value = cell.getElementsByTagNameNS('*', 'v')[0]?.textContent || '';
  if (type === 's') return sharedStrings[Number(value)] || '';
  return value;
}

async function unzipEntries(arrayBuffer) {
  const view = new DataView(arrayBuffer);
  const entries = new Map();
  const centralEntries = centralDirectoryEntries(arrayBuffer);

  for (const entry of centralEntries) {
    if (!entry.fileName.endsWith('.xml')) continue;
    const localOffset = entry.localHeaderOffset;
    const signature = view.getUint32(localOffset, true);
    if (signature !== 0x04034b50) throw new Error('File XLSX bi loi local header');
    const fileNameLength = view.getUint16(localOffset + 26, true);
    const extraLength = view.getUint16(localOffset + 28, true);
    const dataStart = localOffset + 30 + fileNameLength + extraLength;
    const compressed = arrayBuffer.slice(dataStart, dataStart + entry.compressedSize);
    entries.set(entry.fileName, await inflateZipEntry(compressed, entry.compressionMethod));
  }

  if (entries.size > 0) return entries;

  let offset = 0;
  while (offset + 30 <= view.byteLength) {
    const signature = view.getUint32(offset, true);
    if (signature !== 0x04034b50) break;

    const compressionMethod = view.getUint16(offset + 8, true);
    const compressedSize = view.getUint32(offset + 18, true);
    const fileNameLength = view.getUint16(offset + 26, true);
    const extraLength = view.getUint16(offset + 28, true);
    const nameStart = offset + 30;
    const dataStart = nameStart + fileNameLength + extraLength;
    const fileName = new TextDecoder().decode(new Uint8Array(arrayBuffer, nameStart, fileNameLength));
    const compressed = arrayBuffer.slice(dataStart, dataStart + compressedSize);

    if (fileName.endsWith('.xml')) {
      entries.set(fileName, await inflateZipEntry(compressed, compressionMethod));
    }
    offset = dataStart + compressedSize;
  }
  return entries;
}

function centralDirectoryEntries(arrayBuffer) {
  const view = new DataView(arrayBuffer);
  const entries = [];
  const eocdOffset = endOfCentralDirectoryOffset(view);
  if (eocdOffset < 0) return entries;

  const centralDirectorySize = view.getUint32(eocdOffset + 12, true);
  const centralDirectoryOffset = view.getUint32(eocdOffset + 16, true);
  let offset = centralDirectoryOffset;
  const endOffset = centralDirectoryOffset + centralDirectorySize;

  while (offset + 46 <= endOffset && view.getUint32(offset, true) === 0x02014b50) {
    const compressionMethod = view.getUint16(offset + 10, true);
    const compressedSize = view.getUint32(offset + 20, true);
    const fileNameLength = view.getUint16(offset + 28, true);
    const extraLength = view.getUint16(offset + 30, true);
    const commentLength = view.getUint16(offset + 32, true);
    const localHeaderOffset = view.getUint32(offset + 42, true);
    const fileName = new TextDecoder().decode(new Uint8Array(arrayBuffer, offset + 46, fileNameLength));
    entries.push({ fileName, compressionMethod, compressedSize, localHeaderOffset });
    offset += 46 + fileNameLength + extraLength + commentLength;
  }

  return entries;
}

function endOfCentralDirectoryOffset(view) {
  const minimumOffset = Math.max(0, view.byteLength - 65557);
  for (let offset = view.byteLength - 22; offset >= minimumOffset; offset -= 1) {
    if (view.getUint32(offset, true) === 0x06054b50) return offset;
  }
  return -1;
}

async function inflateZipEntry(arrayBuffer, compressionMethod) {
  if (compressionMethod === 0) {
    return new TextDecoder().decode(arrayBuffer);
  }
  if (compressionMethod !== 8) {
    throw new Error(`Khong ho tro compression method ${compressionMethod}`);
  }
  if (!('DecompressionStream' in window)) {
    throw new Error('Trinh duyet nay chua ho tro giai nen XLSX truc tiep. Hay dung scripts/start-web.ps1.');
  }

  const stream = new Blob([arrayBuffer]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
  return await new Response(stream).text();
}

function columnIndex(reference) {
  const letters = reference.replace(/[^A-Za-z]/g, '').toUpperCase();
  let index = 0;
  for (const letter of letters) {
    index = index * 26 + letter.charCodeAt(0) - 64;
  }
  return Math.max(index - 1, 0);
}

function normalizeRows(rows, platform) {
  return rows
    .map((row) => ({
      date: normalizeDate(pick(row, 'date')),
      platform: pick(row, 'platform') || platform || 'Unknown',
      orderId: pick(row, 'orderId'),
      sku: pick(row, 'sku'),
      revenue: numberValue(pick(row, 'revenue')),
      cogs: numberValue(pick(row, 'cogs')),
    }))
    .filter((order) => order.orderId && order.sku);
}

function pick(row, field) {
  const normalized = Object.fromEntries(Object.entries(row).map(([key, value]) => [key.trim().toLowerCase(), String(value || '').trim()]));
  for (const alias of headerAliases[field]) {
    const value = normalized[alias.toLowerCase()];
    if (value) return value;
  }
  return '';
}

function normalizeDate(value) {
  if (!value) return new Date().toISOString().slice(0, 10);
  if (/^\d+(\.\d+)?$/.test(value)) {
    const date = new Date(Date.UTC(1899, 11, 30));
    date.setUTCDate(date.getUTCDate() + Number(value));
    return date.toISOString().slice(0, 10);
  }
  const dayMonthYear = value.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/);
  if (dayMonthYear) {
    return `${dayMonthYear[3]}-${dayMonthYear[2].padStart(2, '0')}-${dayMonthYear[1].padStart(2, '0')}`;
  }
  return value.slice(0, 10);
}

function numberValue(value) {
  const cleaned = String(value || '')
    .replaceAll(',', '')
    .replaceAll('VND', '')
    .replaceAll('₫', '')
    .trim();
  const parsed = Number(cleaned);
  return Number.isFinite(parsed) ? Math.round(parsed) : 0;
}

function appendOrderTableRows(importResult) {
  const headers = Array.isArray(importResult.headers) ? importResult.headers.filter(Boolean) : [];
  const rows = Array.isArray(importResult.rows) ? importResult.rows : [];
  if (!headers.length || !rows.length) return;

  state.orderHeaders = mergeHeaders(state.orderHeaders || [], headers);
  state.orderRows = [...(state.orderRows || []), ...rows];
}

function mergeHeaders(existingHeaders, newHeaders) {
  const merged = [...existingHeaders];
  newHeaders.forEach((header) => {
    if (!merged.includes(header)) merged.push(header);
  });
  return merged;
}

function rowsFromNormalizedOrders(orders) {
  return orders.map((order) => ({
    Ngay: order.date,
    San: order.platform,
    'Ma don': order.orderId,
    SKU: order.sku,
    'Doanh thu': order.revenue,
    'Gia von': order.cogs,
    'Loi nhuan': profit(order),
  }));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}
