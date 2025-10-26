# 🚀 מדריך הפעלת Lumin

## דרישות מוקדמות
- Docker Desktop מותקן ופועל
- Python 3.12

---

## 📋 הפעלה מהירה (לאחר הפעלה מחדש של המחשב)

### אופציה 1: שימוש בקובץ האוטומטי
פשוט לחץ דאבל-קליק על:
```
start_lumin.bat
```

### אופציה 2: הפעלה ידנית (מומלץ לפתרון בעיות)

#### שלב 1: הפעלת Docker
```bash
docker compose up -d
```

#### שלב 2: הפעלת Django Server
```bash
cd lumin-backend
set DATABASE_URL=postgresql://postgres:lumin_dev_2025@127.0.0.1:5432/lumin_db
set DEBUG=True
set DJANGO_SETTINGS_MODULE=config.settings.development
venv\Scripts\python.exe manage.py runserver
```

**הערה חשובה:** חייבים להגדיר את משתני הסביבה (DATABASE_URL וכו') לפני הפעלת השרת!

#### שלב 3: גלוש לאתר
פתח דפדפן וגלוש ל:
```
http://localhost:8000
```

---

## 🔧 פתרון בעיות נפוצות

### שגיאה: `ERR_CONNECTION_REFUSED`
**פתרון:**
1. וודא ש-Docker Desktop פועל
2. בדוק שהשרת Django רץ (צריך לראות הודעה: `Starting development server at http://127.0.0.1:8000/`)

### שגיאה: `password authentication failed for user "postgres"`
**סיבה:** Django לא קורא את משתני הסביבה מקובץ .env

**פתרון:** פשוט השתמש בקובץ `start_lumin.bat` או הגדר את משתני הסביבה ידנית:
```bash
cd lumin-backend
set DATABASE_URL=postgresql://postgres:lumin_dev_2025@127.0.0.1:5432/lumin_db
set DEBUG=True
set DJANGO_SETTINGS_MODULE=config.settings.development
venv\Scripts\python.exe manage.py runserver
```

**אם זה עדיין לא עובד** - אפשר לנסות למחוק את ה-volumes:
```bash
docker compose down -v
docker compose up -d
# המתן 5 שניות ואז הפעל שוב עם משתני הסביבה
```

### Docker לא מגיב
**פתרון:**
1. פתח Docker Desktop ידנית
2. המתן עד שהסטטוס יהיה "Running"
3. נסה שוב

---

## 🛑 עצירת השרת

### עצירת Django:
לחץ `Ctrl + C` בחלון הטרמינל

### עצירת Docker:
```bash
docker compose down
```

---

## 📌 הערות חשובות
- **אל תסגור** את חלון הטרמינל של Django בזמן שאתה משתמש באתר
- אם אתה רואה אזהרות (WARNINGS) - אפשר להתעלם, זה נורמלי
- השרת צריך לרוץ על פורט 8000

---

## 🔐 פרטי התחברות למערכת
- התחבר דרך Google OAuth (אין צורך בסיסמה)
- לוח הבקרה: http://localhost:8000/dashboard/
- אדמין: http://localhost:8000/admin/

---

## 💾 גיבוי והחזר נתונים

### גיבוי מסד נתונים:
```bash
docker exec lumin-postgres pg_dump -U postgres lumin_db > backup.sql
```

### החזרת גיבוי:
```bash
docker exec -i lumin-postgres psql -U postgres lumin_db < backup.sql
```

---

נוצר בעזרת Claude Code ❤️
