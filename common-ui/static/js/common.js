// Common JavaScript for All Frontend Services

(function() {
    'use strict';

    // Auto-dismiss alerts after 5 seconds
    function autoDismissAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }

    // Format numbers with thousand separators
    window.formatNumber = function(num) {
        return new Intl.NumberFormat('vi-VN').format(num);
    };

    // Format currency (VND)
    window.formatCurrency = function(amount) {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    };

    // Format date
    window.formatDate = function(dateString, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        };
        return new Date(dateString).toLocaleDateString('vi-VN', { ...defaultOptions, ...options });
    };

    // Format datetime
    window.formatDateTime = function(dateString) {
        return new Date(dateString).toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // Show loading spinner
    window.showLoading = function() {
        const spinner = document.createElement('div');
        spinner.id = 'loading-spinner';
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
        document.body.appendChild(spinner);
    };

    // Hide loading spinner
    window.hideLoading = function() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    };

    // Confirm dialog
    window.confirmAction = function(message = 'Bạn có chắc chắn muốn thực hiện hành động này?') {
        return confirm(message);
    };

    // Toast notification
    window.showToast = function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || createToastContainer();

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    };

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '11';
        document.body.appendChild(container);
        return container;
    }

    // Form validation
    window.validateForm = function(formId) {
        const form = document.getElementById(formId);
        if (!form) return false;

        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return false;
        }
        return true;
    };

    // AJAX request helper
    window.apiRequest = async function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            showToast(error.message, 'danger');
            throw error;
        }
    };

    // Data table search
    window.searchTable = function(inputId, tableId) {
        const input = document.getElementById(inputId);
        const table = document.getElementById(tableId);

        if (!input || !table) return;

        input.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    };

    // Copy to clipboard
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Đã sao chép vào clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
            showToast('Không thể sao chép!', 'danger');
        });
    };

    // Initialize tooltips
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize popovers
    function initPopovers() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Sidebar toggle for mobile and desktop
    function initSidebarToggle() {
        const sidebarMenu = document.getElementById('sidebarMenu');
        const sidebarContent = document.getElementById('sidebarContent');

        if (!sidebarMenu || !sidebarContent) return;

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            const isClickInsideSidebar = sidebarMenu.contains(event.target);
            const isToggleButton = event.target.closest('[data-bs-target="#sidebarContent"]');

            if (!isClickInsideSidebar && !isToggleButton && window.innerWidth < 768) {
                const bsCollapse = bootstrap.Collapse.getInstance(sidebarContent);
                if (bsCollapse && sidebarContent.classList.contains('show')) {
                    bsCollapse.hide();
                }
            }
        });

        // Close sidebar when a link is clicked on mobile
        const sidebarLinks = sidebarMenu.querySelectorAll('.nav-link');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 768) {
                    const bsCollapse = bootstrap.Collapse.getInstance(sidebarContent);
                    if (bsCollapse && sidebarContent.classList.contains('show')) {
                        bsCollapse.hide();
                    }
                }
            });
        });
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        autoDismissAlerts();
        initTooltips();
        initPopovers();
        initSidebarToggle();

        // Add confirm dialogs to delete buttons
        document.querySelectorAll('[data-confirm]').forEach(button => {
            button.addEventListener('click', function(e) {
                const message = this.getAttribute('data-confirm');
                if (!confirmAction(message)) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    });

})();
