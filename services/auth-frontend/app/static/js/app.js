/**
 * Asset Management System - Main JavaScript
 * Handles common functionality across the application
 */

(function() {
    'use strict';

    // ============================================
    // Initialize on DOM ready
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    /**
     * Main initialization function
     */
    function initializeApp() {
        initializeTooltips();
        initializePopovers();
        initializeAlerts();
        initializeFormValidation();
        initializeSidebar();
        initializeClipboard();
        console.log('Asset Management System initialized');
    }

    // ============================================
    // Bootstrap Components Initialization
    // ============================================

    /**
     * Initialize Bootstrap tooltips
     */
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    /**
     * Initialize Bootstrap popovers
     */
    function initializePopovers() {
        const popoverTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="popover"]')
        );
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // ============================================
    // Alert Management
    // ============================================

    /**
     * Auto-dismiss alerts after 5 seconds
     */
    function initializeAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }

    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type of toast (success, danger, warning, info)
     */
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || createToastContainer();

        const toastHTML = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }

    /**
     * Create toast container if it doesn't exist
     */
    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    // ============================================
    // Form Validation
    // ============================================

    /**
     * Initialize Bootstrap form validation
     */
    function initializeFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');

        Array.from(forms).forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }

    // ============================================
    // Sidebar Management
    // ============================================

    /**
     * Initialize sidebar toggle functionality
     */
    function initializeSidebar() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', function() {
                document.getElementById('sidebarMenu').classList.toggle('show');
            });
        }
    }

    // ============================================
    // Clipboard functionality
    // ============================================

    /**
     * Initialize clipboard copy functionality
     */
    function initializeClipboard() {
        document.addEventListener('click', (e) => {
            const el = e.target;
            if (el.matches('[data-copy]')) {
                const text = el.getAttribute('data-copy');
                if (text) {
                    navigator.clipboard.writeText(text).then(() => {
                        showToast('Đã sao chép vào clipboard!', 'success');
                    });
                }
            }
        });
    }

    // ============================================
    // Loading Overlay
    // ============================================

    /**
     * Show loading overlay
     * @param {string} message - Optional loading message
     */
    function showLoading(message = 'Đang tải...') {
        let overlay = document.getElementById('loadingOverlay');

        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.className = 'spinner-overlay';
            overlay.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-light" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div class="text-light mt-3">${message}</div>
                </div>
            `;
            document.body.appendChild(overlay);
        }

        overlay.style.display = 'flex';
    }

    /**
     * Hide loading overlay
     */
    function hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    // ============================================
    // API Helper Functions
    // ============================================

    /**
     * Make an API request
     * @param {string} url - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise} - Fetch promise
     */
    async function apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const mergedOptions = { ...defaultOptions, ...options };

        try {
            showLoading();
            const response = await fetch(url, mergedOptions);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            hideLoading();
            return data;
        } catch (error) {
            hideLoading();
            console.error('API request failed:', error);
            showToast('Có lỗi xảy ra. Vui lòng thử lại.', 'danger');
            throw error;
        }
    }

    // ============================================
    // Utility Functions
    // ============================================

    /**
     * Format date to Vietnamese locale
     * @param {string|Date} date - Date to format
     * @returns {string} - Formatted date
     */
    function formatDate(date) {
        return new Date(date).toLocaleDateString('vi-VN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    }

    /**
     * Format currency to VND
     * @param {number} amount - Amount to format
     * @returns {string} - Formatted currency
     */
    function formatCurrency(amount) {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND',
        }).format(amount);
    }

    /**
     * Debounce function to limit function calls
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} - Debounced function
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Confirm action with user
     * @param {string} message - Confirmation message
     * @returns {boolean} - User confirmation
     */
    function confirmAction(message) {
        return confirm(message);
    }

    // ============================================
    // Export functions to global scope
    // ============================================
    window.AssetManagement = {
        showToast,
        showLoading,
        hideLoading,
        apiRequest,
        formatDate,
        formatCurrency,
        debounce,
        confirmAction,
    };

})();
