# תיעוד: מערכת הרשאות מבוססת תוכנית (Plan-Based Permissions)

## 📋 סקירה כללית

מערכת זו מאפשרת אכיפה מלאה של מגבלות תוכנית BASIC vs PRO, כולל:
- **אכיפת מגבלות ב-Backend** (Hard limits)
- **הסתרת UI ב-Frontend** (לחוויית משתמש טובה)
- **נעילת חשבון אוטומטית** אם חורגים מהמגבלה

---

## 🎯 מגבלות התוכניות

### BASIC (חינם):
| משאב | מגבלה |
|------|-------|
| לקוחות | 10 |
| מוצרים | 10 |
| מטפלים | 1 |
| אחסון S3 | 5MB לקובץ |
| סנכרון WooCommerce | ייבוא חד-פעמי בלבד (10+10) |
| SMS Marketing | ❌ לא זמין |
| Webhooks | ❌ לא זמין |

### PRO (בתשלום):
| משאב | מגבלה |
|------|-------|
| **הכל** | **ללא הגבלה** |

---

## 🔒 מנגנון נעילת חשבון (Account Locking)

### מתי חשבון ננעל?
חשבון BASIC ינעל אוטומטית (`LOCKED_BASIC`) אם:
1. ייבוא WooCommerce הביא למעל 10 לקוחות
2. ייבוא WooCommerce הביא למעל 10 מוצרים
3. (עתידי) ניסיונות חוזרים לעבור מגבלות

### מה קורה כשחשבון נעול?
- **Backend**: כל פעולות CREATE נחסמות (customers, products, staff, etc.)
- **Frontend**: המערכת כולה נכנסת ל**מצב קריאה בלבד**:
  - באנר אזהרה אדום בראש כל דף
  - כל כפתורי ההוספה, העריכה, המחיקה מנוטרלים
  - הכפתורים מוחלפים ב"שדרג ל-Pro"

### איך לפתוח נעילה?
```python
tenant = Tenant.objects.get(id=tenant_id)
tenant.plan = 'PRO'
tenant.unlock_account()
tenant.save()
```

---

## 🛠️ Backend API

### Endpoint: בדיקת תכונות
```
GET /api/auth/features/
```

**Response Example:**
```json
{
  "plan": "BASIC",
  "account_status": "LOCKED_BASIC",
  "is_locked": true,
  "limits": {
    "max_customers": 10,
    "max_products": 10,
    "max_staff_members": 1,
    "max_s3_storage_mb": 5
  },
  "current": {
    "customers": 12,
    "products": 8,
    "staff_members": 1
  },
  "features": {
    "woocommerce_full_sync": false,
    "woocommerce_basic_import": true,
    "sms_marketing": false,
    "sms_verification": true,
    "s3_uploads": true,
    "unlimited_customers": false,
    "unlimited_products": false,
    "unlimited_staff": false,
    "unlimited_storage": false
  },
  "can_add": {
    "customer": false,
    "product": false,
    "staff_member": false
  }
}
```

---

## 💻 Frontend - מה שנותר לעשות

### שלב 1: יצירת קובץ JavaScript Helper

**קובץ**: `static/js/plan-features.js`

```javascript
/**
 * Plan Features Helper
 * Manages plan-based UI behavior
 */

// Global state
window.luminFeatures = {
    plan: null,
    account_status: null,
    is_locked: false,
    limits: {},
    current: {},
    features: {},
    can_add: {},
    loaded: false
};

/**
 * Fetch features from API
 */
async function loadPlanFeatures() {
    try {
        const response = await fetch('/api/auth/features/', {
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
            }
        });

        if (!response.ok) {
            console.error('Failed to load plan features');
            return false;
        }

        const data = await response.json();
        window.luminFeatures = { ...data, loaded: true };

        // Apply UI changes immediately
        applyPlanRestrictions();

        return true;
    } catch (error) {
        console.error('Error loading plan features:', error);
        return false;
    }
}

/**
 * Check if account is locked
 */
function isAccountLocked() {
    return window.luminFeatures.is_locked === true;
}

/**
 * Check if can add a resource
 */
function canAdd(resource) {
    if (isAccountLocked()) return false;
    return window.luminFeatures.can_add[resource] === true;
}

/**
 * Check if has a feature
 */
function hasFeature(featureName) {
    return window.luminFeatures.features[featureName] === true;
}

/**
 * Get usage percentage for a resource
 */
function getUsagePercentage(resource) {
    const current = window.luminFeatures.current[resource + 's'] || 0;
    const max = window.luminFeatures.limits['max_' + resource + 's'];

    if (!max) return 0;
    return Math.round((current / max) * 100);
}

/**
 * Apply plan restrictions to UI
 */
function applyPlanRestrictions() {
    // Show locked banner if account is locked
    if (isAccountLocked()) {
        showLockedBanner();
        disableAllActions();
    }

    // Hide/disable buttons based on can_add
    if (!canAdd('customer')) {
        disableButton('.add-customer-btn', 'לקוחות');
    }
    if (!canAdd('product')) {
        disableButton('.add-product-btn', 'מוצרים');
    }
    if (!canAdd('staff_member')) {
        disableButton('.add-staff-btn', 'מטפלים');
    }

    // Hide PRO features
    if (!hasFeature('woocommerce_full_sync')) {
        hideElement('.woocommerce-webhooks');
    }
    if (!hasFeature('sms_marketing')) {
        hideElement('.sms-marketing-section');
    }
}

/**
 * Show locked account banner
 */
function showLockedBanner() {
    const banner = document.createElement('div');
    banner.className = 'locked-account-banner';
    banner.innerHTML = `
        <div class="banner-content">
            <span class="banner-icon">🔒</span>
            <div class="banner-text">
                <strong>חשבון נעול</strong> - עברת את מגבלת התוכנית.
                המערכת במצב קריאה בלבד.
            </div>
            <button class="upgrade-btn" onclick="showUpgradeModal()">
                שדרג ל-Pro לשחרור הנעילה
            </button>
        </div>
    `;

    // Insert at top of body
    document.body.insertBefore(banner, document.body.firstChild);
}

/**
 * Disable all action buttons
 */
function disableAllActions() {
    const selectors = [
        '.add-customer-btn',
        '.add-product-btn',
        '.add-staff-btn',
        '.edit-btn',
        '.delete-btn',
        'button[type="submit"]'
    ];

    selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.disabled = true;
            el.classList.add('disabled');
            el.title = 'חשבון נעול - שדרג ל-Pro';
        });
    });
}

/**
 * Disable specific button and replace with upgrade prompt
 */
function disableButton(selector, resourceName) {
    const buttons = document.querySelectorAll(selector);
    buttons.forEach(button => {
        button.style.display = 'none';

        // Create upgrade button
        const upgradeBtn = document.createElement('button');
        upgradeBtn.className = 'upgrade-prompt-btn';
        upgradeBtn.innerHTML = `⭐ שדרג ל-Pro להוספת ${resourceName}`;
        upgradeBtn.onclick = () => showUpgradeModal();

        button.parentNode.insertBefore(upgradeBtn, button.nextSibling);
    });
}

/**
 * Hide element
 */
function hideElement(selector) {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => {
        el.style.display = 'none';
    });
}

/**
 * Show upgrade modal
 */
function showUpgradeModal() {
    alert('שדרוג ל-Pro יפתח בקרוב! צור קשר: support@lumin.co.il');
    // TODO: Implement actual upgrade flow
}

// Auto-load on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadPlanFeatures();
});
```

---

### שלב 2: הוספת CSS לבאנר ולכפתורים

**הוסף ל**: `templates/dashboard.html` (ובכל template אחר)

```html
<style>
/* Locked Account Banner */
.locked-account-banner {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: linear-gradient(135deg, #dc2626, #991b1b);
    color: white;
    padding: 16px 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    animation: slideDown 0.3s ease;
}

@keyframes slideDown {
    from {
        transform: translateY(-100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.banner-content {
    display: flex;
    align-items: center;
    gap: 16px;
    max-width: 1200px;
    margin: 0 auto;
}

.banner-icon {
    font-size: 24px;
}

.banner-text {
    flex: 1;
    font-size: 15px;
    line-height: 1.5;
}

.banner-text strong {
    font-weight: 700;
}

.upgrade-btn {
    background: white;
    color: #dc2626;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.upgrade-btn:hover {
    background: #fef2f2;
    transform: scale(1.05);
}

/* Upgrade Prompt Button */
.upgrade-prompt-btn {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.upgrade-prompt-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

/* Disabled Elements */
button.disabled,
button:disabled {
    opacity: 0.5;
    cursor: not-allowed !important;
    pointer-events: none;
}
</style>
```

---

### שלב 3: טעינת הסקריפט בכל הדפים

**הוסף לפני `</body>` בכל template**:

```html
<script src="/static/js/plan-features.js"></script>
```

---

### שלב 4: שימוש בפונקציות

**דוגמה - לפני הוספת לקוח**:

```html
<button class="add-customer-btn" onclick="addCustomer()">
    + הוסף לקוח
</button>

<script>
async function addCustomer() {
    // Check if can add
    if (!canAdd('customer')) {
        showUpgradeModal();
        return;
    }

    // Continue with add logic...
}
</script>
```

---

## 🧪 בדיקות

### בדיקה 1: API עובד
```bash
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/auth/features/
```

### בדיקה 2: נעילת חשבון
```python
from apps.accounts.models import Tenant
tenant = Tenant.objects.first()
tenant.check_and_lock_if_over_limit()  # Should lock if over limit
```

### בדיקה 3: ניסיון הוספת לקוח מעבר למגבלה
```bash
# Should return 403 with error message
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/customers/ \
  -d '{"first_name": "Test", "last_name": "User"}'
```

---

## 📝 TODO List נותר

- [ ] יצירת `static/js/plan-features.js`
- [ ] הוספת CSS לבאנר נעילה
- [ ] טעינת הסקריפט ב-dashboard.html
- [ ] טעינת הסקריפט ב-customers.html
- [ ] טעינת הסקריפט ב-products.html
- [ ] טעינת הסקריפט ב-sync.html
- [ ] טעינת הסקריפט ב-coupons.html
- [ ] הוספת `class="add-customer-btn"` לכפתור הוספת לקוח
- [ ] הוספת `class="add-product-btn"` לכפתור הוספת מוצר
- [ ] הוספת `class="add-staff-btn"` לכפתור הוספת מטפל
- [ ] יצירת דף Upgrade (עתידי)
- [ ] אינטגרציה עם Stripe לתשלומים (עתידי)

---

## 🎉 סיכום

**Backend**: ✅ מוכן לגמרי!
**Frontend**: ⏳ צריך רק להוסיף את הקבצים לעיל

המערכת נבנתה בצורה מודולרית וגמישה. קל להוסיף פיצ'רים חדשים או לשנות מגבלות פשוט על ידי עדכון ה-Tenant model.

**Next Steps**: העתק את הקוד JavaScript ו-CSS מהתיעוד הזה לקבצים המתאימים, והכל יעבוד!
