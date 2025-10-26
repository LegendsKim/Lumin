# 🎯 Lumin SaaS - Revised Technical Specification
**Full-Stack Development Guide - Lessons Learned Edition**

---

## 📋 REVISION HISTORY

**Original Spec Issues Identified:**
1. ❌ No clear local development setup guide
2. ❌ Environment variable loading strategy unclear
3. ❌ PostgreSQL authentication configuration not specified
4. ❌ No troubleshooting section for common issues
5. ❌ Assumed django-environ works without explicit configuration
6. ❌ No startup verification checklist
7. ❌ Missing Docker compose health check details
8. ❌ No rollback strategy for broken migrations

**This Revision Addresses:**
- ✅ Step-by-step local development setup
- ✅ Explicit environment configuration strategy
- ✅ PostgreSQL trust mode for local development
- ✅ Detailed troubleshooting guide
- ✅ Startup verification procedures
- ✅ Docker configuration best practices
- ✅ Development vs Production environment clarity

---

## 📖 TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Local Development Setup](#3-local-development-setup-critical)
4. [Database Schema](#4-database-schema)
5. [Backend Implementation](#5-backend-implementation)
6. [Frontend Implementation](#6-frontend-implementation)
7. [Authentication Flow](#7-authentication-flow)
8. [Security Implementation](#8-security-implementation)
9. [Deployment Guide](#9-deployment-guide)
10. [Testing Strategy](#10-testing-strategy)
11. [Troubleshooting Guide](#11-troubleshooting-guide-new)
12. [Development Roadmap](#12-development-roadmap)

---

## 1. PROJECT OVERVIEW

**Project Name:** Lumin
**Type:** Multi-Tenant SaaS
**Domain:** Inventory & Sales Management for Small Businesses
**Target:** Beauty Clinics & Cosmetics Stores (MVP)
**Developer:** Solo developer using AI assistance (Claude Code)
**Budget:** Minimal
**Timeline:** 8-9 weeks

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Architecture

```
CLIENT (React + Vite + Tailwind)
    ↓ REST API (JSON)
BACKEND (Django + DRF)
    ↓
DATABASE (PostgreSQL - Multi-Tenant via tenant_id)

EXTERNAL SERVICES:
- Google OAuth (Authentication)
- Twilio (SMS Verification)
- SendGrid (Email)
- AWS S3 (File Storage - Optional)
```

### 2.2 Multi-Tenant Strategy

**Isolation Method:** Logical separation via `tenant_id` column (NOT separate databases)

**Enforcement:**
- Backend middleware automatically injects `request.tenant`
- Every QuerySet MUST filter by `tenant_id`
- API endpoints MUST validate tenant ownership
- Never trust client-sent `tenant_id` - always use `request.user.tenant`

---

## 3. LOCAL DEVELOPMENT SETUP (CRITICAL)

### 3.1 Prerequisites

**Required Software:**
- Python 3.12+ (verify: `python --version`)
- Node.js 18+ (verify: `node --version`)
- Docker Desktop (verify: `docker --version`)
- Git (verify: `git --version`)
- Code editor (VS Code recommended)

**Operating System Notes:**
- Windows: Use Git Bash or PowerShell (avoid CMD where possible)
- macOS/Linux: Use Terminal

---

### 3.2 Initial Project Setup

**Step 1: Clone Repository**
```bash
git clone <repository-url>
cd Lumin
```

**Step 2: Backend Setup**
```bash
cd lumin-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Step 3: Frontend Setup**
```bash
cd ../lumin-frontend

# Install dependencies
npm install
```

---

### 3.3 Docker Configuration (PostgreSQL + Redis)

**File: `docker-compose.yml`**

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: lumin-postgres
    environment:
      POSTGRES_DB: lumin_db
      POSTGRES_USER: postgres
      # IMPORTANT: Use trust mode for local development (no password needed)
      POSTGRES_HOST_AUTH_METHOD: trust
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis Cache & Celery Broker
  redis:
    image: redis:7-alpine
    container_name: lumin-redis
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
    name: lumin_postgres_data
  redis_data:
    name: lumin_redis_data
```

**WHY Trust Mode for Development:**
- ✅ No password authentication issues
- ✅ Simpler local development workflow
- ✅ No need to sync passwords between .env and Docker
- ✅ Faster iteration (no auth failures)
- ⚠️ NEVER use in production (production uses password + SSL)

**Start Docker Services:**
```bash
# From project root
docker compose up -d

# Verify containers are running
docker ps

# Expected output:
# lumin-postgres (healthy)
# lumin-redis (healthy)

# Verify PostgreSQL connection
docker exec lumin-postgres psql -U postgres -d lumin_db -c "SELECT version();"
```

---

### 3.4 Environment Variables Configuration

**CRITICAL LESSON LEARNED:**
The original spec assumed `django-environ` would automatically read `.env` files. In practice, this often fails silently. The solution: **explicit environment file reading in settings**.

**File: `lumin-backend/.env`**

```env
# Django Core Settings
SECRET_KEY=django-insecure-local-dev-key-change-in-production
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development

# Database (NO PASSWORD for local development with trust mode)
DATABASE_URL=postgresql://postgres@127.0.0.1:5432/lumin_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Allowed Hosts (comma separated)
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS (comma separated)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Google OAuth (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here

# Twilio SMS (get from Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# SendGrid Email (get from SendGrid)
SENDGRID_API_KEY=your-api-key
DEFAULT_FROM_EMAIL=noreply@lumin.local

# AWS S3 (Optional - use local storage for development)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

# Session Settings
SESSION_COOKIE_AGE=1200
SESSION_SAVE_EVERY_REQUEST=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Security (Production only)
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
```

**File: `lumin-backend/config/settings/base.py`**

```python
"""
Django base settings for Lumin SaaS project.

IMPORTANT: Environment variable loading strategy
"""
import os
from pathlib import Path
import environ

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize environ
env = environ.Env(
    DEBUG=(bool, False)
)

# CRITICAL: Read .env file explicitly
# This ensures environment variables are loaded correctly
env_file = BASE_DIR / '.env'
if env_file.exists():
    # Use env.read_env() method (not environ.Env.read_env())
    env.read_env(str(env_file))
    print(f"✓ Loaded environment from: {env_file}")
else:
    print(f"⚠ WARNING: .env file not found at {env_file}")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-temp-key-for-dev')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Local apps
    'apps.core',
    'apps.accounts',
    'apps.inventory',
    'apps.sales',
    'apps.customers',
    'apps.analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'apps.core.middleware.TenantMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# CRITICAL: Use env.db() to parse DATABASE_URL
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='postgresql://postgres@127.0.0.1:5432/lumin_db'
    )
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'he'  # Hebrew
TIME_ZONE = 'Asia/Jerusalem'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site ID (for Django Allauth)
SITE_ID = 1

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# CORS Settings
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True

# Session Settings
SESSION_COOKIE_AGE = env.int('SESSION_COOKIE_AGE', default=1200)
SESSION_SAVE_EVERY_REQUEST = env.bool('SESSION_SAVE_EVERY_REQUEST', default=True)
SESSION_COOKIE_HTTPONLY = env.bool('SESSION_COOKIE_HTTPONLY', default=True)
SESSION_COOKIE_SAMESITE = env('SESSION_COOKIE_SAMESITE', default='Lax')

# Celery Configuration
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Jerusalem'

# Django Allauth Configuration
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': env('GOOGLE_CLIENT_ID', default=''),
            'secret': env('GOOGLE_CLIENT_SECRET', default=''),
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Email Configuration (SendGrid)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = env('SENDGRID_API_KEY', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@lumin.local')

# Twilio Configuration
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER', default='')

# AWS S3 Configuration (Optional)
USE_S3 = env.bool('USE_S3', default=False)
if USE_S3:
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

**File: `lumin-backend/config/settings/development.py`**

```python
"""
Development settings - inherits from base.py
"""
from .base import *

# Development-specific settings
DEBUG = True

# Security settings (relaxed for local development)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

### 3.5 Database Migrations

**Run Initial Migrations:**
```bash
# Navigate to backend directory
cd lumin-backend

# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run migrations
python manage.py migrate

# Expected output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, ...
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ...

# Create superuser (for admin access)
python manage.py createsuperuser
# Email: admin@lumin.local
# Password: (enter secure password)
```

**Verify Database Connection:**
```bash
# Test database connection
python manage.py dbshell

# Inside PostgreSQL shell:
\dt  # List tables
\q   # Quit
```

---

### 3.6 Startup Scripts (Automation)

**File: `start_lumin.bat` (Windows)**

```batch
@echo off
echo ==============================================
echo   Lumin - Smart Business Management System
echo ==============================================
echo.

echo [1/4] Starting Docker (PostgreSQL + Redis)...
docker compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Docker failed to start. Please ensure Docker Desktop is running.
    pause
    exit /b 1
)

echo.
echo [2/4] Waiting for database...
timeout /t 5 /nobreak > nul

echo.
echo [3/4] Running migrations...
cd lumin-backend
python manage.py migrate --noinput
if %errorlevel% neq 0 (
    echo ERROR: Migrations failed. Check database connection.
    pause
    exit /b 1
)

echo.
echo [4/4] Starting Django server...
echo.
echo ============================================
echo   Server running at: http://localhost:8000
echo   Press Ctrl+C to stop
echo ============================================
echo.
python manage.py runserver

pause
```

**File: `start_lumin.sh` (macOS/Linux)**

```bash
#!/bin/bash

echo "=============================================="
echo "  Lumin - Smart Business Management System"
echo "=============================================="
echo ""

echo "[1/4] Starting Docker (PostgreSQL + Redis)..."
docker compose up -d
if [ $? -ne 0 ]; then
    echo "ERROR: Docker failed to start."
    exit 1
fi

echo ""
echo "[2/4] Waiting for database..."
sleep 5

echo ""
echo "[3/4] Running migrations..."
cd lumin-backend
source venv/bin/activate
python manage.py migrate --noinput
if [ $? -ne 0 ]; then
    echo "ERROR: Migrations failed."
    exit 1
fi

echo ""
echo "[4/4] Starting Django server..."
echo ""
echo "============================================"
echo "  Server running at: http://localhost:8000"
echo "  Press Ctrl+C to stop"
echo "============================================"
echo ""
python manage.py runserver
```

**Make script executable (macOS/Linux):**
```bash
chmod +x start_lumin.sh
```

---

### 3.7 Startup Verification Checklist

**After running startup script, verify:**

1. **Docker Containers Running:**
   ```bash
   docker ps
   # Should show: lumin-postgres (healthy), lumin-redis (healthy)
   ```

2. **Django Server Started:**
   ```
   # Terminal output should show:
   # System check identified no issues (0 silenced).
   # Django version X.X.X, using settings 'config.settings.development'
   # Starting development server at http://127.0.0.1:8000/
   # Quit the server with CTRL-BREAK.
   ```

3. **Admin Panel Accessible:**
   - Open browser: `http://localhost:8000/admin/`
   - Login with superuser credentials
   - Should see Django admin interface

4. **API Endpoint Test:**
   ```bash
   # In new terminal
   curl http://localhost:8000/api/
   # Should return JSON response (not error)
   ```

5. **Frontend (if applicable):**
   ```bash
   cd lumin-frontend
   npm run dev
   # Open http://localhost:5173
   # Should see landing page
   ```

**If any verification fails, see [Troubleshooting Guide](#11-troubleshooting-guide-new)**

---

## 4. DATABASE SCHEMA

### 4.1 Core Tables

#### `tenants`
**Purpose:** Organization/Business account

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `business_name` | VARCHAR(255) | NOT NULL | Business name |
| `owner_email` | VARCHAR(255) | UNIQUE, NOT NULL | Owner's email |
| `owner_phone` | VARCHAR(20) | NOT NULL | Owner's phone |
| `phone_verified` | BOOLEAN | DEFAULT FALSE | Phone verification status |
| `logo` | FILE | NULLABLE | Business logo |
| `plan` | ENUM | DEFAULT 'BASIC' | Subscription plan (BASIC, PRO) |
| `stripe_customer_id` | VARCHAR(255) | NULLABLE | Stripe customer ID |
| `subscription_expires_at` | TIMESTAMP | NULLABLE | Subscription expiry |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account active status |
| `created_at` | TIMESTAMP | AUTO | Creation timestamp |
| `updated_at` | TIMESTAMP | AUTO | Last update timestamp |

**Plan Limits:**
- BASIC: max 10 products, max 5 customers
- PRO: unlimited

**Indexes:** `owner_email`

---

#### `users`
**Purpose:** User accounts (extends Django AbstractUser)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `tenant_id` | UUID | FK to tenants, NOT NULL | Associated tenant |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User email (login) |
| `phone` | VARCHAR(20) | NULLABLE | Phone number |
| `phone_verified` | BOOLEAN | DEFAULT FALSE | Phone verification status |
| `role` | ENUM | DEFAULT 'BASIC_STAFF' | User role (ADMIN, BASIC_STAFF) |
| `google_sub` | VARCHAR(255) | UNIQUE, NULLABLE | Google OAuth ID |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account active status |
| `last_login` | TIMESTAMP | NULLABLE | Last login timestamp |
| `created_at` | TIMESTAMP | AUTO | Creation timestamp |

**Business Rules:**
- `USERNAME_FIELD = 'email'` (not username)
- ADMIN can see `cost_price` and `profit` fields
- BASIC_STAFF cannot see financial data

**Indexes:** `tenant_id`, `email`, `google_sub`

---

### 4.2 Inventory Module

#### `products`
**Purpose:** Product/Inventory items

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `tenant_id` | UUID | FK, NOT NULL | Associated tenant |
| `name` | VARCHAR(255) | NOT NULL | Product name |
| `sku` | VARCHAR(100) | NULLABLE | Stock keeping unit |
| `description` | TEXT | NULLABLE | Product description |
| `category` | VARCHAR(100) | NULLABLE | Product category |
| `cost_price` | DECIMAL(10,2) | NOT NULL | Cost price (ADMIN ONLY) |
| `sell_price` | DECIMAL(10,2) | NOT NULL | Selling price |
| `current_stock` | INTEGER | DEFAULT 0, CHECK >= 0 | Current stock level |
| `desired_stock` | INTEGER | DEFAULT 0 | Desired stock level |
| `location` | VARCHAR(100) | NULLABLE | Storage location |
| `is_active` | BOOLEAN | DEFAULT TRUE | Product active status |
| `created_by` | UUID | FK to users, NULLABLE | Creator user |
| `updated_by` | UUID | FK to users, NULLABLE | Last updater |
| `created_at` | TIMESTAMP | AUTO | Creation timestamp |
| `updated_at` | TIMESTAMP | AUTO | Last update timestamp |

**Computed Properties:**
- `is_low_stock`: `current_stock < desired_stock`
- `profit_margin`: `((sell_price - cost_price) / sell_price) * 100`

**Constraints:**
- UNIQUE (`tenant_id`, `sku`)
- `sell_price >= cost_price`

**Indexes:** `tenant_id`, `(tenant_id, current_stock)` WHERE `is_low_stock`

---

### 4.3 CRM Module

#### `customers`
**Purpose:** Customer/Client records

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `tenant_id` | UUID | FK, NOT NULL | Associated tenant |
| `full_name` | VARCHAR(255) | NOT NULL | Customer full name |
| `phone` | VARCHAR(20) | NULLABLE | Phone number |
| `email` | VARCHAR(255) | NULLABLE | Email address |
| `notes` | TEXT | NULLABLE | Customer notes |
| `total_purchases` | DECIMAL(10,2) | DEFAULT 0 | Total purchase amount (denormalized) |
| `purchase_count` | INTEGER | DEFAULT 0 | Number of purchases (denormalized) |
| `created_at` | TIMESTAMP | AUTO | Creation timestamp |
| `updated_at` | TIMESTAMP | AUTO | Last update timestamp |

**Constraints:**
- UNIQUE (`tenant_id`, `phone`)

**Indexes:** `tenant_id`, `phone`

---

### 4.4 Sales Module

#### `orders`
**Purpose:** Sales transactions

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `tenant_id` | UUID | FK, NOT NULL | Associated tenant |
| `customer_id` | UUID | FK to customers, NULLABLE | Associated customer |
| `subtotal` | DECIMAL(10,2) | NOT NULL | Subtotal before discount |
| `discount_percent` | DECIMAL(5,2) | DEFAULT 0, CHECK 0-100 | Discount percentage |
| `payment_method` | VARCHAR(50) | NULLABLE | Payment method |
| `notes` | TEXT | NULLABLE | Order notes |
| `created_by` | UUID | FK to users, NULLABLE | Creator user |
| `created_at` | TIMESTAMP | AUTO | Creation timestamp |

**Computed Properties:**
- `discount_amount`: `subtotal * (discount_percent / 100)`
- `total`: `subtotal - discount_amount`
- `total_profit`: `SUM(items.line_profit)` (ADMIN ONLY)

**Indexes:** `tenant_id`, `(tenant_id, created_at DESC)`, `customer_id`

---

#### `order_items`
**Purpose:** Line items in orders

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `order_id` | UUID | FK to orders, CASCADE | Associated order |
| `product_id` | UUID | FK to products, NULLABLE | Associated product |
| `product_name` | VARCHAR(255) | NOT NULL | Product name (snapshot) |
| `unit_price` | DECIMAL(10,2) | NOT NULL | Unit price (snapshot) |
| `cost_price` | DECIMAL(10,2) | NOT NULL | Cost price (snapshot, ADMIN ONLY) |
| `quantity` | INTEGER | NOT NULL, CHECK > 0 | Quantity sold |

**Computed Properties:**
- `line_total`: `unit_price * quantity`
- `line_profit`: `(unit_price - cost_price) * quantity` (ADMIN ONLY)

**Business Logic:**
- On INSERT: Automatically reduce `products.current_stock` by quantity
- On INSERT: Update `customers.total_purchases` and `purchase_count`

**Indexes:** `order_id`, `product_id`

---

### 4.5 Database Triggers Required

**Trigger 1: `update_timestamps`**
- **Table:** All tables with `updated_at`
- **Action:** BEFORE UPDATE → SET `updated_at = NOW()`

**Trigger 2: `reduce_stock_on_sale`**
- **Table:** `order_items`
- **Action:** AFTER INSERT → UPDATE `products` SET `current_stock = current_stock - NEW.quantity`

**Trigger 3: `update_customer_stats`**
- **Table:** `orders`
- **Action:** AFTER INSERT → UPDATE `customers` SET `total_purchases += NEW.total`, `purchase_count += 1`

---

## 5. BACKEND IMPLEMENTATION

### 5.1 Django Project Structure

```
lumin-backend/
├── config/
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── development.py   # Local dev (DEBUG=True)
│   │   ├── production.py    # Production (DEBUG=False)
│   ├── urls.py
│   ├── wsgi.py
├── apps/
│   ├── core/               # Shared utilities
│   ├── accounts/           # Auth, Users, Tenants
│   ├── inventory/          # Products
│   ├── sales/              # Orders, PoS
│   ├── customers/          # CRM
│   ├── analytics/          # Dashboard KPIs
├── requirements.txt
├── .env
├── manage.py
```

### 5.2 Requirements

**File: `requirements.txt`**

```
Django==5.0.1
djangorestframework==3.14.0
django-allauth==0.57.0
psycopg2-binary==2.9.9
celery==5.3.4
redis==5.0.1
django-environ==0.11.2
boto3==1.34.10
twilio==8.11.1
sendgrid==6.11.0
gunicorn==21.2.0
whitenoise==6.6.0
django-cors-headers==4.3.1
django-ratelimit==4.1.0
cryptography==41.0.7
django-filter==23.5
```

---

## 6. FRONTEND IMPLEMENTATION

### 6.1 Project Structure

```
lumin-frontend/
├── src/
│   ├── features/            # Feature modules
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── inventory/
│   │   ├── sales/
│   │   ├── customers/
│   ├── components/
│   │   ├── layout/         # Navbar, Sidebar, Footer
│   │   ├── ui/             # Reusable components
│   ├── config/             # API, constants
│   ├── hooks/              # Custom hooks
│   ├── utils/              # Helpers
│   ├── styles/             # Global CSS, Tailwind config
├── public/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── package.json
├── .env
```

### 6.2 Technology Stack

**Core:**
- React 18
- Vite (build tool)
- React Router DOM v6
- Tailwind CSS

**State Management:**
- Zustand (global state)
- TanStack Query (React Query) for server state

**UI:**
- Lucide React (icons)
- Recharts (charts)
- React Hot Toast (notifications)

**HTTP:**
- Axios

---

## 7. AUTHENTICATION FLOW

### 7.1 User Registration & Onboarding

**Step 1:** User visits landing page → clicks "Start Free"

**Step 2:** Google Sign-In
- Redirect to `/accounts/google/login/`
- Django Allauth handles OAuth flow
- Backend creates User object (email, google_sub, tenant_id=NULL)

**Step 3:** Phone Verification
- Frontend: POST `/api/auth/phone/request` → sends SMS
- User enters 6-digit code
- Frontend: POST `/api/auth/phone/verify` → validates code

**Step 4:** Create Tenant
- User enters business name
- Frontend: POST `/api/auth/register-tenant`
- Backend creates Tenant, updates User
- Redirect to Dashboard

### 7.2 Subsequent Logins

- User clicks "Sign in with Google"
- Backend finds User by google_sub
- Frontend: GET `/api/users/me/`
- Redirect to Dashboard

---

## 8. SECURITY IMPLEMENTATION

### 8.1 Critical Security Rules

1. **Tenant Isolation (MOST CRITICAL):**
   - NEVER trust client-sent `tenant_id`
   - ALWAYS use `request.user.tenant`
   - EVERY QuerySet MUST filter by `tenant_id`

2. **Role-Based Access Control:**
   - ADMIN sees all fields
   - BASIC_STAFF sees limited fields

3. **Plan Limits Enforcement:**
   - Check limits BEFORE creating resource

4. **Input Validation:**
   - Validate all input at serializer level

5. **Rate Limiting:**
   - SMS endpoint: max 3 requests/phone/hour

6. **Session Security:**
   - `SESSION_COOKIE_HTTPONLY = True`
   - `SESSION_COOKIE_SECURE = True` (production)
   - Session timeout: 20 minutes

---

## 9. DEPLOYMENT GUIDE

### 9.1 Backend Deployment (Render)

**Prerequisites:**
- GitHub repository
- Render account

**Steps:**

1. **Create PostgreSQL Database:**
   - Render Dashboard → New → PostgreSQL
   - Name: `lumin-db`
   - Copy `DATABASE_URL` (with password)

2. **Create Redis Instance:**
   - New → Redis
   - Name: `lumin-redis`
   - Copy `REDIS_URL`

3. **Create Web Service:**
   - New → Web Service
   - Connect GitHub repo
   - Name: `lumin-backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn config.wsgi:application`
   - Environment Variables:
     ```
     DATABASE_URL=<from-postgres-service>
     REDIS_URL=<from-redis-service>
     DEBUG=False
     DJANGO_SETTINGS_MODULE=config.settings.production
     SECRET_KEY=<generate-strong-key>
     ALLOWED_HOSTS=lumin-backend.onrender.com
     GOOGLE_CLIENT_ID=<from-google-console>
     GOOGLE_CLIENT_SECRET=<from-google-console>
     ...
     ```

4. **Run Migrations:**
   - Shell in Render: `python manage.py migrate`
   - Create superuser: `python manage.py createsuperuser`

5. **Collect Static Files:**
   - `python manage.py collectstatic --noinput`

---

## 10. TESTING STRATEGY

### 10.1 Backend Testing

**Setup:**
- pytest + pytest-django
- factory-boy for fixtures

**Test Categories:**
1. Model Tests
2. API Tests
3. Service Tests
4. Security Tests

**Run Tests:**
```bash
pytest --cov=apps --cov-report=html
```

### 10.2 Frontend Testing

**Setup:**
- Vitest + React Testing Library

**Test Categories:**
1. Component Tests
2. Integration Tests
3. Store Tests

**Run Tests:**
```bash
npm run test
```

---

## 11. TROUBLESHOOTING GUIDE (NEW)

### 11.1 Common Issues & Solutions

#### Issue 1: "password authentication failed for user postgres"

**Symptoms:**
```
django.db.utils.OperationalError: connection to server at "127.0.0.1", port 5432 failed:
FATAL: password authentication failed for user "postgres"
```

**Root Cause:**
- PostgreSQL is configured for password authentication, but Django is not providing the correct password
- OR Django is not reading the DATABASE_URL from .env

**Solutions:**

**Option A: Use Trust Mode (Recommended for Development)**
```yaml
# docker-compose.yml
postgres:
  environment:
    POSTGRES_HOST_AUTH_METHOD: trust  # No password needed
```

```env
# .env
DATABASE_URL=postgresql://postgres@127.0.0.1:5432/lumin_db  # No password
```

**Option B: Use Password Authentication**
```yaml
# docker-compose.yml
postgres:
  environment:
    POSTGRES_PASSWORD: lumin_dev_2025
    # Remove POSTGRES_HOST_AUTH_METHOD
```

```env
# .env
DATABASE_URL=postgresql://postgres:lumin_dev_2025@127.0.0.1:5432/lumin_db
```

**Verify Fix:**
```bash
# Test connection from inside container
docker exec lumin-postgres psql -U postgres -d lumin_db -c "SELECT 1;"

# Test from Django
python manage.py dbshell
```

**If still failing:**
1. Delete Docker volumes: `docker compose down -v`
2. Recreate containers: `docker compose up -d`
3. Wait 10 seconds for PostgreSQL initialization
4. Test connection again

---

#### Issue 2: Django not reading .env file

**Symptoms:**
- Environment variables not loaded
- Django uses default values instead of .env values

**Root Cause:**
- `environ.Env.read_env()` not called correctly
- `.env` file in wrong location

**Solutions:**

**Verify .env location:**
```
lumin-backend/
├── .env  ← Should be here (same level as manage.py)
├── manage.py
```

**Verify settings/base.py:**
```python
# config/settings/base.py
env = environ.Env()
env_file = BASE_DIR / '.env'
if env_file.exists():
    env.read_env(str(env_file))  # Use env.read_env(), NOT environ.Env.read_env()
    print(f"✓ Loaded: {env_file}")
else:
    print(f"⚠ NOT FOUND: {env_file}")
```

**Test:**
```bash
python manage.py shell

>>> from django.conf import settings
>>> print(settings.DATABASES)
# Should show correct DATABASE_URL
```

---

#### Issue 3: Server hangs on startup (loading migrations)

**Symptoms:**
```
DEBUG autoreload File ...migrations\__init__.py first seen...
DEBUG autoreload File ...migrations\__init__.py first seen...
(repeats forever, server never starts)
```

**Root Cause:**
- Django autoreload scanning too many files
- Database connection issues during migration check

**Solutions:**

**Option A: Disable autoreload (temporary)**
```bash
python manage.py runserver --noreload
```

**Option B: Run migrations first**
```bash
# Run migrations separately
python manage.py migrate --noinput

# Then start server
python manage.py runserver
```

**Option C: Check database connection**
```bash
# Verify PostgreSQL is running
docker ps | grep lumin-postgres

# Test connection
docker exec lumin-postgres pg_isready -U postgres
```

---

#### Issue 4: Docker containers not starting

**Symptoms:**
```
Error: Cannot start container lumin-postgres
```

**Solutions:**

**Check Docker Desktop is running:**
- Windows: Check system tray for Docker icon
- macOS: Check menu bar for Docker icon

**Check port conflicts:**
```bash
# Windows
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# macOS/Linux
lsof -i :5432
lsof -i :6379
```

**Stop conflicting services:**
```bash
# Windows (if local PostgreSQL is running)
net stop postgresql-x64-15

# macOS
brew services stop postgresql
```

**Restart Docker:**
```bash
docker compose down
docker compose up -d
```

---

#### Issue 5: CORS errors in frontend

**Symptoms:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/' from origin
'http://localhost:5173' has been blocked by CORS policy
```

**Solutions:**

**Verify CORS settings in .env:**
```env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**Verify settings/base.py:**
```python
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True
```

**Verify middleware order:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Must be before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    ...
]
```

---

### 11.2 Debugging Checklist

**When something breaks:**

1. ✅ Check browser console for errors
2. ✅ Check Django terminal for exceptions
3. ✅ Check Docker containers are running: `docker ps`
4. ✅ Check database connection: `python manage.py dbshell`
5. ✅ Check .env file is loaded: `python manage.py shell` → `from django.conf import settings` → `print(settings.DATABASES)`
6. ✅ Check migrations are applied: `python manage.py showmigrations`
7. ✅ Test API directly: `curl http://localhost:8000/api/`
8. ✅ Check logs: `docker logs lumin-postgres`, `docker logs lumin-redis`

---

### 11.3 Fresh Start Procedure

**If everything is broken and you need to start over:**

```bash
# 1. Stop all Docker containers
docker compose down -v

# 2. Delete all Docker volumes (CAUTION: deletes all data)
docker volume rm lumin_postgres_data lumin_redis_data

# 3. Restart Docker containers
docker compose up -d

# 4. Wait for initialization
sleep 10

# 5. Run migrations
cd lumin-backend
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Start server
python manage.py runserver

# 8. Test in browser
# http://localhost:8000/admin/
```

---

## 12. DEVELOPMENT ROADMAP

### Phase 1: Setup (Week 1)
- ✅ Initialize Django project
- ✅ Setup PostgreSQL + Redis (Docker)
- ✅ Configure settings (base, dev, prod)
- ✅ Create User and Tenant models
- ✅ Initialize React + Vite project
- ✅ Configure Tailwind CSS

### Phase 2: Authentication (Week 2)
- ✅ Implement Google Sign-In
- ✅ Implement phone verification
- ✅ Implement tenant registration
- ✅ Create auth store (Zustand)
- ✅ Test full registration flow

### Phase 3: Core Models & APIs (Week 3-4)
- ✅ Create Product model + API
- ✅ Create Customer model + API
- ✅ Create Order model + API
- ✅ Implement tenant isolation
- ✅ Implement role-based permissions
- ✅ Write backend tests

### Phase 4: Dashboard & Analytics (Week 5)
- ✅ Create analytics endpoints
- ✅ Build Dashboard page
- ✅ Create KPI cards
- ✅ Integrate charts (Recharts)

### Phase 5: Inventory Module (Week 6)
- ✅ Build Inventory page
- ✅ Create Product form
- ✅ Implement stock adjustment
- ✅ Implement CSV export

### Phase 6: Sales Module (Week 7)
- ✅ Build Sales page (PoS)
- ✅ Create order form
- ✅ Implement stock reduction
- ✅ Show order history

### Phase 7: Customers Module (Week 7)
- ✅ Build Customers page
- ✅ Create customer form
- ✅ Show purchase history

### Phase 8: Polish & Deploy (Week 8-9)
- ✅ Responsive design
- ✅ RTL layout check
- ✅ Error handling
- ✅ Deploy to Render
- ✅ Security audit
- ✅ Beta testing

---

## 13. KEY LESSONS LEARNED

### 13.1 What Went Wrong in Original Spec

1. **Environment Variables:**
   - ❌ Assumed django-environ "just works"
   - ✅ Need explicit `env.read_env()` call
   - ✅ Need to verify .env is loaded (print statement)

2. **PostgreSQL Authentication:**
   - ❌ Didn't specify authentication method
   - ✅ Use trust mode for local development
   - ✅ Document password vs trust mode tradeoffs

3. **Startup Process:**
   - ❌ No automated startup script
   - ✅ Create .bat/.sh scripts for one-command startup
   - ✅ Include verification steps in script

4. **Troubleshooting:**
   - ❌ No troubleshooting guide
   - ✅ Document common errors with solutions
   - ✅ Include "fresh start" procedure

5. **Docker Configuration:**
   - ❌ Assumed Docker volumes persist correctly
   - ✅ Document volume deletion for fresh start
   - ✅ Use health checks to verify services ready

---

### 13.2 Best Practices Moving Forward

1. **Always verify environment loading:**
   ```python
   if env_file.exists():
       env.read_env(str(env_file))
       print(f"✓ Loaded: {env_file}")
   ```

2. **Use trust mode for local PostgreSQL:**
   ```yaml
   POSTGRES_HOST_AUTH_METHOD: trust
   ```

3. **Test database connection before running migrations:**
   ```bash
   docker exec lumin-postgres pg_isready -U postgres
   ```

4. **Create automated startup scripts:**
   - One command to start everything
   - Include verification steps
   - Handle errors gracefully

5. **Document troubleshooting from day 1:**
   - Keep troubleshooting log
   - Document every error encountered
   - Add solutions to spec

---

## 14. SUCCESS CRITERIA

**MVP is complete when:**

- ✅ Owner can register with Google + phone
- ✅ Owner sees dashboard with real data
- ✅ Owner can add 10 products (BASIC limit enforced)
- ✅ Owner can add 5 customers (BASIC limit enforced)
- ✅ Owner can record sale, stock reduces automatically
- ✅ Owner sees low stock alert
- ✅ Owner can export to CSV
- ✅ Owner can invite staff
- ✅ Staff can't see financials
- ✅ All pages work on mobile
- ✅ Hebrew text displays correctly (RTL)
- ✅ System deployed online
- ✅ No security vulnerabilities
- ✅ Session expires after 20 minutes
- ✅ **Startup works with ONE command**
- ✅ **Troubleshooting guide prevents 90% of issues**

---

## END OF REVISED SPECIFICATION

**This specification incorporates all lessons learned from the initial development session and provides:**
- ✅ Clear local development setup
- ✅ Explicit environment configuration
- ✅ PostgreSQL trust mode for development
- ✅ Automated startup scripts
- ✅ Comprehensive troubleshooting guide
- ✅ Fresh start procedure
- ✅ Verification checklists

**Use this specification for all future development to avoid the issues encountered in the original implementation.**
