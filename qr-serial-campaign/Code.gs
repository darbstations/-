/**
 * توزيع سيريال نمبر فريد لكل عميل يعبّي جوجل فورم الشريك.
 *
 * الإعداد:
 * 1) افتح Google Sheet المرتبط بالفورم (الردود).
 * 2) أضف ورقة باسم "Serials" وفيها:  A = Serial  |  B = Status  |  C = Email  |  D = Date
 *    والصق سيريالات الشريك في العمود A بدءاً من الصف 2.
 * 3) Extensions > Apps Script والصق هذا الملف، وعدّل الإعدادات تحت.
 * 4) شغّل الدالة setup() مرة وحدة ووافق على الصلاحيات.
 */

const CONFIG = {
  SERIALS_SHEET: 'Serials',
  EMAIL_QUESTION: 'البريد الإلكتروني', // عنوان سؤال الإيميل في الفورم بالضبط
  NAME_QUESTION: 'الاسم',             // اختياري
  EMAIL_SUBJECT: 'رقمك التسلسلي من حملة الشريك',
  ALLOW_DUPLICATE_EMAIL: false,        // false = العميل ياخذ سيريال واحد فقط حتى لو عبّى أكثر من مرة
  LOW_STOCK_ALERT: 20,                 // تنبيه لك لما يقل المتبقي عن هذا الرقم
};

function setup() {
  const ss = SpreadsheetApp.getActive();
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('onFormSubmit').forSpreadsheet(ss).onFormSubmit().create();
}

function onFormSubmit(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000); // يمنع إن عميلين ياخذون نفس السيريال لو سجّلوا بنفس اللحظة
  try {
    const answers = e.namedValues;
    const email = String((answers[CONFIG.EMAIL_QUESTION] || [''])[0]).trim().toLowerCase();
    const name = String((answers[CONFIG.NAME_QUESTION] || [''])[0]).trim();
    if (!email) return;

    const sheet = SpreadsheetApp.getActive().getSheetByName(CONFIG.SERIALS_SHEET);
    const last = sheet.getLastRow();
    if (last < 2) return notifyOwner_('خلصت السيريالات!');
    const data = sheet.getRange(2, 1, last - 1, 3).getValues();

    if (!CONFIG.ALLOW_DUPLICATE_EMAIL) {
      const prev = data.find(r => String(r[2]).toLowerCase() === email);
      if (prev) return sendSerial_(email, name, prev[0], true);
    }

    const idx = data.findIndex(r => r[0] && !r[1]);
    if (idx === -1) return notifyOwner_('خلصت السيريالات! عميل ما استلم: ' + email);

    const row = idx + 2;
    sheet.getRange(row, 2, 1, 3).setValues([['USED', email, new Date()]]);
    SpreadsheetApp.flush();

    // نكتب السيريال جنب رد العميل في ورقة الردود
    const resp = e.range.getSheet();
    let col = resp.getRange(1, 1, 1, resp.getLastColumn()).getValues()[0].indexOf('Serial') + 1;
    if (!col) { col = resp.getLastColumn() + 1; resp.getRange(1, col).setValue('Serial'); }
    resp.getRange(e.range.getRow(), col).setValue(data[idx][0]);

    sendSerial_(email, name, data[idx][0], false);

    const remaining = data.filter(r => r[0] && !r[1]).length - 1;
    if (remaining === CONFIG.LOW_STOCK_ALERT) notifyOwner_('باقي ' + remaining + ' سيريال فقط');
  } finally {
    lock.releaseLock();
  }
}

function sendSerial_(email, name, serial, again) {
  const html =
    '<div dir="rtl" style="font-family:Tahoma,Arial;font-size:16px">' +
    '<p>أهلاً ' + (name || '') + '،</p>' +
    '<p>' + (again ? 'سبق وسجّلت معنا، وهذا رقمك:' : 'شكراً لتسجيلك! رقمك التسلسلي:') + '</p>' +
    '<p style="font-size:28px;font-weight:bold;letter-spacing:2px">' + serial + '</p>' +
    '</div>';
  MailApp.sendEmail({ to: email, subject: CONFIG.EMAIL_SUBJECT, htmlBody: html });
}

function notifyOwner_(msg) {
  MailApp.sendEmail(Session.getEffectiveUser().getEmail(), 'تنبيه حملة السيريالات', msg);
}
