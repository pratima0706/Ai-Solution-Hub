

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all admin functionality
    initSidebar();
    initThemeToggle();
    initDropdowns();
    initCharts();
    initDataTables();
    initFilters();
    initModals();
    initNotifications();
});

// Sidebar functionality
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
    const sidebar = document.getElementById('adminSidebar');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
        });
    }
    
    if (mobileSidebarToggle) {
        mobileSidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 1024) {
            if (!sidebar.contains(e.target) && !mobileSidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        }
    });
}

// Theme toggle functionality
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    
    // Load saved theme
    const savedTheme = localStorage.getItem('admin-theme') || 'light';
    body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('admin-theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }
}

// Dropdown functionality
function initDropdowns() {
    const userDropdown = document.getElementById('userDropdown');
    const userDropdownMenu = document.getElementById('userDropdownMenu');
    
    if (userDropdown && userDropdownMenu) {
        userDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdownMenu.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            userDropdownMenu.classList.remove('show');
        });
    }
}

// Chart initialization
function initCharts() {
    // Initialize any charts on the page
    const chartElements = document.querySelectorAll('[data-chart]');
    chartElements.forEach(function(element) {
        const chartType = element.getAttribute('data-chart');
        const chartData = JSON.parse(element.getAttribute('data-chart-data') || '{}');
        createChart(element, chartType, chartData);
    });
}

function createChart(canvas, type, data) {
    const ctx = canvas.getContext('2d');
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 20
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                }
            },
            y: {
                grid: {
                    color: '#e2e8f0'
                }
            }
        }
    };
    
    const chartConfig = {
        type: type,
        data: data,
        options: defaultOptions
    };
    
    return new Chart(ctx, chartConfig);
}

// Data tables functionality
function initDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(function(table) {
        // Add sorting functionality
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function(header) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, header);
            });
        });
    });
}

function sortTable(table, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const isAscending = header.classList.contains('sort-asc');
    
    // Remove existing sort classes
    header.parentNode.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Add appropriate sort class
    header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
    
    // Sort rows
    rows.sort(function(a, b) {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();
        
        if (isAscending) {
            return bValue.localeCompare(aValue);
        } else {
            return aValue.localeCompare(bValue);
        }
    });
    
    // Reorder rows in table
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}

// Filter functionality
function initFilters() {
    const filterForms = document.querySelectorAll('.filter-form');
    
    filterForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            applyFilters(form);
        });
        
        // Auto-apply filters on change
        const filterInputs = form.querySelectorAll('input, select');
        filterInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                applyFilters(form);
            });
        });
    });
}

function applyFilters(form) {
    const formData = new FormData(form);
    const params = new URLSearchParams();
    
    for (let [key, value] of formData.entries()) {
        if (value) {
            params.append(key, value);
        }
    }
    
    const url = new URL(window.location);
    url.search = params.toString();
    window.location.href = url.toString();
}

// Modal functionality
function initModals() {
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    
    modalTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = trigger.getAttribute('data-modal-target');
            const modal = document.getElementById(modalId);
            
            if (modal) {
                showModal(modal);
            }
        });
    });
    
    // Close modal on backdrop click
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-backdrop')) {
            closeModal(e.target);
        }
    });
    
    // Close modal on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });
}

function showModal(modal) {
    modal.classList.add('show');
    document.body.classList.add('modal-open');
    
    // Focus first input
    const firstInput = modal.querySelector('input, textarea, select');
    if (firstInput) {
        firstInput.focus();
    }
}

function closeModal(modal) {
    modal.classList.remove('show');
    document.body.classList.remove('modal-open');
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.alert-container') || createAlertContainer();
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container';
    const content = document.querySelector('.admin-content');
    if (content) {
        content.insertBefore(container, content.firstChild);
    }
    return container;
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Copied to clipboard!', 'success');
    }).catch(function() {
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Export functionality
function exportToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const csvContent = [];
    
    rows.forEach(function(row) {
        const cells = row.querySelectorAll('th, td');
        const rowData = Array.from(cells).map(cell => {
            return '"' + cell.textContent.replace(/"/g, '""') + '"';
        });
        csvContent.push(rowData.join(','));
    });
    
    const blob = new Blob([csvContent.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Search functionality
function initSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.dashboard-card').querySelector('.data-table');
            
            if (table) {
                filterTable(table, searchTerm);
            }
        });
    });
}

function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(function(row) {
        const text = row.textContent.toLowerCase();
        const shouldShow = text.includes(searchTerm);
        row.style.display = shouldShow ? '' : 'none';
    });
}

// Pagination
function initPagination() {
    const paginationLinks = document.querySelectorAll('.page-btn');
    
    paginationLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            if (page) {
                loadPage(page);
            }
        });
    });
}

function loadPage(page) {
    const url = new URL(window.location);
    url.searchParams.set('page', page);
    window.location.href = url.toString();
}

// Initialize search and pagination
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
    initPagination();
});

// Chart helper functions
function createLineChart(canvas, data, options = {}) {
    const defaultData = {
        labels: data.labels || [],
        datasets: [{
            label: data.label || 'Data',
            data: data.values || [],
            borderColor: options.color || '#6366f1',
            backgroundColor: options.backgroundColor || 'rgba(99, 102, 241, 0.1)',
            tension: 0.4,
            fill: true
        }]
    };
    
    return createChart(canvas, 'line', defaultData);
}

function createBarChart(canvas, data, options = {}) {
    const defaultData = {
        labels: data.labels || [],
        datasets: [{
            label: data.label || 'Data',
            data: data.values || [],
            backgroundColor: options.backgroundColor || '#6366f1',
            borderColor: options.borderColor || '#6366f1',
            borderWidth: 1
        }]
    };
    
    return createChart(canvas, 'bar', defaultData);
}

function createDoughnutChart(canvas, data, options = {}) {
    const defaultData = {
        labels: data.labels || [],
        datasets: [{
            data: data.values || [],
            backgroundColor: options.colors || [
                '#6366f1',
                '#10b981',
                '#f59e0b',
                '#ef4444',
                '#8b5cf6'
            ],
            borderWidth: 0
        }]
    };
    
    return createChart(canvas, 'doughnut', defaultData);
}

// Progress circle animation
function animateProgressCircle(circle, percentage) {
    const progress = circle.querySelector('.progress-text');
    const circumference = 2 * Math.PI * 30; // radius = 30
    const offset = circumference - (percentage / 100) * circumference;
    
    circle.style.background = `conic-gradient(#6366f1 0deg, #6366f1 ${percentage * 3.6}deg, #e2e8f0 ${percentage * 3.6}deg)`;
    
    if (progress) {
        progress.textContent = percentage + '%';
    }
}

// Initialize progress circles
document.addEventListener('DOMContentLoaded', function() {
    const progressCircles = document.querySelectorAll('.progress-circle');
    progressCircles.forEach(function(circle) {
        const percentage = parseInt(circle.getAttribute('data-percentage') || '0');
        animateProgressCircle(circle, percentage);
    });
});

// Notification functionality
function initNotifications() {
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationMenu = document.getElementById('notificationMenu');
    const notificationBadge = document.getElementById('notificationBadge');
    const notificationList = document.getElementById('notificationList');
    const notificationCount = document.getElementById('notificationCount');
    
    if (!notificationBtn || !notificationMenu) return;
    
    // Toggle notification dropdown
    notificationBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        notificationMenu.classList.toggle('show');
        // Load notifications when opened
        if (notificationMenu.classList.contains('show')) {
            loadNotifications();
        }
    });
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!notificationBtn.contains(e.target) && !notificationMenu.contains(e.target)) {
            notificationMenu.classList.remove('show');
        }
    });
    // Load initial notification count
    loadNotificationCount();
    // Set up real-time updates (every 30 seconds)
    setInterval(function() {
        loadNotificationCount();
        if (notificationMenu.classList.contains('show')) {
            loadNotifications();
        }
    }, 30000);
}
function loadNotificationCount() {
    fetch('/admin/notifications/count/')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('notificationBadge');
            const count = document.getElementById('notificationCount');
            if (badge) {
                badge.textContent = data.count || 0;
                badge.style.display = data.count > 0 ? 'inline' : 'none';
            }
            if (count) {
                count.textContent = data.count || 0;
                count.style.display = data.count > 0 ? 'inline-block' : 'none';
            }
        })
        .catch(error => {
            // ignore
        });
}
function loadNotifications() {
    fetch('/admin/notifications/list/')
        .then(response => response.json())
        .then(data => {
            const notificationList = document.getElementById('notificationList');
            if (!notificationList) return;
            if (data.items && data.items.length > 0) {
                notificationList.innerHTML = data.items.map(item => `
                    <div class="notification-item" data-type="${item.type}">
                        ${item.avatar ? `<img src="${item.avatar}" class="notification-avatar" alt="avatar">` : `<div class="notification-avatar"><i class="fas fa-user"></i></div>`}
                        <div class="notification-content">
                            <div class="notification-text">${item.text}</div>
                            <div class="notification-time">${item.time}</div>
                        </div>
                    </div>
                `).join('');
            } else {
                notificationList.innerHTML = `
                    <div class="notification-item" style="text-align:center; color:var(--text-secondary);">
                        <div class="notification-content">
                            <div class="notification-text">No new notifications</div>
                        </div>
                    </div>
                `;
            }
        })
        .catch(error => {
            const notificationList = document.getElementById('notificationList');
            if (notificationList) {
                notificationList.innerHTML = `
                    <div class="notification-item" style="text-align:center; color:var(--text-secondary);">
                        <div class="notification-content">
                            <div class="notification-text">Error loading notifications</div>
                        </div>
                    </div>
                `;
            }
        });
}

function markAllAsRead() {
    // This would typically make an API call to mark all notifications as read
    // For now, we'll just hide the badge
    const badge = document.getElementById('notificationBadge');
    if (badge) {
        badge.style.display = 'none';
        badge.textContent = '0';
    }
    
    // Show success message
    showNotification('All notifications marked as read', 'success');
}
