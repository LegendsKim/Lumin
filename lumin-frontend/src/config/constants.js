/**
 * Global constants for Lumin SaaS application.
 */

// Application Info
export const APP_NAME = 'Lumin';
export const APP_TAGLINE = 'האור של העסק שלך';
export const VERSION = '1.0.0';

// Routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  REGISTER_TENANT: '/register-tenant',
  DASHBOARD: '/dashboard',
  INVENTORY: '/inventory',
  PRODUCTS: '/products',
  PRODUCT_DETAIL: '/products/:id',
  SALES: '/sales',
  ORDERS: '/orders',
  ORDER_DETAIL: '/orders/:id',
  CUSTOMERS: '/customers',
  CUSTOMER_DETAIL: '/customers/:id',
  ANALYTICS: '/analytics',
  SETTINGS: '/settings',
  PROFILE: '/profile',
  NOT_FOUND: '/404',
};

// User Roles
export const USER_ROLES = {
  ADMIN: 'ADMIN',
  BASIC_STAFF: 'BASIC_STAFF',
};

export const ROLE_LABELS = {
  [USER_ROLES.ADMIN]: 'מנהל',
  [USER_ROLES.BASIC_STAFF]: 'צוות',
};

// Plan Types
export const PLAN_TYPES = {
  BASIC: 'BASIC',
  PRO: 'PRO',
};

export const PLAN_LABELS = {
  [PLAN_TYPES.BASIC]: 'בסיסי',
  [PLAN_TYPES.PRO]: 'מקצועי',
};

// Plan Limits
export const PLAN_LIMITS = {
  [PLAN_TYPES.BASIC]: {
    max_products: 10,
    max_customers: 5,
  },
  [PLAN_TYPES.PRO]: {
    max_products: Infinity,
    max_customers: Infinity,
  },
};

// Payment Methods
export const PAYMENT_METHODS = [
  { value: 'cash', label: 'מזומן' },
  { value: 'credit_card', label: 'כרטיס אשראי' },
  { value: 'debit_card', label: 'כרטיס חיוב' },
  { value: 'bank_transfer', label: 'העברה בנקאית' },
  { value: 'digital_wallet', label: 'ארנק דיגיטלי' },
  { value: 'other', label: 'אחר' },
];

// Date Formats
export const DATE_FORMATS = {
  DISPLAY: 'dd/MM/yyyy',
  DISPLAY_WITH_TIME: 'dd/MM/yyyy HH:mm',
  API: 'yyyy-MM-dd',
  API_WITH_TIME: "yyyy-MM-dd'T'HH:mm:ss",
};

// Pagination
export const DEFAULT_PAGE_SIZE = 50;
export const PAGE_SIZE_OPTIONS = [25, 50, 100, 200];

// File Upload
export const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

// API Endpoints (relative to base URL)
export const API_ENDPOINTS = {
  // Auth & Users (unified under accounts)
  AUTH_PHONE_REQUEST: '/api/accounts/phone/request/',
  AUTH_PHONE_VERIFY: '/api/accounts/phone/verify/',
  AUTH_REGISTER_TENANT: '/api/accounts/register-tenant/',
  AUTH_LOGOUT: '/api/accounts/logout/',

  // Users
  USERS_ME: '/api/accounts/me/',
  USERS_INVITE: '/api/accounts/invite/',

  // Products
  PRODUCTS: '/api/products/',
  PRODUCTS_LOW_STOCK: '/api/products/low-stock/',
  PRODUCTS_EXPORT: '/api/products/export/',
  PRODUCT_ADJUST_STOCK: (id) => `/api/products/${id}/adjust-stock/`,

  // Orders
  ORDERS: '/api/orders/',
  ORDERS_TODAY: '/api/orders/today/',
  ORDERS_STATS: '/api/orders/stats/',
  ORDERS_EXPORT: '/api/orders/export/',

  // Customers
  CUSTOMERS: '/api/customers/',
  CUSTOMERS_SEARCH: '/api/customers/search/',
  CUSTOMERS_TOP: '/api/customers/top/',
  CUSTOMERS_EXPORT: '/api/customers/export/',

  // Analytics
  ANALYTICS_DASHBOARD: '/api/analytics/dashboard/',
  ANALYTICS_SALES_CHART: '/api/analytics/sales-chart/',
  ANALYTICS_TOP_PRODUCTS: '/api/analytics/top-products/',
};

// Chart Colors
export const CHART_COLORS = {
  primary: '#00ADB5',
  secondary: '#8c7ae6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#3b82f6',
  gradient: ['#8c7ae6', '#c56cf0', '#f64e60'],
};

// Toast Duration
export const TOAST_DURATION = 4000; // 4 seconds

// Session Timeout
export const SESSION_TIMEOUT = 20 * 60 * 1000; // 20 minutes in milliseconds

// Debounce Delay
export const DEBOUNCE_DELAY = 500; // 500ms

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'שגיאת רשת. אנא בדוק את החיבור לאינטרנט.',
  UNAUTHORIZED: 'אין הרשאה. אנא התחבר מחדש.',
  FORBIDDEN: 'אין לך הרשאה לבצע פעולה זו.',
  NOT_FOUND: 'הפריט המבוקש לא נמצא.',
  SERVER_ERROR: 'שגיאת שרת. אנא נסה שוב מאוחר יותר.',
  VALIDATION_ERROR: 'שגיאת אימות. אנא בדוק את הנתונים שהוזנו.',
  LIMIT_REACHED: 'הגעת למגבלת התוכנית שלך.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  SAVED: 'השינויים נשמרו בהצלחה',
  CREATED: 'נוצר בהצלחה',
  UPDATED: 'עודכן בהצלחה',
  DELETED: 'נמחק בהצלחה',
  SENT: 'נשלח בהצלחה',
};
