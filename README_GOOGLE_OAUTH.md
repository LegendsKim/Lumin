# התחברות עם Google OAuth - מדריך מהיר

## ✅ מה שכבר מוכן

- ✅ דף התחברות יפה בעברית: http://localhost:8000/accounts/login/
- ✅ כפתור Google כחול (לא גרדיינט!)
- ✅ Google Client ID כבר מוגדר
- ✅ המערכת מוכנה לקבל משתמשים

---

## 🔑 המידע שלך

**Google Client ID:**
```
333006482129-1i8g1gtsquvfvk3e2uf8vaqb78rjq1p6.apps.googleusercontent.com
```

**Google Client Secret:**
```
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
```

---

## 📋 הגדרה ב-Google Cloud Console

### 1. כניסה לקונסול

1. היכנס ל-[Google Cloud Console](https://console.cloud.google.com/)
2. בחר את הפרויקט שלך

### 2. הגדרת Redirect URIs (החלק החשוב!)

1. לך ל-**APIs & Services** > **Credentials**
2. מצא את ה-OAuth 2.0 Client ID שלך
3. לחץ עליו לעריכה
4. תחת **Authorized redirect URIs**, הוסף:

```
http://localhost:8000/accounts/google/login/callback/
```

⚠️ **חשוב:** 
- הכתובת חייבת להיות **בדיוק** כך
- עם slash (/) בסוף!
- אם זה לא עובד, נסה גם:
  ```
  http://127.0.0.1:8000/accounts/google/login/callback/
  ```

5. לחץ **Save**

### 3. הוספת Authorized JavaScript origins

תחת **Authorized JavaScript origins**, הוסף:
```
http://localhost:8000
```

---

## 🧪 בדיקה

### 1. ודא שהשרת רץ

```bash
cd lumin-backend
venv\Scripts\python.exe manage.py runserver
```

### 2. פתח את דף ההתחברות

```
http://localhost:8000/accounts/login/
```

### 3. לחץ על "התחבר עם Google"

- אמור להעביר אותך ל-Google
- לאחר בחירת חשבון, אמור להחזיר אותך למערכת
- תיווצר משתמש חדש אוטומטית!

---

## ❌ פתרון בעיות

### שגיאה: "redirect_uri_mismatch"

**הפתרון:**
1. ודא שב-Google Console יש **בדיוק**:
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```
2. ודא שיש slash (/) בסוף
3. נסה גם את הגרסה עם 127.0.0.1

### שגיאה: "This app is blocked"

**הפתרון:**
1. לך ל-**OAuth consent screen** > **Test users**
2. לחץ **Add users**
3. הוסף את האימייל שלך
4. נסה שוב

### שגיאה: "invalid_client"

**הפתרון:**
1. ודא שב-`.env` יש את ה-Client ID ו-Secret הנכונים
2. הפעל מחדש את השרת

---

## 📊 איך זה עובד?

1. משתמש לוחץ "התחבר עם Google"
2. מועבר ל-Google OAuth
3. Google שואל אם לתת הרשאה ל-Lumin
4. לאחר אישור, Google מחזיר ל-`/accounts/google/login/callback/`
5. Django מיצר משתמש חדש (או מתחבר לקיים)
6. המשתמש מועבר לדף הבית

---

## 🎯 טיפים

- **משתמשים חדשים:** נוצרים אוטומטית עם האימייל מ-Google
- **משתמשים קיימים:** אם יש כבר משתמש עם אותו Google ID, פשוט מתחבר אליו
- **בטיחות:** Google מטפל בכל האבטחה - אין צורך בסיסמאות!
- **Tenant:** כל משתמש חדש צריך Tenant - אפשר ליצור אוטומטית או לבקש מהמשתמש

---

## 📁 קבצים רלוונטיים

- **דף התחברות:** `lumin-backend/templates/account/login.html`
- **הגדרות:** `lumin-backend/config/settings/base.py`
- **Environment:** `lumin-backend/.env`
- **Setup script:** `lumin-backend/setup_google_oauth.py`

---

## ✨ תכונות

✅ עיצוב מודרני בעברית
✅ כפתור Google כחול רשמי
✅ לוגו וסלוגן "Lumin - האור של העסק שלך"
✅ רשימת יתרונות
✅ הודעת פרטיות

---

**בהצלחה! 🚀**
