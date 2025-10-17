# 💎 Lumin SaaS - האור של העסק שלך

<div align="center">

![Lumin Logo](https://via.placeholder.com/200x80/00ADB5/FFFFFF?text=Lumin)

**Multi-Tenant Inventory & Sales Management System**

Built for Beauty Clinics & Cosmetics Stores

[![Django](https://img.shields.io/badge/Django-5.0-green)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC)](https://tailwindcss.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Development](#-development)
- [Deployment](#-deployment)
- [Security](#-security)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Lumin** is a comprehensive SaaS platform designed to help small businesses (specifically beauty clinics and cosmetics stores) manage their inventory, sales, and customers efficiently. The system features a multi-tenant architecture, ensuring complete data isolation between different business accounts.

### Key Highlights

- 🏢 **Multi-Tenant Architecture** - Logical separation via `tenant_id`
- 🌐 **Hebrew RTL Support** - Fully optimized for Hebrew (right-to-left)
- 📱 **Responsive Design** - Works seamlessly on mobile, tablet, and desktop
- 🔐 **Google OAuth + SMS Verification** - Secure and convenient authentication
- 📊 **Real-time Analytics** - Dashboard with KPIs and charts
- 💰 **Point of Sale (PoS) Lite** - Quick order creation with automatic stock updates
- 👥 **Customer Management (CRM)** - Track purchases and customer data
- 📦 **Inventory Tracking** - Low stock alerts and stock adjustments
- 🎨 **Beautiful UI** - Modern design with turquoise brand colors and gradients

---

## ✨ Features

### MVP (Version 1.0)

#### 🔐 Authentication & Authorization
- Google Sign-In (OAuth 2.0)
- SMS phone verification (Twilio)
- Multi-tenant registration
- Role-based access control (Admin vs Basic Staff)
- Session management (20-minute timeout)

#### 📦 Inventory Management
- CRUD operations for products
- Stock level tracking
- Low stock alerts
- Manual stock adjustments
- CSV export
- Plan limits (BASIC: 10 products, PRO: unlimited)

#### 💰 Sales Management
- Manual order entry (PoS Lite)
- Automatic stock reduction
- Discount percentage support
- Multiple payment methods
- Orders history
- CSV export

#### 👥 Customer Management (CRM)
- CRUD operations for customers
- Purchase history tracking
- Customer search
- Top customers report
- Plan limits (BASIC: 5 customers, PRO: unlimited)

#### 📊 Dashboard & Analytics
- Today's revenue and order count
- Monthly revenue and order count
- Low stock items alert
- Total customers count
- Gross profit (Admin only)
- Sales chart (last 30 days)
- Top 5 products by revenue

#### ⚙️ Settings
- Business profile (name, logo)
- Staff invitation (Admin only)
- Plan details view

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Django 5.0** | Web framework |
| **Django REST Framework** | API development |
| **PostgreSQL 15** | Database |
| **Celery** | Task queue |
| **Redis** | Cache & Celery broker |
| **Django Allauth** | Google OAuth |
| **Twilio** | SMS verification |
| **SendGrid** | Email service |
| **AWS S3** | File storage (optional) |
| **Gunicorn** | WSGI server |
| **WhiteNoise** | Static files |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **Vite** | Build tool |
| **Tailwind CSS** | Styling |
| **Zustand** | Global state management |
| **TanStack Query** | Server state management |
| **Axios** | HTTP client |
| **React Router v6** | Routing |
| **Lucide React** | Icons |
| **Recharts** | Charts |
| **React Hot Toast** | Notifications |

---

## 📂 Project Structure

```
Lumin/
│
├── lumin-backend/          # Django REST API
│   ├── config/             # Settings & configuration
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── celery.py
│   ├── apps/
│   │   ├── core/           # Shared utilities
│   │   ├── accounts/       # Auth, Users, Tenants
│   │   ├── inventory/      # Products
│   │   ├── sales/          # Orders
│   │   ├── customers/      # CRM
│   │   └── analytics/      # Dashboard
│   ├── requirements.txt
│   ├── .env.example
│   └── manage.py
│
├── lumin-frontend/         # React SPA
│   ├── src/
│   │   ├── features/       # Feature modules
│   │   ├── components/     # Reusable components
│   │   ├── config/         # API & constants
│   │   ├── hooks/          # Custom hooks
│   │   ├── utils/          # Utility functions
│   │   ├── styles/         # Global styles
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── docs/                   # Documentation
│   ├── Lumin Project.txt   # Full technical specification
│   └── DOCKER_SETUP.md     # Docker setup guide
│
├── scripts/                # Automation scripts
│   ├── dev-setup.bat       # Windows setup script
│   └── dev-setup.sh        # Unix setup script
│
├── docker-compose.yml      # Docker services configuration
├── .gitignore
└── README.md               # This file
```

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**
- **Node.js 18+** & npm
- **Docker Desktop** (recommended) OR PostgreSQL 15+ & Redis 7+

> 💡 **Pro Tip**: We highly recommend using Docker for PostgreSQL and Redis. It's easier to set up and matches the production environment. See our [Docker Setup Guide](docs/DOCKER_SETUP.md) for details.

### Quick Setup with Docker (Recommended) 🐳

For the fastest setup, use our automated scripts:

**Windows:**
```bash
scripts\dev-setup.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh
```

This will:
- ✅ Start Docker containers (PostgreSQL + Redis)
- ✅ Create the database
- ✅ Run migrations
- ✅ Set up the backend

**Then start the servers:**
```bash
# Backend
cd lumin-backend
python manage.py runserver

# Frontend (new terminal)
cd lumin-frontend
npm run dev
```

---

### Manual Setup (Without Docker)

If you prefer manual setup or don't use Docker:

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd lumin-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Create PostgreSQL database**
   ```bash
   createdb lumin_db
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Run Celery worker** (in a new terminal)
   ```bash
   celery -A config worker -l info
   ```

Backend will be available at `http://localhost:8000`

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd lumin-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with backend API URL
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

Frontend will be available at `http://localhost:5173`

---

### 🐳 Docker Management

For detailed Docker commands and troubleshooting, see [Docker Setup Guide](docs/DOCKER_SETUP.md).

**Quick Commands:**
```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose stop

# View logs
docker-compose logs -f

# Restart containers
docker-compose restart

# Stop and remove (keeps data)
docker-compose down
```

---

## 💻 Development

### Development Workflow

1. **Backend**: Make changes in `lumin-backend/apps/`
2. **Frontend**: Make changes in `lumin-frontend/src/`
3. **Test**: Ensure both servers are running simultaneously
4. **Commit**: Follow conventional commit messages

### Running Tests

**Backend:**
```bash
cd lumin-backend
pytest --cov=apps
```

**Frontend:**
```bash
cd lumin-frontend
npm run test  # (To be configured)
```

### Code Style

- **Backend**: Follow PEP 8, use Black formatter
- **Frontend**: Follow Airbnb style guide, use ESLint

---

## 🚢 Deployment

### Backend (Render)

1. Create PostgreSQL database on Render
2. Create Redis instance on Render
3. Create Web Service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn config.wsgi:application`
4. Create Background Worker (Celery):
   - **Start Command**: `celery -A config worker -l info`
5. Set all environment variables from `.env.example`

### Frontend (Render Static Site)

1. Create Static Site on Render
2. **Build Command**: `npm install && npm run build`
3. **Publish Directory**: `dist`
4. Set `VITE_API_URL` to your backend URL

### External Services

- **Google OAuth**: Create project in Google Cloud Console
- **Twilio**: Sign up and get credentials
- **SendGrid**: Sign up and create API key
- **AWS S3** (optional): Create bucket and IAM user

---

## 🔒 Security

### Critical Security Features

1. **Multi-Tenant Isolation**
   - Every query filtered by `tenant_id`
   - Middleware enforces tenant context
   - Never trust client-sent `tenant_id`

2. **Role-Based Access Control**
   - ADMIN: Full access including financials
   - BASIC_STAFF: Limited access, no financial data

3. **Authentication**
   - Google OAuth for secure login
   - SMS verification for phone numbers
   - Session timeout (20 minutes)

4. **Data Protection**
   - CSRF protection enabled
   - SQL injection prevention (Django ORM)
   - XSS prevention (React auto-escaping)
   - Encrypted API keys (Fernet/AES-256)

5. **Rate Limiting**
   - SMS endpoint: 3 requests per phone per hour

---

## 🗺️ Roadmap

### Phase 1: Setup ✅ (Week 1)
- [x] Django project structure
- [x] React project structure
- [x] Core models and utilities
- [x] Authentication setup

### Phase 2: Authentication (Week 2)
- [ ] Google OAuth integration
- [ ] Phone verification flow
- [ ] Tenant registration
- [ ] Auth UI components

### Phase 3: Core Models & APIs (Week 3-4)
- [ ] Product model & API
- [ ] Customer model & API
- [ ] Order model & API
- [ ] Multi-tenant enforcement
- [ ] Unit tests

### Phase 4: Dashboard & Analytics (Week 5)
- [ ] Analytics API endpoints
- [ ] Dashboard UI
- [ ] KPI cards
- [ ] Charts integration

### Phase 5: Inventory Module (Week 6)
- [ ] Inventory page
- [ ] Product CRUD UI
- [ ] Stock adjustment
- [ ] Low stock alerts
- [ ] CSV export

### Phase 6: Sales Module (Week 7)
- [ ] PoS Lite interface
- [ ] Order creation
- [ ] Orders history
- [ ] Stock auto-reduction

### Phase 7: Customers Module (Week 7)
- [ ] Customers page
- [ ] Customer CRUD UI
- [ ] Purchase history
- [ ] Top customers

### Phase 8: Polish & Deploy (Week 8-9)
- [ ] Responsive design testing
- [ ] RTL testing
- [ ] Error handling
- [ ] Loading states
- [ ] Deploy to Render
- [ ] Beta testing

### Future Enhancements (v2.0+)
- [ ] Treatment/Service module
- [ ] Advanced CRM features
- [ ] WooCommerce integration
- [ ] PDF reports
- [ ] Refunds/Returns
- [ ] Multi-location support
- [ ] Dark mode
- [ ] Mobile app (PWA)
- [ ] Advanced analytics

---

## 🤝 Contributing

This is a proprietary project. Contributions are limited to the development team.

---

## 📄 License

**Proprietary** - All rights reserved.

For more information, contact the development team.

---

## 📞 Support

For technical questions or issues, please refer to:
- **Full Specification**: [docs/Lumin Project.txt](docs/Lumin%20Project.txt)
- **Docker Setup Guide**: [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md)
- **Quick Start Guide**: [QUICK_START.md](QUICK_START.md)
- **Backend README**: [lumin-backend/README.md](lumin-backend/README.md)
- **Frontend README**: [lumin-frontend/README.md](lumin-frontend/README.md)

---

<div align="center">

**Built with ❤️ by the Lumin Team**

*Lumin - האור של העסק שלך*

</div>
