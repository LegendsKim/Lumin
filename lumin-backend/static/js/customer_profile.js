// Customer Profile Page Logic

// State
let customerData = null;
let customerId = null;

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', function () {
    // Get customer ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    customerId = urlParams.get('id') || window.location.pathname.split('/').filter(x => x).pop();

    console.log('Customer profile initialized for ID:', customerId);
    loadCustomer();

    // Setup form listeners
    setupEventListeners();
});

function setupEventListeners() {
    // Image upload handler
    document.getElementById('profileImageInput').addEventListener('change', handleImageUpload);

    // Treatment form submission
    document.getElementById('treatmentForm').addEventListener('submit', handleTreatmentSubmit);

    // Edit customer form submission
    document.getElementById('editForm').addEventListener('submit', handleEditSubmit);

    // Save notes form submission
    document.getElementById('notesForm').addEventListener('submit', handleNotesSubmit);

    // Close modals on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function (e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    });
}

// ========== HELPERS ==========
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

// ========== DATA LOADING ==========
async function loadCustomer() {
    try {
        const response = await fetch(`/api/customers/api/customers/${customerId}/`);
        customerData = await response.json();

        // Update header
        document.getElementById('customerName').textContent = customerData.full_name;
        document.getElementById('customerEmail').textContent = customerData.email || '-';
        document.getElementById('customerPhone').textContent = customerData.phone;
        document.getElementById('customerType').textContent = customerData.customer_type_display || customerData.customer_type;

        // Update statistics
        document.getElementById('totalTreatments').textContent = customerData.treatment_count || 0;
        document.getElementById('treatmentTotal').textContent = Number(customerData.total_treatments || 0).toLocaleString();
        document.getElementById('totalPurchases').textContent = customerData.purchase_count || 0;
        document.getElementById('purchaseTotal').textContent = Number(customerData.total_purchases || 0).toLocaleString();

        // Update notes
        document.getElementById('generalNotes').value = customerData.notes || '';
        document.getElementById('medicalNotes').value = customerData.medical_notes || '';

        // Update profile image if exists
        updateProfileImage();

        // Load related data
        await loadTreatments();
        await loadTreatmentTypes();
        await loadStaffMembers();
    } catch (error) {
        console.error('Error loading customer:', error);
        alert('שגיאה בטעינת נתוני הלקוח');
    }
}

function updateProfileImage() {
    if (customerData && customerData.profile_image_url) {
        const avatar = document.getElementById('customerAvatar');
        avatar.style.background = `url('${customerData.profile_image_url}') center/cover no-repeat`;
        avatar.innerHTML = '<div style="opacity: 0;">👤</div>';
    }
}

async function loadTreatments() {
    try {
        const response = await fetch(`/api/customers/api/treatments/?customer=${customerId}`);
        const data = await response.json();
        const treatments = data.results || data || [];

        const list = document.getElementById('treatmentsList');

        if (treatments.length === 0) {
            list.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">💆</div>
                    <div class="empty-title">אין טיפולים עדיין</div>
                    <div class="empty-text">הוסף את הטיפול הראשון ללקוח זה</div>
                </div>
            `;
        } else {
            list.innerHTML = treatments.map(treatment => `
                <div class="treatment-item">
                    <div class="treatment-info">
                        <h4>${treatment.treatment_type_name}</h4>
                        <div class="treatment-meta">
                            📅 ${new Date(treatment.treatment_date).toLocaleDateString('he-IL')}
                            ${treatment.staff_member_display ? `• 👤 ${treatment.staff_member_display}` : ''}
                        </div>
                        ${treatment.notes ? `<div class="treatment-meta">💬 ${treatment.notes}</div>` : ''}
                    </div>
                    <div class="treatment-price">₪${Number(treatment.price).toLocaleString()}</div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading treatments:', error);
    }
}

async function loadTreatmentTypes() {
    try {
        const response = await fetch('/api/customers/api/treatment-types/');
        const data = await response.json();
        const types = (data.results || data || []).filter(t => t.is_active);

        const select = document.getElementById('treatmentType');
        select.innerHTML = '<option value="">בחר סוג טיפול...</option>' +
            types.map(type => `<option value="${type.id}" data-price="${type.default_price || 0}">${type.name}</option>`).join('');

        // Auto-fill price when treatment type changes
        select.addEventListener('change', function () {
            const selected = this.options[this.selectedIndex];
            if (selected.dataset.price) {
                document.querySelector('[name="price"]').value = selected.dataset.price;
            }
        });
    } catch (error) {
        console.error('Error loading treatment types:', error);
    }
}

async function loadStaffMembers() {
    try {
        const response = await fetch('/api/customers/api/staff-members/');
        const data = await response.json();
        const staff = (data.results || data || []).filter(s => s.is_active);

        const select = document.getElementById('staffMember');
        select.innerHTML = '<option value="">בחר מטפל...</option>' +
            staff.map(member => `<option value="${member.id}">${member.full_name}</option>`).join('');
    } catch (error) {
        console.error('Error loading staff members:', error);
    }
}

// ========== UI ACTIONS ==========
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.closest('.tab-btn').classList.add('active');

    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

function toggleStaffInput() {
    const option = document.querySelector('input[name="staff_option"]:checked').value;
    const staffSelect = document.getElementById('staffMember');
    const newStaffInput = document.getElementById('newStaffName');

    if (option === 'existing') {
        staffSelect.style.display = 'block';
        newStaffInput.style.display = 'none';
        newStaffInput.value = '';
    } else {
        staffSelect.style.display = 'none';
        newStaffInput.style.display = 'block';
        staffSelect.value = '';
    }
}

function toggleTreatmentTypeInput() {
    const option = document.querySelector('input[name="treatment_type_option"]:checked').value;
    const typeSelect = document.getElementById('treatmentType');
    const newTypeInput = document.getElementById('newTreatmentTypeName');

    if (option === 'existing') {
        typeSelect.style.display = 'block';
        newTypeInput.style.display = 'none';
        newTypeInput.value = '';
        typeSelect.required = true;
        newTypeInput.required = false;
    } else {
        typeSelect.style.display = 'none';
        newTypeInput.style.display = 'block';
        typeSelect.value = '';
        typeSelect.required = false;
        newTypeInput.required = true;
    }
}

function openImageUpload(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const input = document.getElementById('profileImageInput');
    setTimeout(() => input.click(), 100);
}

function openAddTreatmentModal() {
    document.getElementById('treatmentModal').classList.add('active');
    document.getElementById('treatmentForm').reset();

    // Reset to "existing" options
    document.querySelector('input[name="staff_option"][value="existing"]').checked = true;
    document.querySelector('input[name="treatment_type_option"][value="existing"]').checked = true;
    toggleStaffInput();
    toggleTreatmentTypeInput();
}

function closeTreatmentModal() {
    document.getElementById('treatmentModal').classList.remove('active');
}

function openEditModal() {
    document.getElementById('editModal').classList.add('active');

    if (customerData) {
        document.getElementById('editFirstName').value = customerData.first_name;
        document.getElementById('editLastName').value = customerData.last_name;
        document.getElementById('editEmail').value = customerData.email || '';
        document.getElementById('editPhone').value = customerData.phone;
        document.getElementById('editCustomerType').value = customerData.customer_type;
    }
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
}

// ========== FORM HANDLERS ==========
async function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('image', file);

    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch(`/api/customers/api/customers/${customerId}/upload_profile_image/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            credentials: 'same-origin',
            body: formData
        });

        if (response.ok) {
            await loadCustomer();
            alert('תמונת הפרופיל עודכנה בהצלחה! ✓');
        } else {
            const error = await response.json();
            alert('שגיאה בהעלאת התמונה: ' + (error.error || JSON.stringify(error)));
        }
    } catch (error) {
        console.error('Error uploading image:', error);
        alert('שגיאה בהעלאת התמונה');
    }

    // Reset input
    e.target.value = '';
}

async function handleTreatmentSubmit(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const staffOption = document.querySelector('input[name="staff_option"]:checked').value;
    const treatmentTypeOption = document.querySelector('input[name="treatment_type_option"]:checked').value;
    const csrftoken = getCookie('csrftoken');

    try {
        let staffMemberId = formData.get('staff_member') || null;
        let treatmentTypeId = formData.get('treatment_type') || null;

        // If creating new treatment type, create it first
        if (treatmentTypeOption === 'new') {
            const newTypeName = formData.get('new_treatment_type_name');
            if (!newTypeName || newTypeName.trim() === '') {
                alert('נא להזין שם טיפול');
                return;
            }

            const typeResponse = await fetch('/api/customers/api/treatment-types/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
                credentials: 'same-origin',
                body: JSON.stringify({ name: newTypeName.trim(), is_active: true })
            });

            if (!typeResponse.ok) {
                const error = await typeResponse.json();
                alert('שגיאה ביצירת סוג טיפול חדש: ' + JSON.stringify(error));
                return;
            }

            const newType = await typeResponse.json();
            treatmentTypeId = newType.id;
            await loadTreatmentTypes();
        }

        // If creating new staff member, create it
        if (staffOption === 'new') {
            const newStaffName = formData.get('new_staff_name');
            if (!newStaffName || newStaffName.trim() === '') {
                alert('נא להזין שם מטפל');
                return;
            }

            const staffResponse = await fetch('/api/customers/api/staff-members/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
                credentials: 'same-origin',
                body: JSON.stringify({ full_name: newStaffName.trim(), is_active: true })
            });

            if (!staffResponse.ok) {
                const error = await staffResponse.json();
                alert('שגיאה ביצירת מטפל חדש: ' + JSON.stringify(error));
                return;
            }

            const newStaff = await staffResponse.json();
            staffMemberId = newStaff.id;
            await loadStaffMembers();
        }

        // Now create the treatment
        const treatmentData = {
            customer: customerId,
            treatment_type: treatmentTypeId,
            treatment_date: formData.get('treatment_date'),
            staff_member: staffMemberId,
            price: formData.get('price'),
            notes: formData.get('notes') || ''
        };

        const response = await fetch('/api/customers/api/treatments/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
            credentials: 'same-origin',
            body: JSON.stringify(treatmentData)
        });

        if (response.ok) {
            closeTreatmentModal();
            await loadCustomer();
            await loadTreatments();
            alert('הטיפול נוסף בהצלחה! ✓');
        } else {
            const error = await response.json();
            alert('שגיאה בהוספת הטיפול: ' + JSON.stringify(error));
        }
    } catch (error) {
        console.error('Error adding treatment:', error);
        alert('שגיאה בהוספת הטיפול');
    }
}

async function handleEditSubmit(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const customerUpdate = {
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        customer_type: formData.get('customer_type')
    };

    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch(`/api/customers/api/customers/${customerId}/`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
            credentials: 'same-origin',
            body: JSON.stringify(customerUpdate)
        });

        if (response.ok) {
            closeEditModal();
            await loadCustomer();
            alert('הלקוח עודכן בהצלחה! ✓');
        } else {
            const error = await response.json();
            alert('שגיאה בעדכון הלקוח: ' + JSON.stringify(error));
        }
    } catch (error) {
        console.error('Error updating customer:', error);
        alert('שגיאה בעדכון הלקוח');
    }
}

async function handleNotesSubmit(e) {
    e.preventDefault();

    const notesData = {
        notes: document.getElementById('generalNotes').value,
        medical_notes: document.getElementById('medicalNotes').value
    };

    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch(`/api/customers/api/customers/${customerId}/`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
            credentials: 'same-origin',
            body: JSON.stringify(notesData)
        });

        if (response.ok) {
            alert('ההערות נשמרו בהצלחה! ✓');
        } else {
            alert('שגיאה בשמירת ההערות');
        }
    } catch (error) {
        console.error('Error saving notes:', error);
        alert('שגיאה בשמירת ההערות');
    }
}

// ========== EXPOSE GLOBALS ==========
window.switchTab = switchTab;
window.toggleStaffInput = toggleStaffInput;
window.toggleTreatmentTypeInput = toggleTreatmentTypeInput;
window.openImageUpload = openImageUpload;
window.openAddTreatmentModal = openAddTreatmentModal;
window.closeTreatmentModal = closeTreatmentModal;
window.openEditModal = openEditModal;
window.closeEditModal = closeEditModal;
