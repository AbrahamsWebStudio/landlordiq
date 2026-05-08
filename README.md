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
