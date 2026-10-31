// Google Sheets prijemnik za FEM landing stranice (bez Zapier-a).
// 1) Novi Google Sheet "FEM — Lista čekanja" > Extensions > Apps Script > nalepi ovo.
// 2) Deploy > New deployment > Web app > Execute as: Me, Who has access: Anyone > Deploy.
// 3) Dobijeni URL (https://script.google.com/macros/s/.../exec) upiši u CONFIG.formEndpoint na obe stranice.
function doPost(e) {
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getSheetByName('Prijave') || ss.insertSheet('Prijave');
  if (sh.getLastRow() === 0) sh.appendRow(['Vreme', 'Tip', 'Varijanta', 'Email', 'Gde kupuje', 'Zašto', 'Cena', 'Odgovor (cena ili kreatin)', 'Stranica', 'UTM']);
  var d = JSON.parse(e.postData.contents);
  sh.appendRow([new Date(), d.type || '', d.variant || '', d.email || '', d.kupuje || '', d.zasto || '', d.cena || '', d.odgovor || '', d.page || '', JSON.stringify(d.utm || {})]);
  return ContentService.createTextOutput('ok');
}
