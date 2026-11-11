// FEM prijemnik v3.1 (test od 13.11.2026). Upisuje u list "Test 13.11" (QA probe u list "QA"). Stari listovi ostaju netaknuti.
// Ugradnja: u ISTOM Apps Script projektu zameni ceo kod ovim > Deploy > Manage deployments > olovka (Edit)
// > Version: New version > Deploy. URL ostaje isti, stranica ne mora da se menja. Objavljuje vlasnik Sheet-a.
// Cena se upisuje sa ' ispred, da Sheets "4.490" ne pretvori u broj 4,49.
// Pravljenje lista je pod zaključavanjem, da se ne izgubi prijava ako dve stignu istovremeno dok list još ne postoji.
var H_ = ['Vreme', 'Tip', 'Formula', 'Hook', 'Broj', 'Email', 'Odgovor', 'Cena', 'Stranica', 'UTM', 'Sekunde'];
function s_(x, n) { x = String(x == null ? '' : x).slice(0, n || 100); return /^[=+\-@]/.test(x) ? "'" + x : x; }
function doPost(e) {
  var d;
  try { d = JSON.parse(e.postData.contents); } catch (err) { return ContentService.createTextOutput('bad'); }
  if (d.hp) return ContentService.createTextOutput('ok');
  if (String(d.variant || '').indexOf('F-') !== 0) return ContentService.createTextOutput('bad');
  var email = String(d.email || '').trim().toLowerCase();
  if (d.type === 'prednarudzbina' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return ContentService.createTextOutput('bad');
  var ss = SpreadsheetApp.getActive();
  var name = d.qa ? 'QA' : 'Test 13.11';
  var sh = ss.getSheetByName(name);
  if (!sh || sh.getLastRow() === 0) {
    var lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      sh = ss.getSheetByName(name) || ss.insertSheet(name);
      if (sh.getLastRow() === 0) sh.appendRow(H_);
    } finally { lock.releaseLock(); }
  }
  sh.appendRow([new Date(), s_(d.type, 30), s_(d.variant, 10), s_(d.hook, 10), s_(d.broj, 20), s_(email, 120), s_(d.odgovor, 30), "'" + s_(d.cena, 10), s_(d.page, 60), s_(JSON.stringify(d.utm || {}), 300), s_(d.sek, 10)]);
  return ContentService.createTextOutput('ok');
}
