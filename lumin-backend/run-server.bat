@echo off
docker run --rm ^
  --network=lumin_network ^
  -v "%cd%://app" ^
  -w //app ^
  -p 8000:8000 ^
  -e DATABASE_URL=postgresql://postgres:lumin_dev_2025@lumin-postgres:5432/lumin_db ^
  -e DJANGO_SETTINGS_MODULE=config.settings.development ^
  -e DEBUG=True ^
  python:3.11-slim ^
  sh -c "pip install -q -r requirements.txt && python manage.py runserver 0.0.0.0:8000"