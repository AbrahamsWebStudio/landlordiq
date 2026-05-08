LandlordIQ — Client Brief
==========================

Date: 2026-05-05

Executive summary
-----------------
LandlordIQ is a lightweight property management web app built with Django and PostgreSQL. The delivered features include tenant and lease management, unit/property management, automated monthly invoice generation, utility billing (metered and fixed), and MPesa payment reconciliation for received mobile payments.

What this release provides (business view)
-----------------------------------------
- Tenant & Lease management: create and track tenants, link leases to units, and view ledger balances.
- Rent invoicing: monthly invoices are generated per active lease (rent + utility charges aggregated into a single master invoice).
- Utilities billing: per-unit subscriptions to services (e.g., water, trash, security); metered usage and fixed charges supported.
- MPesa payments: automatic webhook processing that records successful payments and reconciles invoices when payments are confirmed.
- Demo data seeds: easy provisioning of demo properties, tenants, and subscriptions for demonstrations.

How clients use it (typical flow)
--------------------------------
1. Operator (admin) provisions a property and units, creates a tenant and a lease with `monthly_rent`.
2. On the 1st of the month, run the invoice engine (or schedule it) to generate invoices for active leases.
3. Tenants pay via MPesa; the MPesa webhook will mark payments as confirmed and update invoice statuses.

Business benefits
-----------------
- Consolidates rent + utilities into a single invoice per tenant — simplifies reconciliation and tenant communication.
- Supports metered billing for utilities so tenants are billed for actual usage.
- Enables mobile-money payments (MPesa) for fast reconciliation.

Limitations & immediate risks
-----------------------------
- MPesa webhook currently swallows internal errors (returns success to Safaricom to stop retries). We must add logging and alerting to detect processing failures.
- The destructive DB reset approach used during handover is NOT safe for production — migrations should be authored for live upgrades.
- No tenant-facing portal or notification/emailing system included — invoices are generated server-side only.

Recommended next steps (business + delivery)
-------------------------------------------
Short term (2–4 days)
- Add monitoring/logging for MPesa webhook and payment reconciliation. Add a small health endpoint for payments.
- Add `.env.example` and rotate any credentials that were removed.

Medium term (2–4 weeks)
- Implement scheduled automation (cron/worker) to run `generate_all_invoices` monthly and a retryable background job for webhook processing.
- Add tenant portal (view invoices, confirm payments) and email/SMS notifications for invoices and receipts.

Long term (1–3 months)
- Hardening & security: deploy to staging, run penetration tests, set up CI/CD, database backups, and production monitoring.
- Add reporting (delinquency, cashflow, monthly revenue) and CSV/XLSX export for accounting.

How to get support
------------------
- For technical work, open issues in the repository and tag `priority/urgent` for payment or data-loss risks. For product requests, create tickets with acceptance criteria and sample data.

Contact
-------
- Development lead: add internal contact or use repository issues to request changes.
