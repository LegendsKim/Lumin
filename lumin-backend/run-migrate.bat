@echo off
REM Activate virtual environment and run migrations with correct DATABASE_URL

cd /d "%~dp0"
call venv\Scripts\activate.bat
set DATABASE_URL=postgresql://postgres@localhost:5432/lumin_db
set DEBUG=True
set DJANGO_SETTINGS_MODULE=config.settings.development

echo Running Django migrations with DATABASE_URL: %DATABASE_URL%
python manage.py migrate

pause
