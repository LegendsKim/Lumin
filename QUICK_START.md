# 🚀 Lumin - Quick Start Guide

Get Lumin up and running in 10 minutes!

## ⚡ Prerequisites

Make sure you have these installed:
- Python 3.11+
- Node.js 18+
- **Docker Desktop** (recommended) OR PostgreSQL 15+ & Redis 7+

## 📦 Installation

### 🐳 Option 1: Docker Setup (Recommended)

Docker handles PostgreSQL and Redis automatically - no manual installation needed!

#### Step 1: Start Docker Containers

```bash
# Navigate to project directory
cd Lumin

# Start PostgreSQL + Redis containers
docker-compose up -d

# Verify containers are running
docker-compose ps
```

#### Step 2: Setup Backend

```bash
# Create virtual environment
cd lumin-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
```

**Edit `.env`** - Docker default values are already configured!
```env
DATABASE_URL=postgresql://lumin_user:lumin_password@localhost:5432/lumin_db
REDIS_URL=redis://localhost:6379/0
```

#### Step 3: Create Database & Run Migrations

```bash
# Create database
docker exec -it lumin-postgres psql -U lumin_user -c "CREATE DATABASE lumin_db;"

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

#### Step 4: Setup Frontend

```bash
cd lumin-frontend
npm install
cp .env.example .env
```

**Edit `.env`** - Set `VITE_API_URL=http://localhost:8000`

#### Step 5: Run the App

**Terminal 1 - Backend:**
```bash
cd lumin-backend
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd lumin-frontend
npm run dev
```

**Terminal 3 - Celery (optional):**
```bash
cd lumin-backend
celery -A config worker -l info
```

#### 🎯 Automated Setup Script

For even faster setup, use our automated script:

**Windows:**
```bash
scripts\dev-setup.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh
```

---

### 🔧 Option 2: Manual Installation (Without Docker)

If you prefer installing PostgreSQL and Redis manually:

### Step 1: Clone & Setup Environment

```bash
# Navigate to project directory
cd Lumin

# Backend setup
cd lumin-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

**Edit `.env`** with your credentials (at minimum, set SECRET_KEY and DATABASE_URL)

### Step 2: Database Setup

```bash
# Create database
createdb lumin_db

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### Step 3: Frontend Setup

```bash
# In a new terminal
cd lumin-frontend
npm install
cp .env.example .env
```

**Edit `.env`** - Set `VITE_API_URL=http://localhost:8000`

### Step 4: Run the App

**Terminal 1 - Backend:**
```bash
cd lumin-backend
python manage.py runserver
```

**Terminal 2 - Celery (optional for now):**
```bash
cd lumin-backend
celery -A config worker -l info
```

**Terminal 3 - Frontend:**
```bash
cd lumin-frontend
npm run dev
```

## 🎉 Access the App

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

## 🔧 Troubleshooting

### Docker Issues

**Containers won't start?**
- Check if Docker Desktop is running
- Check ports: `docker ps` to see if ports are already in use
- Restart Docker: `docker-compose down && docker-compose up -d`

**Database connection error?**
- Check container health: `docker exec lumin-postgres pg_isready -U lumin_user`
- View logs: `docker-compose logs postgres`
- Recreate container: `docker-compose down && docker-compose up -d`

**Redis connection error?**
- Check container health: `docker exec lumin-redis redis-cli ping`
- View logs: `docker-compose logs redis`
- Recreate container: `docker-compose down && docker-compose up -d`

### Manual Installation Issues

**Database connection error?**
- Make sure PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env`

**Redis connection error?**
- Make sure Redis is running: `redis-cli ping`
- Expected response: `PONG`

### General Issues

**Port already in use?**
- Backend: Change port in runserver command: `python manage.py runserver 8001`
- Frontend: Change port in `vite.config.js`

**Need more help?**
- See detailed Docker guide: [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md)

## 📚 Next Steps

1. Read the full [README.md](README.md)
2. Check the [Project Specification](docs/Lumin%20Project.txt)
3. Review the [Roadmap](README.md#-roadmap)
4. Start coding! 🚀

## 🆘 Need Help?

- **Backend issues**: See `lumin-backend/README.md`
- **Frontend issues**: See `lumin-frontend/README.md`
- **Architecture questions**: Read `docs/Lumin Project.txt`

---

**Happy Coding! 💻✨**

*Lumin - האור של העסק שלך*
