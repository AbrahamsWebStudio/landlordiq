LandlordIQ — Technical Handover
=================================

Date: 2026-05-05

Purpose
-------
- This document hands over the LandlordIQ codebase to the next development/operations team. It summarizes what was implemented, how to run it, current caveats, and recommended next steps.

What was delivered
------------------
- Tenant & Lease management (`tenants/`): tenant records, `Lease` model with `monthly_rent`, `rent_due_day`, `status`, `total_paid` and `balance` helpers. See `tenants/models.py`.
- Property & Unit (`properties/`): `Property` and `Unit` with `default_rent` (unit-level suggestion). See `properties/models.py`.
- Utilities billing (`utilities/`): `ServiceCharge`, `UnitServiceSubscription`, `ServiceUsage`. `ServiceUsage.save()` computes `billed_amount` (metered vs fixed). See `utilities/models.py`.
- Invoice-as-master-bill (`payments/`): `Invoice` aggregates `rent_amount`, `charges_amount`, `total_amount`, `amount_paid`, `status`. `Payment` links to `Invoice` and `Payment.save()` reconciles `Invoice.amount_paid` from `is_confirmed=True` payments. See `payments/models.py`.
- Recurring invoice engine: `payments/invoice_engine.py` contains `generate_invoice_for_lease` and `generate_all_invoices` (monthly invoice generator).
- MPesa callback: `payments/views.py` implements `mpesa_callback` that accepts Safaricom STK responses and creates confirmed `Payment` records for successful callbacks.
- Seeders: `utilities` management commands `seed_services` and `seed_test_data` (used to provision demo data).

Current repo state (what I left)
--------------------------------
- Core apps: `core/`, `tenants/`, `properties/`, `payments/`, `utilities/`, `dashboard/` (models, views, admin, templates remain intact).
- Migrations: initial migrations for the apps are present in each app's `migrations/` folder.
- Tests: placeholder/temporary tests were removed per request; add tests back into `tests/` when needed.
- Helper scripts: local automation scripts were removed to keep repo minimal; if you want them preserved, they can be restored from the branch history.

How to run locally (developer quick start)
-----------------------------------------
1. Create and activate venv:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

2. Build CSS (if desired):

```bash
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
```

3. Database & migrations

Note: The reset approach below is destructive. Use in local/demo only.

```bash
# (Optional) As postgres superuser - drop & recreate DB
sudo -u postgres psql -c "DROP DATABASE IF EXISTS landlordiq_db;"
sudo -u postgres psql -c "CREATE DATABASE landlordiq_db OWNER abraham;"

export PGPASSWORD='your_db_password'
venv/bin/python manage.py makemigrations tenants properties utilities payments --noinput
venv/bin/python manage.py migrate --noinput

# Ensure superuser
venv/bin/python - <<'PY'
from django.contrib.auth import get_user_model
U = get_user_model()
if not U.objects.filter(username='admin').exists():
    U.objects.create_superuser('admin','admin@example.com','adminpass')
print('superuser ensured')
PY

# Seed demo data
venv/bin/python manage.py seed_services
venv/bin/python manage.py seed_test_data
```

Testing
-------
- Run test suite: `venv/bin/python manage.py test` (note: tests were removed to keep the repo minimal; add tests under each app's `tests.py` as needed).

MPesa webhook (integration details)
-----------------------------------
- Endpoint: `payments.views.mpesa_callback` expects a Safaricom STK JSON payload. On success (`ResultCode == 0`) it extracts `MpesaReceiptNumber`, `Amount`, and `CheckoutRequestID` and creates a `Payment` record with `is_confirmed=True`.
- Payment reconciliation: `Payment.save()` recalculates `Invoice.amount_paid` using only `is_confirmed=True` payments. Document this workflow to avoid confusion (created vs confirmed states).

Operational cautions & security
-------------------------------
- Secrets: Removed plaintext `property management cred` and transient `scripts/action_log.txt`. Rotate any leaked secrets immediately. Add `.env` and similar files to `.gitignore` and use `.env.example` for onboarding.
- DB destructive reset: In production, do not use drop/recreate. Instead prepare migration scripts and backups.

Known issues & follow-ups
------------------------
- MPesa webhook: logging and error monitoring need to be added so that failed internal processing is surfaced (current handler returns success to Safaricom even on internal errors to avoid retries).
- Add integration tests for the MPesa webhook and scheduled invoice generation.
- Add CI with `makemigrations --check` and tests on PRs.

Files I removed
---------------
- `property management cred` (sensitive)
- `scripts/action_log.txt` (transient)
- some temporary tests and helper scripts (per your request). See `HANDBOOK.md` for the itemized removals.

Next recommended actions (priority)
----------------------------------
1. Add `.env.example` and `SECURITY.md` to standardize secret handling.
2. Add CI to run `manage.py test` and `makemigrations --check`.
3. Add logging & monitoring for `mpesa_callback` and failed payment reconciliations.
4. Create an integration test for webhook and scheduled invoice run.

Recent fixes
------------
- 2026-05-06: Added a basic `maintenance` URL, view, and template to resolve a NoReverseMatch error in the dashboard navigation. The new route is `maintenance/` and is named `maintenance`. The placeholder view renders `templates/maintenance/index.html`.
- 2026-05-06: Fixed dashboard bottom navigation link to payments ledger — template now uses the existing `tenant_ledger` URL name (`/payments/ledger/`) to avoid a NoReverseMatch for `payments_ledger`.
Contact
-------
- For follow-ups, open an issue in the repo or ask me to open a PR with any of the recommended items.
