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

### Which Google account should deploy it?

Any Google account can run this — personal Gmail, a contractor's Workspace account, or a
manteca.gov account. It will successfully email econdev@manteca.gov either way. But the
account you pick has consequences:

**The "From" address is the deploying account, and cannot be faked.** If a personal Gmail
deploys it, inquiries arrive at econdev from that Gmail address rather than from the City.
That looks like a phishing email — an outside personal address claiming to relay messages
from the public — and it is more likely to land in spam. It can be fixed, but only by adding
econdev@manteca.gov as a verified "Send mail as" alias in the deploying account, which
requires someone with access to the econdev mailbox to click Google's verification link. At
that point you may as well deploy from a City account.

**The inquiry Sheet lives in whichever account owns it.** Messages from the public to a City
department are very likely public records under the California Public Records Act. Keeping
them in a vendor's or an individual's personal Drive puts them outside the City's retention
and custody, and makes them awkward to produce on request.

**Continuity.** If the owning account is closed, its password changes, or a contract ends,
the form stops capturing and nobody finds out until someone notices the Sheet has gone quiet.
Lead capture for the City's investor site should not depend on an individual's account.

Recommended, in order:

1. A **manteca.gov account** owns the Sheet and the deployment. Cleanest on all three counts.
2. A **dedicated Google account created and owned by the City** specifically for this.
3. **Formspree instead** (Option B) — no Google account or Drive custody question at all,
   though it moves storage to a third party. A reasonable trade if getting a City-owned
   Google account is the blocker.

Deploying from a personal or contractor account is fine for a short-term test. It is not a
good place to leave it.

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
