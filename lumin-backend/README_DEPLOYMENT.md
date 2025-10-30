# 🚀 Lumin SaaS - Deployment Guide (Render)

מדריך מקיף לפריסת פרויקט Lumin ב-Render.

---

## 📋 תוכן עניינים

1. [דרישות מקדימות](#דרישות-מקדימות)
2. [הכנת הפרויקט](#הכנת-הפרויקט)
3. [פריסה ב-Render](#פריסה-ב-render)
4. [הגדרת משתני סביבה](#הגדרת-משתני-סביבה)
5. [בדיקות לאחר הפריסה](#בדיקות-לאחר-הפריסה)
6. [פתרון בעיות](#פתרון-בעיות)
7. [שדרוגים עתידיים](#שדרוגים-עתידיים)

---

## 🔧 דרישות מקדימות

### חשבונות נדרשים:
- ✅ חשבון GitHub (לאחסון הקוד)
- ✅ חשבון Render (https://render.com)
- 📝 חשבון AWS (אופציונלי - לאחסון קבצים ב-S3)
- 📧 חשבון SendGrid (אופציונלי - לשליחת מיילים)
- 📱 חשבון Twilio (אופציונלי - לאימות SMS)

### מה כבר מוכן:
- ✅ **requirements.txt** - עודכן עם כל התלויות
- ✅ **config/settings/base.py** - תמיכה ב-DATABASE_URL אוטומטי
- ✅ **config/settings/production.py** - הגדרות אבטחה לפרודקשן
- ✅ **build.sh** - סקריפט build אוטומטי
- ✅ **render.yaml** - Blueprint להגדרת כל השירותים
- ✅ **.env.example** - תבנית למשתני סביבה

---

## 📦 הכנת הפרויקט

### 1. ודא שכל הקבצים committed

```bash
git add .
git commit -m "feat: prepare for Render deployment"
git push origin main
```

### 2. ודא ש-.gitignore כולל:

```
.env
db.sqlite3
*.pyc
__pycache__/
media/
staticfiles/
```

---

## 🌐 פריסה ב-Render

### אופציה 1: שימוש ב-Blueprint (מומלץ)

1. **התחבר ל-Render**: https://dashboard.render.com

2. **לחץ על "New" → "Blueprint"**

3. **חבר את ה-Repository שלך**:
   - בחר את הארגון/משתמש שלך ב-GitHub
   - בחר את repository של Lumin

4. **Render יזהה את `render.yaml` אוטומטית**

5. **לחץ "Apply"** - Render ייצור 3 שירותים:
   - `lumin-web` (Web Service)
   - `lumin-db` (PostgreSQL)
   - `lumin-redis` (Redis)

6. **המתן לסיום הבנייה** (~5-10 דקות)

### אופציה 2: פריסה ידנית (אם Blueprint לא עובד)

<details>
<summary>לחץ להרחבה</summary>

#### שלב 1: יצירת PostgreSQL Database
1. New → PostgreSQL
2. Name: `lumin-db`
3. Region: Oregon
4. Plan: Free
5. Create Database

#### שלב 2: יצירת Redis
1. New → Redis
2. Name: `lumin-redis`
3. Region: Oregon
4. Plan: Free
5. Create Redis

#### שלב 3: יצירת Web Service
1. New → Web Service
2. Connect repository
3. Settings:
   - Name: `lumin-web`
   - Region: Oregon
   - Branch: `main`
   - Runtime: Python 3
   - Build Command: `./build.sh`
   - Start Command: `gunicorn config.wsgi:application`
   - Plan: Free

#### שלב 4: קישור Database ו-Redis
ראה סעיף [הגדרת משתני סביבה](#הגדרת-משתני-סביבה) למטה.

</details>

---

## 🔐 הגדרת משתני סביבה

### משתנים שהוגדרו אוטומטית:
- ✅ `DATABASE_URL` - מקושר מ-PostgreSQL
- ✅ `REDIS_URL` - מקושר מ-Redis
- ✅ `SECRET_KEY` - נוצר אוטומטית

### משתנים שצריך להוסיף ידנית:

1. **עבור אל Dashboard → lumin-web → Environment**

2. **הוסף את המשתנים הבאים**:

```bash
# חובה
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
ALLOWED_HOSTS=.onrender.com
CORS_ALLOWED_ORIGINS=https://lumin-app.onrender.com
CSRF_TRUSTED_ORIGINS=https://*.onrender.com

# אופציונלי - AWS S3 (כשמוכן)
USE_S3=True
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_STORAGE_BUCKET_NAME=<your-bucket>
AWS_S3_REGION_NAME=us-east-1

# אופציונלי - SendGrid Email
SENDGRID_API_KEY=<your-api-key>
DEFAULT_FROM_EMAIL=noreply@lumin.app

# אופציונלי - Twilio SMS
TWILIO_ACCOUNT_SID=<your-sid>
TWILIO_AUTH_TOKEN=<your-token>
TWILIO_PHONE_NUMBER=+1234567890

# אופציונלי - Google OAuth
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-secret>
```

3. **שמור את השינויים** - Render יעשה redeploy אוטומטית

---

## ✅ בדיקות לאחר הפריסה

### 1. בדוק שהאתר עובד:
```
https://lumin-web.onrender.com
```

### 2. בדוק את ה-Admin:
```
https://lumin-web.onrender.com/admin/
```

### 3. צור superuser:
```bash
# בעמוד Render Dashboard → lumin-web → Shell
python manage.py createsuperuser
```

### 4. בדוק logs:
```
Render Dashboard → lumin-web → Logs
```

---

## 🔧 פתרון בעיות

### Build Failed

**בעיה**: `./build.sh: Permission denied`

**פתרון**:
```bash
chmod +x build.sh
git add build.sh
git commit -m "fix: make build.sh executable"
git push
```

---

### Database Connection Error

**בעיה**: `FATAL: no pg_hba.conf entry`

**פתרון**:
1. וודא ש-`DATABASE_URL` מוגדר נכון
2. בדוק ב-Render Dashboard → lumin-db → Connections
3. וודא ש-Web Service מחובר לDB

---

### Static Files Not Loading

**בעיה**: CSS/JS לא נטענים

**פתרון זמני** (Whitenoise):
```bash
# Settings כבר מוגדרים נכון
# אם עדיין לא עובד, בדוק:
STATICFILES_STORAGE=whitenoise.storage.CompressedManifestStaticFilesStorage
```

**פתרון קבוע** (S3 - מומלץ):
1. צור S3 bucket ב-AWS
2. הגדר את משתני הסביבה:
   ```
   USE_S3=True
   AWS_ACCESS_KEY_ID=xxx
   AWS_SECRET_ACCESS_KEY=xxx
   AWS_STORAGE_BUCKET_NAME=xxx
   ```
3. Redeploy

---

### Redis Connection Error

**בעיה**: `Error connecting to Redis`

**פתרון**:
1. וודא ש-`REDIS_URL` מוגדר
2. בדוק שה-Redis service פעיל:
   ```
   Render Dashboard → lumin-redis → Status
   ```

---

### CSRF Verification Failed

**בעיה**: CSRF errors במעבר בין דפים

**פתרון**:
הוסף את הדומיין ל-`CSRF_TRUSTED_ORIGINS`:
```bash
CSRF_TRUSTED_ORIGINS=https://lumin-web.onrender.com,https://*.onrender.com
```

---

## 🚀 שדרוגים עתידיים

### Celery Worker (לטאסקים אסינכרוניים)

אם תצטרך Celery:

1. **צור Background Worker ב-Render**:
   - New → Background Worker
   - Repository: (אותו repository)
   - Start Command: `celery -A config worker -l info`

2. **צור Celery Beat (לטאסקים מתוזמנים)**:
   - New → Background Worker
   - Start Command: `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

---

### Custom Domain

1. Render Dashboard → lumin-web → Settings → Custom Domain
2. הוסף את הדומיין שלך (למשל: `app.lumin.co.il`)
3. עדכן DNS records אצל רשם הדומיינים:
   ```
   CNAME record:
   app.lumin.co.il → lumin-web.onrender.com
   ```
4. עדכן `ALLOWED_HOSTS`:
   ```
   ALLOWED_HOSTS=.onrender.com,app.lumin.co.il
   ```

---

### Auto-Deploy מ-GitHub

כבר מוגדר! כל push ל-`main` branch יפעיל deploy אוטומטי.

לנטרול:
```
Render Dashboard → lumin-web → Settings → Auto-Deploy → Disable
```

---

## 📚 משאבים נוספים

- [Render Docs](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Render Blueprint Spec](https://render.com/docs/blueprint-spec)

---

## 🆘 תמיכה

אם נתקלת בבעיה:
1. בדוק את ה-logs ב-Render Dashboard
2. חפש בתיעוד של Render
3. פתח issue ב-GitHub repository

---

**בהצלחה! 🎉**
