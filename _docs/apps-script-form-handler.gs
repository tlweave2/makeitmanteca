/**
 * makeitmanteca.com — contact form handler
 *
 * Receives inquiries from the website, appends them to this spreadsheet, and emails a
 * notification to the Economic Development inbox. Deploy as a Web app with
 * "Execute as: Me" and "Who has access: Anyone". Setup: _docs/contact-form-setup.md
 */

var SHEET_ID = 'PASTE_SHEET_ID_HERE';
var TAB_NAME = 'Inquiries';
var NOTIFY = 'econdev@manteca.gov';

function doPost(e) {
  try {
    var p = (e && e.parameter) || {};

    var name = (p.Name || '').trim();
    var company = (p.Company || '').trim();
    var email = (p.Email || '').trim();
    var phone = (p.Phone || '').trim();
    var message = (p.Message || '').trim();

    // Drop empties and anything that tripped the honeypot on the page.
    if (p.Website) return json({ ok: true });
    if (!name && !email && !message) return json({ ok: false, error: 'empty' });

    SpreadsheetApp.openById(SHEET_ID)
      .getSheetByName(TAB_NAME)
      .appendRow([new Date(), name, company, email, phone, message]);

    var subject = 'makeitmanteca.com inquiry' + (company ? ' — ' + company : '');
    var body =
      'New inquiry from makeitmanteca.com\n\n' +
      'Name:    ' + name + '\n' +
      'Company: ' + company + '\n' +
      'Email:   ' + email + '\n' +
      'Phone:   ' + phone + '\n\n' +
      message + '\n';

    var opts = { to: NOTIFY, subject: subject, body: body };
    // Reply goes to the person who submitted, so staff can answer straight from the alert.
    if (email && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) opts.replyTo = email;
    MailApp.sendEmail(opts);

    return json({ ok: true });
  } catch (err) {
    // Logged to the Apps Script execution log; the site falls back to mailto on a non-200.
    console.error(err);
    return json({ ok: false, error: String(err) });
  }
}

function doGet() {
  return json({ ok: true, note: 'makeitmanteca.com form handler is deployed.' });
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
