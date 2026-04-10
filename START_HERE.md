# 🚀 Lumin - מערכת ניהול עסקית

## ✅ המערכת מוכנה!

כל מה שצריך עכשיו זה להגדיר את ה-Redirect URI ב-Google Console ולהתחבר!

---

## 🔐 נתוני Google OAuth (מעודכנים!)

**Client ID:**
```
your-google-client-id
```

**Client Secret:**
```
your-google-client-secret
```

✅ כבר מעודכן ב-.env
✅ כבר מעודכן במסד הנתונים
✅ השרת רץ עם ההגדרות החדשות

---

## 📋 שלבים אחרונים (2 דקות!)

### 1. הגדר Redirect URI ב-Google Console

1. **פתח:** https://console.cloud.google.com/apis/credentials
2. **לחץ** על OAuth 2.0 Client ID שלך
3. **תחת "Authorized redirect URIs"**, לחץ **"+ ADD URI"**
4. **הוסף בדיוק:**
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```
5. **לחץ SAVE**

⚠️ **חשוב:** הכתובת חייבת להיות בדיוק כך, עם slash (/) בסוף!

### 2. (אופציונלי) הוסף JavaScript Origins

תחת **"Authorized JavaScript origins"**, הוסף:
```
http://localhost:8000
```

### 3. נסה להתחבר!

1. **פתח:** http://localhost:8000/accounts/login/
2. **לחץ** על הכפתור הכחול "התחבר עם Google"
3. **בחר** את החשבון Google שלך
4. **אשר** הרשאות
5. **תועבר** למערכת עם משתמש חדש!

---

## 🎯 לינקים מהירים

- 🔐 **התחברות:** http://localhost:8000/accounts/login/
- 🏠 **דף הבית:** http://localhost:8000/
- ⚙️ **Admin Panel:** http://localhost:8000/admin/
  - Email: admin@lumin.com
  - Password: admin123

---

## 🚀 הפעלת השרת

בכל פעם שאתה רוצה לעבוד על המערכת:

```bash
cd C:\Users\Marlen\Desktop\Projects\Lumin\lumin-backend
venv\Scripts\python.exe manage.py runserver
```

השרת יעלה על: **http://localhost:8000**

---

## 🎨 מה עשינו?

✅ דף התחברות מעוצב בעברית
✅ לוגו ✨ + סלוגן "האור של העסק שלך"
✅ כפתור Google כחול (לא גרדיינט!)
✅ יצירת Tenant אוטומטית למשתמשים חדשים
✅ כל משתמש Google הופך ל-ADMIN של העסק שלו
✅ SQLite במקום PostgreSQL (יותר פשוט לפיתוח)
✅ כל המיגרציות רצות בהצלחה

---

## 🆘 פתרון בעיות

### "redirect_uri_mismatch"
→ ודא שב-Google Console יש **בדיוק:**
```
http://localhost:8000/accounts/google/login/callback/
```

### "This app is blocked"
→ הוסף את עצמך כ-Test User:
1. Google Console > OAuth consent screen
2. Test users > Add users
3. הוסף את האימייל שלך

### "invalid_client"
→ ודא שה-Client ID ו-Secret נכונים ב-.env
→ הפעל מחדש את השרver

---

## 📚 קבצים חשובים

- `.env` - משתני סביבה (Google credentials)
- `templates/account/login.html` - דף התחברות
- `apps/accounts/social_signals.py` - יצירת Tenant אוטומטית
- `db.sqlite3` - מסד הנתונים

---

## 🎉 מה קורה אחרי התחברות?

1. **Google מאמת** את זהות המשתמש
2. **Django יוצר** משתמש חדש עם האימייל מ-Google
3. **Signal יוצר** Tenant חדש אוטומטית
4. **המשתמש הופך** ל-ADMIN של העסק שלו
5. **מועבר** לדף הבית

---

## 💡 טיפ

אחרי התחברות מוצלחת, תוכל לראות את המשתמש החדש ב-Admin Panel:
- http://localhost:8000/admin/
- היכנס עם admin@lumin.com / admin123
- לך ל-"Users" ותראה את המשתמש החדש!

---

**בהצלחה! 🚀**

יש בעיה? בדוק את README_GOOGLE_OAUTH.md למידע מפורט יותר.
