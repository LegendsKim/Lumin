# 🐳 Docker Setup Guide for Lumin

Complete guide for setting up and managing Docker containers for Lumin SaaS.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Common Commands](#common-commands)
- [Database Management](#database-management)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## 🎯 Prerequisites

### Required Software

1. **Docker Desktop** (recommended)
   - Download: https://www.docker.com/products/docker-desktop/
   - Minimum version: 20.10+
   - Includes Docker Compose

2. **Alternative: Docker Engine + Docker Compose** (Linux)
   ```bash
   # Install Docker Engine
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

### Verify Installation

```bash
# Check Docker version
docker --version
# Expected: Docker version 20.10.0 or higher

# Check Docker Compose version
docker-compose --version
# Expected: Docker Compose version 2.0.0 or higher

# Check Docker is running
docker ps
# Should show empty list or running containers (no errors)
```

---

## 🚀 Quick Start

### 1. Start Containers

```bash
# Navigate to project root
cd Lumin

# Start PostgreSQL + Redis
docker-compose up -d
```

**Expected Output:**
```
[+] Running 3/3
 ✔ Network lumin_network        Created
 ✔ Container lumin-postgres     Started
 ✔ Container lumin-redis        Started
```

### 2. Verify Containers are Running

```bash
docker-compose ps
```

**Expected Output:**
```
NAME              IMAGE                COMMAND                  STATUS         PORTS
lumin-postgres    postgres:15-alpine   "docker-entrypoint.s…"   Up 10 seconds  0.0.0.0:5432->5432/tcp
lumin-redis       redis:7-alpine       "docker-entrypoint.s…"   Up 10 seconds  0.0.0.0:6379->6379/tcp
```

### 3. Create Database

```bash
docker exec -it lumin-postgres psql -U lumin_user -c "CREATE DATABASE lumin_db;"
```

**Expected Output:**
```
CREATE DATABASE
```

### 4. Run Migrations

```bash
cd lumin-backend
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Start Development Servers

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

---

## 🔧 Detailed Setup

### Understanding docker-compose.yml

The `docker-compose.yml` file defines two services:

#### PostgreSQL Service
- **Image**: `postgres:15-alpine` (lightweight)
- **Port**: `5432` (standard PostgreSQL port)
- **User**: `lumin_user`
- **Password**: `lumin_password`
- **Volume**: `postgres_data` (persists data)
- **Health Check**: Checks readiness every 10 seconds

#### Redis Service
- **Image**: `redis:7-alpine` (lightweight)
- **Port**: `6379` (standard Redis port)
- **Volume**: `redis_data` (persists data)
- **Persistence**: AOF (Append Only File) enabled
- **Health Check**: Pings Redis every 10 seconds

### Environment Variables

Update `lumin-backend/.env`:

```env
# PostgreSQL
DATABASE_URL=postgresql://lumin_user:lumin_password@localhost:5432/lumin_db

# Redis
REDIS_URL=redis://localhost:6379/0
```

---

## 📝 Common Commands

### Starting and Stopping

```bash
# Start containers (detached mode)
docker-compose up -d

# Start containers (view logs)
docker-compose up

# Stop containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (⚠️ DELETES DATA!)
docker-compose down -v
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# View logs for specific service
docker-compose logs postgres
docker-compose logs redis

# Follow logs (real-time)
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

### Container Management

```bash
# List running containers
docker-compose ps

# Restart specific service
docker-compose restart postgres
docker-compose restart redis

# Rebuild containers
docker-compose up -d --build

# Remove stopped containers
docker-compose rm
```

### Health Checks

```bash
# Check PostgreSQL health
docker exec lumin-postgres pg_isready -U lumin_user

# Check Redis health
docker exec lumin-redis redis-cli ping

# View container health status
docker inspect --format='{{.State.Health.Status}}' lumin-postgres
docker inspect --format='{{.State.Health.Status}}' lumin-redis
```

---

## 🗄️ Database Management

### PostgreSQL

#### Access PostgreSQL CLI

```bash
# Connect to postgres database
docker exec -it lumin-postgres psql -U lumin_user

# Connect to lumin_db database
docker exec -it lumin-postgres psql -U lumin_user -d lumin_db
```

#### Common PostgreSQL Commands

```sql
-- List databases
\l

-- Connect to database
\c lumin_db

-- List tables
\dt

-- Describe table
\d tablename

-- Quit
\q
```

#### Backup Database

```bash
# Backup to SQL file
docker exec lumin-postgres pg_dump -U lumin_user lumin_db > backup_$(date +%Y%m%d).sql

# Backup with compression
docker exec lumin-postgres pg_dump -U lumin_user lumin_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

#### Restore Database

```bash
# Restore from SQL file
docker exec -i lumin-postgres psql -U lumin_user -d lumin_db < backup_20250117.sql

# Restore from compressed file
gunzip -c backup_20250117.sql.gz | docker exec -i lumin-postgres psql -U lumin_user -d lumin_db
```

#### Drop and Recreate Database

```bash
# Drop database (⚠️ DELETES ALL DATA!)
docker exec -it lumin-postgres psql -U lumin_user -c "DROP DATABASE IF EXISTS lumin_db;"

# Create fresh database
docker exec -it lumin-postgres psql -U lumin_user -c "CREATE DATABASE lumin_db;"

# Run migrations
cd lumin-backend
python manage.py migrate
```

### Redis

#### Access Redis CLI

```bash
docker exec -it lumin-redis redis-cli
```

#### Common Redis Commands

```redis
# Ping Redis
PING
# Response: PONG

# Get all keys
KEYS *

# Get value
GET key_name

# Set value
SET key_name value

# Delete key
DEL key_name

# Flush all data (⚠️ DELETES ALL DATA!)
FLUSHALL

# Quit
EXIT
```

#### Monitor Redis

```bash
# Monitor real-time commands
docker exec -it lumin-redis redis-cli MONITOR

# Get server info
docker exec -it lumin-redis redis-cli INFO

# Check memory usage
docker exec -it lumin-redis redis-cli INFO memory
```

---

## 🐛 Troubleshooting

### Issue: Containers won't start

**Symptoms:**
```
Error: port is already allocated
```

**Solution:**
```bash
# Check what's using the port
# Windows:
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# Linux/Mac:
lsof -i :5432
lsof -i :6379

# Kill the process or change ports in docker-compose.yml
```

### Issue: Database connection refused

**Symptoms:**
```
django.db.utils.OperationalError: could not connect to server
```

**Solution:**
```bash
# 1. Check if container is running
docker-compose ps

# 2. Check logs
docker-compose logs postgres

# 3. Wait for health check
docker inspect --format='{{.State.Health.Status}}' lumin-postgres

# 4. Restart container
docker-compose restart postgres
```

### Issue: Redis connection refused

**Symptoms:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution:**
```bash
# 1. Check if container is running
docker-compose ps

# 2. Check logs
docker-compose logs redis

# 3. Test connection
docker exec lumin-redis redis-cli ping

# 4. Restart container
docker-compose restart redis
```

### Issue: Data lost after restart

**Symptoms:**
Database is empty after `docker-compose down`

**Solution:**
```bash
# DON'T use -v flag when stopping
docker-compose down    # ✅ Keeps data
docker-compose down -v # ❌ Deletes data

# Verify volumes exist
docker volume ls | grep lumin
```

### Issue: Permission denied

**Symptoms:**
```
Permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
# Windows: Run Docker Desktop as Administrator

# Linux: Add user to docker group
sudo usermod -aG docker $USER
# Then logout and login again
```

### Issue: Containers running but can't connect

**Symptoms:**
Containers show as "Up" but connection fails

**Solution:**
```bash
# Check if services are listening on correct ports
docker exec lumin-postgres netstat -tuln | grep 5432
docker exec lumin-redis netstat -tuln | grep 6379

# Check Docker network
docker network inspect lumin_network

# Recreate containers
docker-compose down
docker-compose up -d
```

---

## 🚢 Production Deployment

### Building for Production

The included `Dockerfile` creates an optimized production image:

```bash
# Build production image
docker build -t lumin-backend:latest ./lumin-backend

# Run production container
docker run -d \
  --name lumin-backend \
  -p 8000:8000 \
  --env-file lumin-backend/.env \
  --network lumin_network \
  lumin-backend:latest
```

### Full Production Stack

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: lumin-postgres
    environment:
      POSTGRES_DB: lumin_db
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    container_name: lumin-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: always

  backend:
    build: ./lumin-backend
    container_name: lumin-backend
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.production
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    restart: always

  celery:
    build: ./lumin-backend
    container_name: lumin-celery
    command: celery -A config worker -l info
    depends_on:
      - postgres
      - redis
    restart: always

volumes:
  postgres_data:
  redis_data:
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📚 Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Documentation**: https://docs.docker.com/compose/
- **PostgreSQL Docker Hub**: https://hub.docker.com/_/postgres
- **Redis Docker Hub**: https://hub.docker.com/_/redis

---

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. View container logs: `docker-compose logs`
3. Check container status: `docker-compose ps`
4. Restart services: `docker-compose restart`
5. For persistent issues, recreate containers: `docker-compose down && docker-compose up -d`

---

**Happy Dockerizing! 🐳**

*Lumin - האור של העסק שלך*
