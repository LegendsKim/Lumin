/**
 * Plan Features Helper
 * Manages plan-based UI behavior and restrictions
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

        console.log('Plan features loaded:', window.luminFeatures);

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
    console.log('Applying plan restrictions...');

    // Show locked banner if account is locked
    if (isAccountLocked()) {
        showLockedBanner();
        disableAllActions();
        return; // If locked, disable everything
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

    // Hide PRO features for BASIC users
    if (!hasFeature('woocommerce_full_sync')) {
        hideElement('.woocommerce-webhooks');
    }
    if (!hasFeature('sms_marketing')) {
        hideElement('.sms-marketing-section');
    }

    console.log('Plan restrictions applied');
}

/**
 * Show locked account banner
 */
function showLockedBanner() {
    // Check if banner already exists
    if (document.querySelector('.locked-account-banner')) {
        return;
    }

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
 * Disable all action buttons (for locked accounts)
 */
function disableAllActions() {
    console.log('Disabling all actions due to locked account...');

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
            el.style.opacity = '0.5';
            el.style.cursor = 'not-allowed';
        });
    });
}

/**
 * Disable specific button and replace with upgrade prompt
 */
function disableButton(selector, resourceName) {
    const buttons = document.querySelectorAll(selector);

    buttons.forEach(button => {
        // Hide original button
        button.style.display = 'none';

        // Create upgrade button
        const upgradeBtn = document.createElement('button');
        upgradeBtn.className = 'upgrade-prompt-btn';
        upgradeBtn.type = 'button';
        upgradeBtn.innerHTML = `⭐ שדרג ל-Pro להוספת ${resourceName}`;
        upgradeBtn.onclick = (e) => {
            e.preventDefault();
            showUpgradeModal();
        };

        // Insert after original button
        button.parentNode.insertBefore(upgradeBtn, button.nextSibling);
    });

    console.log(`Disabled ${buttons.length} buttons for ${resourceName}`);
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
    const counts = window.luminFeatures.current;
    const limits = window.luminFeatures.limits;

    let message = 'שדרג ל-Pro כדי להסיר את כל המגבלות!\n\n';
    message += `📊 המצב הנוכחי שלך:\n`;
    message += `• לקוחות: ${counts.customers || 0}/${limits.max_customers || '∞'}\n`;
    message += `• מוצרים: ${counts.products || 0}/${limits.max_products || '∞'}\n`;
    message += `• מטפלים: ${counts.staff_members || 0}/${limits.max_staff_members || '∞'}\n\n`;
    message += 'מסלול Pro כולל:\n';
    message += '✓ ללא הגבלת לקוחות, מוצרים ומטפלים\n';
    message += '✓ סנכרון מלא עם WooCommerce\n';
    message += '✓ שיווק SMS\n';
    message += '✓ אחסון ללא הגבלה\n\n';
    message += 'צור קשר: support@lumin.co.il';

    alert(message);

    // TODO: Implement actual upgrade flow with payment
}

/**
 * Display usage stats (optional - for dashboard)
 */
function displayUsageStats() {
    const statsContainer = document.getElementById('usage-stats');
    if (!statsContainer || !window.luminFeatures.loaded) return;

    const { current, limits } = window.luminFeatures;

    const html = `
        <div class="usage-stats">
            <div class="stat-item">
                <div class="stat-label">לקוחות</div>
                <div class="stat-bar">
                    <div class="stat-progress" style="width: ${getUsagePercentage('customer')}%"></div>
                </div>
                <div class="stat-text">${current.customers || 0} / ${limits.max_customers || '∞'}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">מוצרים</div>
                <div class="stat-bar">
                    <div class="stat-progress" style="width: ${getUsagePercentage('product')}%"></div>
                </div>
                <div class="stat-text">${current.products || 0} / ${limits.max_products || '∞'}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">מטפלים</div>
                <div class="stat-bar">
                    <div class="stat-progress" style="width: ${getUsagePercentage('staff_member')}%"></div>
                </div>
                <div class="stat-text">${current.staff_members || 0} / ${limits.max_staff_members || '∞'}</div>
            </div>
        </div>
    `;

    statsContainer.innerHTML = html;
}

// Auto-load on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Loading plan features...');
    await loadPlanFeatures();

    // Display usage stats if container exists
    displayUsageStats();
});

// Export functions for use in other scripts
window.planFeatures = {
    isAccountLocked,
    canAdd,
    hasFeature,
    getUsagePercentage,
    showUpgradeModal,
    loadPlanFeatures,
    displayUsageStats
};
