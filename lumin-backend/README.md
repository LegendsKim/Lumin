# Lumin Backend - האור של העסק שלך

Django REST API backend for Lumin SaaS - Multi-Tenant Inventory & Sales Management System.

## 🏗️ Architecture

- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL (Multi-Tenant via `tenant_id`)
- **Task Queue**: Celery + Redis
- **Authentication**: Google OAuth + Phone Verification (Twilio)
- **File Storage**: AWS S3 (optional)

## 📦 Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Setup Steps

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb lumin_db

   # Run migrations
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Run Celery Worker (separate terminal)**
   ```bash
   celery -A config worker -l info
   ```

## 🔐 Security

### Multi-Tenant Isolation

**CRITICAL**: Every query MUST filter by `tenant_id`. This is enforced by:

1. **TenantMiddleware**: Injects `request.tenant` for authenticated users
2. **TenantQuerySetMixin**: Auto-filters all QuerySets by tenant
3. **IsTenantMember Permission**: Verifies object ownership

### Role-Based Access Control

- **ADMIN**: Full access including financial data (cost, profit)
- **BASIC_STAFF**: Limited access, cannot see financial data

## 📂 Project Structure

```
lumin-backend/
├── config/                 # Django settings
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── development.py # Dev settings
│   │   └── production.py  # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── core/              # Shared utilities
│   ├── accounts/          # Auth, Users, Tenants
│   ├── inventory/         # Products
│   ├── sales/             # Orders, PoS
│   ├── customers/         # CRM
│   └── analytics/         # Dashboard KPIs
├── requirements.txt
├── .env.example
└── manage.py
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html
```

## 🚀 Deployment (Render)

1. Create PostgreSQL database on Render
2. Create Redis instance on Render
3. Create Web Service (Django)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn config.wsgi:application`
4. Create Background Worker (Celery)
   - Start Command: `celery -A config worker -l info`
5. Set environment variables from `.env.example`

## 📝 API Documentation

API endpoints will be documented using DRF's built-in browsable API.

Access at: `http://localhost:8000/api/`

## 🔗 Related

- Frontend: `../lumin-frontend`
- Docs: See `Lumin Project.txt` for full specification

## 📄 License

Proprietary - All rights reserved
