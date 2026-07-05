const OMNI_SHEETS = [
  'products',
  'sku_mapping',
  'warehouses',
  'suppliers',
  'inventory_lots',
  'settings',
];

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('OMNI ERP')
    .addItem('Setup Sheets', 'setupOmniSheets')
    .addItem('Refresh Dashboard', 'refreshOmniDashboard')
    .addItem('Create Backup Marker', 'createBackupMarker')
    .addToUi();
}

function setupOmniSheets() {
  const spreadsheet = SpreadsheetApp.getActive();
  OMNI_SHEETS.forEach((sheetName) => {
    if (!spreadsheet.getSheetByName(sheetName)) {
      spreadsheet.insertSheet(sheetName);
    }
  });
}

function refreshOmniDashboard() {
  const spreadsheet = SpreadsheetApp.getActive();
  const sheet = spreadsheet.getSheetByName('dashboard') || spreadsheet.insertSheet('dashboard');
  sheet.getRange('A1').setValue('Last refreshed');
  sheet.getRange('B1').setValue(new Date());
}

function createBackupMarker() {
  const spreadsheet = SpreadsheetApp.getActive();
  const sheet = spreadsheet.getSheetByName('settings') || spreadsheet.insertSheet('settings');
  sheet.appendRow(['last_backup_marker', new Date(), 'Created from OMNI ERP Apps Script menu']);
}
