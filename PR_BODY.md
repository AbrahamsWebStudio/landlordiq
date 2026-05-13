Title: feat: host vendor assets locally & harden MPesa webhook

Summary
-------
This branch prefers local vendor assets (lucide + local fonts) with CDN fallbacks, adds a local fonts loader, documents how to vendor assets, and hardens the M-Pesa callback handler with idempotency and optional HMAC verification.

Key changes
-----------
- `payments/views.py`: idempotent MPesa webhook, DB-atomic creation, optional HMAC verification via `MPESA_CALLBACK_SECRET`.
- `templates/base.html`: prefer local `static/vendor/lucide.min.js` and `static/css/fonts.css` with CDN fallbacks.
- `static/css/fonts.css`: local fonts loader and fallback font stack.
- `static/vendor/README.md`: instructions to vendor lucide and DM Sans fonts.
- `.gitignore`: ignore `.env` and common files.
- `README.md`, `DEVELOPER_FLASHDRIVE.md`, `.env.example`: onboarding and webhook docs updated.

Testing / verification
----------------------
1. Activate venv and install deps:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

2. Run checks and collect static:

```bash
python manage.py check
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

3. Seed dev data and run server:

```bash
python manage.py seed_test_data
python manage.py runserver
# visit http://127.0.0.1:8000 and confirm icons load from /static/vendor and fonts load (or fallback to Google Fonts)
```

4. MPesa callback testing (sandbox): simulate a successful callback payload and verify a single `Payment` is created; re-send the same payload and verify no duplicate payment.

Reviewer checklist
------------------
- [ ] Confirm `payments_payment` table has unique `mpesa_code` constraint and that duplicate callbacks do not create duplicate rows.
- [ ] Verify local vendor assets are present in `static/vendor` and `static/fonts` before merging to avoid CDN dependency.
- [ ] Ensure `.env` is not committed and secrets are rotated if they were previously exposed.

Notes
-----
If you prefer the assistant to commit actual font binaries, grant permission and indicate whether to add them to LFS or vendor them directly.
