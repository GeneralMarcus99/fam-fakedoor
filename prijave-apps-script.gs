// Procvat prijemnik v3.2 (test od 13.11.2026). Upisuje u list "Test 13.11" (QA probe u list "QA"). Stari listovi ostaju netaknuti.
// v3.2: posle prednarudžbine šalje potvrdni mejl sa procvat@tfnootropics.com (alias u Gmail-u: Send mail as).
// Zaštita: najviše 1 mejl po adresi na 6 h i najviše 300 mejlova dnevno. Ako slanje ne uspe, prijava je svejedno upisana.
// Ugradnja: u ISTOM Apps Script projektu zameni ceo kod ovim > Deploy > Manage deployments > olovka (Edit)
// > Version: New version > Deploy. URL ostaje isti, stranica ne mora da se menja. Objavljuje vlasnik Sheet-a.
// Cena se upisuje sa ' ispred, da Sheets "4.490" ne pretvori u broj 4,49.
// Pravljenje lista je pod zaključavanjem, da se ne izgubi prijava ako dve stignu istovremeno dok list još ne postoji.
var H_ = ['Vreme', 'Tip', 'Formula', 'Hook', 'Broj', 'Email', 'Odgovor', 'Cena', 'Stranica', 'UTM', 'Sekunde', 'Mejl'];
var FROM_ = 'procvat@tfnootropics.com';
var SASTAV_ = { kk: 'kreatin 3 g i kolagen 5 g', km: 'kreatin 3 g i maka 2 g', mk: 'kolagen 5 g i maka 2 g' };
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
  var mejl = '';
  if (d.type === 'prednarudzbina') mejl = posalji_(email, s_(d.broj, 20), String(d.variant).slice(2));
  sh.appendRow([new Date(), s_(d.type, 30), s_(d.variant, 10), s_(d.hook, 10), s_(d.broj, 20), s_(email, 120), s_(d.odgovor, 30), "'" + s_(d.cena, 10), s_(d.page, 60), s_(JSON.stringify(d.utm || {}), 300), s_(d.sek, 10), mejl]);
  return ContentService.createTextOutput('ok');
}
function posalji_(email, broj, f) {
  try {
    var c = CacheService.getScriptCache();
    if (c.get('m:' + email)) return 'preskočen (već poslat)';
    var dan = 'n:' + Utilities.formatDate(new Date(), 'Europe/Belgrade', 'yyyyMMdd');
    var n = Number(c.get(dan) || 0);
    if (n >= 300) return 'preskočen (dnevni limit)';
    var body = 'Dobrodošla u Procvat.\n\nTi si među prvima.\n\n'
      + 'U znak zahvalnosti dobijaš 10% popusta na prvu porudžbinu. Tvoj kod: ' + broj + '\n\n'
      + 'Pre lansiranja javljamo ti se sa konačnim sastavom, datumom i novostima.\n\n'
      + 'Ako se predomisliš, samo odgovori na ovaj mejl.\n\n'
      + 'Andrija, Procvat\nTF Nootropics d.o.o.';
    GmailApp.sendEmail(email, 'Dobrodošla u Procvat', body, { from: FROM_, name: 'Procvat', replyTo: FROM_, htmlBody: html_(broj) });
    c.put('m:' + email, '1', 21600);
    c.put(dan, String(n + 1), 21600);
    return 'poslat';
  } catch (err) {
    return 'greška: ' + String(err).slice(0, 80);
  }
}
// HTML verzija mejla (slike se učitavaju sa sajta lista.tfnootropics.com).
function html_(broj) {
  var k = String(broj).replace(/[^A-Za-z0-9\-]/g, '');
  var S = 'https://lista.tfnootropics.com';
  return '<div style="display:none;max-height:0;overflow:hidden">Ti si među prvima. Tvoj kod za 10% popusta je unutra.</div>'
    + '<div style="background:#e7e4df;padding:24px 12px;font-family:Helvetica,Arial,sans-serif;color:#1e1a1f">'
    + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:#f6f5f2;border-radius:14px;overflow:hidden">'
    + '<tr><td style="padding:20px 28px 16px"><img src="' + S + '/znak-180.png" width="28" height="28" alt="" style="vertical-align:middle;border:0">'
    + '<span style="font-size:14px;letter-spacing:4px;color:#5B2A4E;vertical-align:middle;margin-left:10px">PROCVAT</span></td></tr>'
    + '<tr><td><img src="' + S + '/mejl/dobrodosla.jpg?v=2" width="560" alt="" style="display:block;width:100%;height:auto;border:0"></td></tr>'
    + '<tr><td style="padding:28px 28px 0"><p style="margin:0 0 8px;font-size:13px;letter-spacing:2px;color:#a9834a;text-transform:uppercase">Dobrodošla u Procvat</p>'
    + '<h1 style="margin:0;font-size:32px;line-height:1.15;color:#5B2A4E;font-weight:700">Ti si među prvima.</h1></td></tr>'
    + '<tr><td style="padding:14px 28px 0;font-size:16px;line-height:1.55">U znak zahvalnosti dobijaš 10% popusta na prvu porudžbinu.</td></tr>'
    + '<tr><td style="padding:18px 28px"><div style="border:1.5px solid #a9834a;border-radius:10px;padding:14px 18px;text-align:center">'
    + '<div style="font-size:12px;letter-spacing:2px;color:#5d575e;text-transform:uppercase">Tvoj kod</div>'
    + '<div style="font-size:24px;font-weight:700;letter-spacing:2px;color:#5B2A4E;margin-top:4px">' + k + '</div></div></td></tr>'
    + '<tr><td style="padding:0 28px;font-size:16px;line-height:1.55">Pre lansiranja javljamo ti se sa konačnim sastavom, datumom i novostima.</td></tr>'
    + '<tr><td style="padding:14px 28px 0;font-size:14px;line-height:1.5;color:#5d575e">Ako se predomisliš, samo odgovori na ovaj mejl.</td></tr>'
    + '<tr><td style="padding:24px 28px 28px;font-size:15px;line-height:1.5">Andrija, Procvat<br><span style="color:#5d575e;font-size:13px">TF Nootropics d.o.o.</span></td></tr>'
    + '</table></div>';
}
// Pokreni jednom iz editora (izaberi funkciju "proba" > Run > autorizuj) pre Deploy-a: traži dozvolu za Gmail i šalje probni mejl na team@.
function proba() { CacheService.getScriptCache().remove('m:team@tfnootropics.com'); Logger.log(posalji_('team@tfnootropics.com', 'PRC-PROBA', 'kk')); }
