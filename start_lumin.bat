@echo off
echo ==============================================
echo   Lumin - מערכת ניהול עסקי חכמה
echo ==============================================
echo.

echo [1/3] מפעיל Docker (PostgreSQL + Redis)...
docker compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Docker לא הצליח להפעיל. נא לבדוק שDocker Desktop פועל.
    pause
    exit /b 1
)

echo.
echo [2/3] ממתין לבסיס הנתונים...
timeout /t 5 /nobreak > nul

echo.
echo [3/4] מריץ migrations...
cd lumin-backend
venv\Scripts\python.exe manage.py migrate --noinput
if %errorlevel% neq 0 (
    echo ERROR: Migrations נכשלו. נא לבדוק את החיבור לבסיס הנתונים.
    pause
    exit /b 1
)

echo.
echo [4/4] מפעיל את שרת Django...
echo.
echo ============================================
echo   השרת פועל על: http://localhost:8000
echo   לעצירה: לחץ Ctrl+C
echo ============================================
echo.
venv\Scripts\python.exe manage.py runserver

pause
