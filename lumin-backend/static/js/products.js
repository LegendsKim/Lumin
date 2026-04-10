// Products Page Logic

// State
let allProducts = [];
let currentView = 'grid';

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', function () {
    console.log('Product page initialized (External JS)');
    fetchProducts();

    // Setup event listeners
    setupEventListeners();
});

function setupEventListeners() {
    // Search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            const query = e.target.value.toLowerCase();
            const filtered = allProducts.filter(p =>
                p.name.toLowerCase().includes(query) ||
                p.sku.toLowerCase().includes(query) ||
                (p.barcode && p.barcode.toLowerCase().includes(query))
            );
            renderProducts(filtered);
        });
    }

    // Filter
    const stockFilter = document.getElementById('stockFilter');
    if (stockFilter) {
        stockFilter.addEventListener('change', function (e) {
            const status = e.target.value;
            if (status === '') {
                renderProducts(allProducts);
            } else {
                const filtered = allProducts.filter(p => p.stock_status === status);
                renderProducts(filtered);
            }
        });
    }

    // Modal Close (Click outside)
    const productModal = document.getElementById('productModal');
    if (productModal) {
        productModal.addEventListener('click', function (e) {
            if (e.target === this) {
                closeProductModal();
            }
        });
    }

    // Form Submit
    const productForm = document.getElementById('productForm');
    if (productForm) {
        productForm.addEventListener('submit', handleProductSubmit);
    }
}

// ========== DATA FETCHING ==========
async function fetchProducts() {
    try {
        console.log('Fetching products...');
        const response = await fetch('/api/products/data/products/');

        if (!response.ok) {
            throw new Error(`HTTP Status: ${response.status}`);
        }

        const data = await response.json();
        allProducts = data.results || data || [];

        // Hide loading
        const loadingState = document.getElementById('loadingState');
        if (loadingState) loadingState.style.display = 'none';

        if (allProducts.length === 0) {
            const emptyState = document.getElementById('emptyState');
            if (emptyState) emptyState.style.display = 'block';
        } else {
            renderProducts(allProducts);
        }
    } catch (error) {
        console.error('Error fetching products:', error);

        const loadingState = document.getElementById('loadingState');
        if (loadingState) loadingState.style.display = 'none';

        // Show detailed error
        const emptyState = document.getElementById('emptyState');
        if (emptyState) {
            emptyState.style.display = 'block';
            emptyState.innerHTML = `
                <div class="empty-icon">⚠️</div>
                <div class="empty-title">שגיאה בטעינת מוצרים</div>
                <div class="empty-text">${error.message}</div>
                <button class="primary-btn" onclick="location.reload()">
                    <span>🔄</span>
                    <span>נסה שוב</span>
                </button>
            `;
        }
    }
}

// ========== RENDERING ==========
function renderProducts(products) {
    if (currentView === 'grid') {
        renderGrid(products);
    } else {
        renderTable(products);
    }
}

function renderGrid(products) {
    const grid = document.getElementById('productsGrid');
    const table = document.getElementById('productsTable');

    if (!grid || !table) return;

    grid.style.display = 'grid';
    table.classList.remove('active');

    if (products.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748B;">לא נמצאו מוצרים תואמים לחיפוש</div>';
        return;
    }

    grid.innerHTML = products.map((product, index) => `
        <div class="product-card" style="animation-delay: ${index * 0.05}s;">
            <div class="product-image">
                ${product.image ? `<img src="${product.image}" alt="${product.name}">` : '📦'}
                <span class="stock-badge ${product.stock_status}">${getStockText(product.stock_status)}</span>
            </div>
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-sku">SKU: ${product.sku}</div>
                <div class="product-price">₪${product.price}</div>
                <div class="product-meta">
                    <div class="product-stock">
                        <strong>${product.stock_quantity}</strong> ${product.unit || 'יח\''}
                    </div>
                    <div class="product-actions">
                        <button class="action-btn edit" onclick="editProduct('${product.id}')">✏️</button>
                        <button class="action-btn delete" onclick="deleteProduct('${product.id}')">🗑️</button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function renderTable(products) {
    const grid = document.getElementById('productsGrid');
    const table = document.getElementById('productsTable');
    const tbody = document.getElementById('productsTableBody');

    if (!grid || !table || !tbody) return;

    grid.style.display = 'none';
    table.classList.add('active');

    if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px; color: #64748B;">לא נמצאו מוצרים תואמים לחיפוש</td></tr>';
        return;
    }

    tbody.innerHTML = products.map(product => `
        <tr>
            <td>
                ${product.image ? `<img src="${product.image}" style="width: 48px; height: 48px; object-fit: cover; border-radius: 8px;">` : '📦'}
            </td>
            <td><strong>${product.name}</strong></td>
            <td>${product.sku}</td>
            <td>${product.category_name || '-'}</td>
            <td><strong>₪${product.price}</strong></td>
            <td>${product.stock_quantity} ${product.unit || 'יח\''}</td>
            <td><span class="stock-badge ${product.stock_status}">${getStockText(product.stock_status)}</span></td>
            <td>
                <div class="product-actions">
                    <button class="action-btn edit" onclick="editProduct('${product.id}')">✏️</button>
                    <button class="action-btn delete" onclick="deleteProduct('${product.id}')">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function getStockText(status) {
    const texts = {
        'good': 'מלאי תקין',
        'medium': 'מלאי בינוני',
        'low': 'מלאי נמוך',
        'out': 'אזל מהמלאי'
    };
    return texts[status] || 'לא ידוע';
}

// ========== ACTIONS ==========
function openAddProductModal() {
    const modal = document.getElementById('productModal');
    const form = document.getElementById('productForm');
    const title = document.getElementById('modalTitle');
    const idInput = document.getElementById('productId');

    if (!modal || !form || !title || !idInput) return;

    title.textContent = 'הוסף מוצר חדש';
    form.reset();
    idInput.value = '';
    modal.classList.add('active');
}

function closeProductModal() {
    const modal = document.getElementById('productModal');
    if (modal) modal.classList.remove('active');
}

function editProduct(id) {
    const product = allProducts.find(p => String(p.id) === String(id));
    if (!product) return;

    document.getElementById('modalTitle').textContent = 'ערוך מוצר';
    document.getElementById('productId').value = product.id;
    document.getElementById('productName').value = product.name;
    document.getElementById('productSku').value = product.sku;
    document.getElementById('productBarcode').value = product.barcode || '';
    document.getElementById('productPrice').value = product.price;
    document.getElementById('productCost').value = product.cost || '';
    document.getElementById('productStock').value = product.stock_quantity;
    document.getElementById('productMinStock').value = product.min_stock_level;
    document.getElementById('productDescription').value = product.description || '';

    document.getElementById('productModal').classList.add('active');
}

async function handleProductSubmit(e) {
    e.preventDefault();

    const id = document.getElementById('productId').value;
    const isEdit = !!id;

    const data = {
        name: document.getElementById('productName').value,
        sku: document.getElementById('productSku').value,
        barcode: document.getElementById('productBarcode').value,
        price: document.getElementById('productPrice').value,
        cost: document.getElementById('productCost').value || 0,
        stock_quantity: document.getElementById('productStock').value,
        min_stock_level: document.getElementById('productMinStock').value,
        description: document.getElementById('productDescription').value,
        is_active: true
    };

    try {
        const url = isEdit ? `/api/products/data/products/${id}/` : '/api/products/data/products/';
        const method = isEdit ? 'PATCH' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            closeProductModal();
            fetchProducts();
            showNotification(isEdit ? 'המוצר עודכן בהצלחה' : 'המוצר נוצר בהצלחה', 'success');
        } else {
            const error = await response.json();
            alert('שגיאה בשמירה: ' + (error.detail || JSON.stringify(error)));
        }
    } catch (error) {
        console.error('Error saving product:', error);
        alert('שגיאה בשמירת המוצר');
    }
}

async function deleteProduct(id) {
    if (confirm('האם אתה בטוח שברצונך למחוק מוצר זה?')) {
        try {
            const response = await fetch(`/api/products/data/products/${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            if (response.ok) {
                fetchProducts();
                showNotification('המוצר נמחק בהצלחה', 'success');
            } else {
                alert('שגיאה במחיקת המוצר');
            }
        } catch (error) {
            console.error('Error deleting product:', error);
            alert('שגיאה במחיקת המוצר');
        }
    }
}

// ========== HELPERS ==========
function switchView(view) {
    currentView = view;
    document.querySelectorAll('.view-toggle-btn').forEach(btn => btn.classList.remove('active'));

    // Find button for this view and activate it
    const activeBtn = Array.from(document.querySelectorAll('.view-toggle-btn'))
        .find(btn => btn.onclick.toString().includes(view));
    if (activeBtn) activeBtn.classList.add('active');

    renderProducts(allProducts);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.textContent = message;
    alertDiv.style.cssText = `
        position: fixed; 
        bottom: 20px; 
        right: 20px; 
        background: ${type === 'success' ? '#10B981' : '#EF4444'}; 
        color: white; 
        padding: 12px 24px; 
        border-radius: 8px; 
        animation: fadeInUp 0.3s ease; 
        z-index: 3000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        alertDiv.style.transform = 'translateY(10px)';
        alertDiv.style.transition = 'all 0.3s ease';
        setTimeout(() => alertDiv.remove(), 300);
    }, 3000);
}

// Expose functions globally for HTML onclick handlers
window.switchView = switchView;
window.openAddProductModal = openAddProductModal;
window.closeProductModal = closeProductModal;
window.editProduct = editProduct;
window.deleteProduct = deleteProduct;
