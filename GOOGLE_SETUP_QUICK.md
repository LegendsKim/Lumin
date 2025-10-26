# 🚀 הגדרת Google OAuth - מדריך מהיר (5 דקות)

## שלב 1: השלמת ההרשמה ב-Google Cloud (שכבר התחלת)

אני רואה שהגעת לשלב תשלום ב-Google Cloud. **אל תדאג - זה חינם לחלוטין!**

### מה לעשות:

1. **לחץ על "Start free"** בדף שפתחת
2. **מלא פרטי כרטיס אשראי** - Google לא תחייב אותך אלא אם תעבור ל-Premium באופן ידני
3. **אשר והמשך**

---

## שלב 2: יצירת OAuth Credentials

לאחר שנכנסת ל-Google Cloud Console:

### 2.1 יצור פרויקט (אם עוד לא יצרת)

1. למעלה ליד הלוגו של Google Cloud, לחץ על **"Select a project"**
2. לחץ **"NEW PROJECT"**
3. שם הפרויקט: `Lumin`
4. לחץ **"CREATE"**

### 2.2 הגדר OAuth Consent Screen

1. בתפריט השמאלי (☰), עבור ל:
   **APIs & Services** → **OAuth consent screen**

2. בחר **"External"** ← לחץ **"CREATE"**

3. מלא את הפרטים:
   - **App name:** `Lumin`
   - **User support email:** (בחר את האימייל שלך)
   - **Developer contact information:** (האימייל שלך)

4. לחץ **"SAVE AND CONTINUE"**

5. בדף **Scopes**:
   - לחץ **"ADD OR REMOVE SCOPES"**
   - בחר את:
     - ✅ `.../auth/userinfo.email`
     - ✅ `.../auth/userinfo.profile`
   - לחץ **"UPDATE"** ← **"SAVE AND CONTINUE"**

6. בדף **Test users**:
   - לחץ **"ADD USERS"**
   - הוסף את **האימייל שלך** (זה שתשתמש בו לבדיקות)
   - לחץ **"ADD"** ← **"SAVE AND CONTINUE"**

7. לחץ **"BACK TO DASHBOARD"**

### 2.3 צור OAuth Client ID

1. בתפריט השמאלי, עבור ל:
   **APIs & Services** → **Credentials**

2. למעלה, לחץ **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**

3. בחר:
   - **Application type:** `Web application`
   - **Name:** `Lumin Local`

4. ב-**Authorized redirect URIs**, לחץ **"+ ADD URI"** והוסף:
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```

5. שוב **"+ ADD URI"** והוסף:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

6. לחץ **"CREATE"**

7. **תראה חלון עם Client ID ו-Client Secret** - **העתק אותם!**

---

## שלב 3: עדכון .env והרצת הסקריפט

### 3.1 עדכן את .env

פתח את הקובץ `.env` והחלף את השורות:

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

ב-**ערכים האמיתיים** שקיבלת מGoogle:

```env
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcd1234efgh5678ijkl
```

### 3.2 הרץ סקריפט הגדרה

```bash
cd c:/Users/Marlen/Desktop/Projects/Lumin/lumin-backend
docker exec nice_meninsky python manage.py shell < setup_google_oauth.py
```

אם הכל עבד, תראה:

```
✓ Site already exists: Lumin Local
✓ Created Google OAuth app
✓ Added site to Google OAuth app

🎉 Google OAuth setup completed successfully!
```

### 3.3 הפעל מחדש את השרת

```bash
docker-compose restart
```

---

## שלב 4: בדוק שזה עובד!

1. פתח: `http://localhost:8000/register/`
2. לחץ על **"התחילו עם Google"**
3. בחר את החשבון שלך (שהוספת כTest User)
4. אמור להגיע ל**דף השלמת הפרטים** עם האימייל שלך כבר ממולא ונעול! ✨

---

## ❓ שאלות נפוצות

**ש: למה Google דורשת כרטיס אשראי?**
ת: לאימות זהות. לא יחייבו אותך אלא אם תעבור ידנית ל-Premium.

**ש: כמה זה עולה?**
ת: 0₪. Google OAuth API חינמי לחלוטין עד מיליון משתמשים.

**ש: מה אם אני לא רוצה להזין כרטיס?**
ת: אז פשוט השתמש ב**הרשמה הרגילה** (אימייל וסיסמה) שכבר עובדת מצוין!

**ש: קיבלתי "This app is blocked"**
ת: זה בגלל שהאפליקציה במצב Testing. ודא שהוספת את עצמך כTest User בשלב 2.2.

---

## 🎯 לסיכום

1. השלם הרשמה ב-Google Cloud (חינם!)
2. צור OAuth Client ID
3. העתק Client ID + Secret ל-.env
4. הרץ סקריפט: `docker exec nice_meninsky python manage.py shell < setup_google_oauth.py`
5. הפעל מחדש: `docker-compose restart`
6. נסה להירשם! 🚀

**זמן משוער: 5-10 דקות** ⏱️
