# LandlordIQ

LandlordIQ is a Django-based property management system designed to help landlords and property managers manage properties, units, tenants, leases, and rental income in one centralized platform.

It is built with a modular architecture, reusable UI components, and a focus on scalability, automation, and real-world Kenyan property management workflows.

---

## 🚀 Features

### Property Management
- Create, edit, and delete properties
- Track property status (active/inactive)
- View property-level analytics

### Unit Management
- Assign units to properties
- Track occupancy status
- Manage default rent suggestions

### Tenant & Lease System
- Tenant registration and assignment
- Lease tracking with monthly rent
- Active/inactive lease status

### Financial Overview
- Monthly revenue aggregation
- Occupancy rate tracking
- Property-level earnings breakdown

### UI/UX System
- Reusable form components (input, textarea, select, actions)
- Consistent dashboard layout
- Mobile-friendly responsive design
- TailwindCSS-based styling system

---

## 🧱 Tech Stack

- Python 3.12
- Django 6
- PostgreSQL
- TailwindCSS
- Vanilla JS (minimal interactivity)
- Lucide Icons

---

## 📁 Project Structure


templates/
├── components/ # Reusable UI components
├── properties/ # Property module
├── tenants/ # Tenant module
├── payments/ # Payment tracking
├── dashboard/ # Analytics dashboard


---

## ⚙️ Setup Instructions

## Environment & Local Seed (recommended)

1. Copy environment example and fill values (DO NOT commit a real `.env` file):

```bash
cp .env.example .env
# edit .env and set database, SECRET_KEY and MPESA credentials
```

2. Optional: enable MPesa callback HMAC verification by adding a secret:

```
MPESA_CALLBACK_SECRET=some-long-random-secret
```

3. Run migrations and collect static files:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

4. Seed local test data (creates a superuser, property, unit, tenant and invoice):

```bash
python manage.py seed_test_data
```

Seed defaults are driven from environment variables (see `.env.example`). This allows the seeding script to be parameterized in CI or dev environments.

5. Run the dev server:

```bash
python manage.py runserver
```

6. Tests (optional):

```bash
python manage.py test
```

Security reminder: Never commit `.env` or secrets. Use `.env.example` for onboarding and set real secrets in your deployment environment or secret manager.


### 1. Clone repository
```bash
git clone https://github.com/YOUR_USERNAME/landlordiq.git
cd landlordiq
2. Create virtual environment
python -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Run migrations
python manage.py makemigrations
python manage.py migrate
5. Create superuser
python manage.py createsuperuser
6. Run server
python manage.py runserver
🧠 Key Design Decisions
Component-based UI system for scalability
Separation of concerns between properties, tenants, and payments
Lightweight frontend (no heavy JS frameworks)
Database-driven property and lease structure
Designed for Kenyan landlords and SMEs
📌 Roadmap
 Tenant payment history UI
 M-Pesa integration
 PDF invoice generation
 SMS rent reminders
 Role-based access (Owner, Manager, Agent)
 AI rent prediction module
🇰🇪 Built For
Landlords in Kenya
Property managers
Small real estate firms
Rental agencies
👨‍💻 Author

Built by Genix Digital Collectives (GDC Kenya)
Focused on AI automation, software systems, and digital transformation for African SMEs.
