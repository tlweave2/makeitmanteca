# Turning on the contact form

The form on makeitmanteca.com does **not** capture inquiries yet. Until an endpoint is
configured it falls back to opening a pre-filled message in the visitor's own mail client —
that works, but they have to press send, and nothing is logged anywhere.

To turn on real submissions, open `index.html`, find `FORM_ENDPOINT` near the bottom, and
paste in a URL:

```js
var FORM_ENDPOINT = 'https://...';
```

That's the only change needed. Pick one of the two options below.

---

## Option A — Google Apps Script (recommended for the City)

Inquiries land in a Google Sheet **inside the City's own Google account** and are emailed to
econdev@manteca.gov. Nothing passes through a third-party vendor, which matters for a .gov
site: no new data-processing agreement, and the records stay where the City's retention
policy already applies. Free, no submission cap.

Tradeoff: takes ~10 minutes and needs someone with a manteca.gov Google account.

1. Create a new Google Sheet in the City's account. Name the first tab `Inquiries`.
   Put these headers in row 1:
   `Timestamp | Name | Company | Email | Phone | Message`
2. Copy the Sheet's ID out of its URL — the long string between `/d/` and `/edit`.
3. In the Sheet, go to **Extensions → Apps Script**. Delete the placeholder code and paste
   in the contents of `_docs/apps-script-form-handler.gs` from this repo.
4. Replace `PASTE_SHEET_ID_HERE` at the top with the ID from step 2.
5. Click **Deploy → New deployment**. Set:
   - Type: **Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**  ← required; "Anyone with Google account" will not work
     for public website visitors
6. Authorize when prompted. Google will warn that the script is unverified — that's normal
   for an internal script; continue.
7. Copy the **Web app URL** (ends in `/exec`) and paste it into `FORM_ENDPOINT`.

To change where the notification email goes, edit `NOTIFY` in the script.

---

## Option B — Formspree (fastest)

Fine if you want this working in the next five minutes, or as a stopgap while IT reviews
Option A.

1. Sign up at formspree.io and create a new form.
2. Set the destination email to econdev@manteca.gov and confirm the verification email.
3. Copy the endpoint (`https://formspree.io/f/xxxxxxxx`) into `FORM_ENDPOINT`.

Worth knowing before you pick this: the free tier caps at 50 submissions/month, and
inquiries pass through and are stored on Formspree's servers. For a City site that's worth a
quick check with IT — it's a third-party processor holding correspondence from the public.

---

## Testing it

After setting `FORM_ENDPOINT`, submit a test inquiry from the live site and confirm:

- the form clears and shows the green "Thank you" confirmation
- the row appears in the Sheet (Option A) or the Formspree dashboard (Option B)
- the notification email arrives at econdev@manteca.gov
- **reply to that email** and confirm it goes back to the person who submitted, not to
  yourself — both options set the reply-to to the submitter's address

If the endpoint is wrong or unreachable, the form says so and falls back to the visitor's
mail client rather than failing silently.

## Spam

The form has a hidden honeypot field; submissions that fill it are dropped in the browser
before anything is sent. That handles most drive-by bots. If real spam starts arriving, add
Formspree's built-in reCAPTCHA (Option B) or a similar check in the Apps Script (Option A) —
don't add a captcha pre-emptively, it costs real inquiries.
