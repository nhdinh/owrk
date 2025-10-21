// Asset Frontend JavaScript

// Modal functions
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Form validation
function validateAssetForm() {
    const requiredFields = ['asset_code', 'name', 'category_id', 'purchase_price', 'purchase_date'];
    let isValid = true;

    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field && !field.value) {
            field.style.borderColor = 'red';
            isValid = false;
        } else if (field) {
            field.style.borderColor = '#ddd';
        }
    });

    return isValid;
}

// File upload preview
function handleFileSelect(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('file-preview');

    if (file && preview) {
        const fileSize = (file.size / 1024 / 1024).toFixed(2); // MB
        preview.innerHTML = `
            <p><strong>File:</strong> ${file.name}</p>
            <p><strong>Size:</strong> ${fileSize} MB</p>
            <p><strong>Type:</strong> ${file.type}</p>
        `;
    }
}

// Assignment form
function showAssignmentModal(assetId) {
    document.getElementById('assignment_asset_id').value = assetId;
    showModal('assignmentModal');
}

// Search and filter
function applyFilters() {
    const form = document.getElementById('filterForm');
    if (form) {
        form.submit();
    }
}

// QR Code display
function displayQRCode(qrCodeData) {
    const qrContainer = document.getElementById('qr-code-container');
    if (qrContainer && qrCodeData) {
        qrContainer.innerHTML = `<img src="${qrCodeData}" alt="QR Code" />`;
    }
}

// Status badge color
function getStatusBadgeClass(status) {
    const statusMap = {
        'NEW': 'status-new',
        'AVAILABLE': 'status-available',
        'IN_USE': 'status-in-use',
        'MAINTENANCE': 'status-maintenance',
        'BROKEN': 'status-broken',
        'DISPOSED': 'status-disposed'
    };
    return statusMap[status] || 'status-new';
}

// Confirmation dialog
function confirmDelete(assetId, assetName) {
    return confirm(`Are you sure you want to delete asset "${assetName}"?`);
}

function confirmReturn(assetId) {
    return confirm('Are you sure you want to return this asset?');
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        z-index: 2000;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}
