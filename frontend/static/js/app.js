// A.I.D.P.S Enhanced Frontend JavaScript - UI Connectors

document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh stats every 30 seconds on dashboard
    if (window.location.pathname === '/dashboard' || window.location.pathname === '/') {
        setInterval(updateStats, 30000);
    }
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize workflow stepper if present
    initWorkflowStepper();
    
    // Initialize bulk actions if checkboxes present
    initBulkActions();
});

// ========== ENHANCED AJAX WITH PROGRESS ==========
function ajaxRequest(url, options = {}) {
    const progressBar = document.getElementById('workflow-progress');
    if (progressBar) progressBar.style.width = '30%';
    
    return fetch(url, {
        method: options.method || 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: options.data ? JSON.stringify(options.data) : null
    })
    .then(response => response.json())
    .then(data => {
        if (progressBar) progressBar.style.width = '100%';
        showNotification(data.message || (data.success ? 'Success!' : 'Completed'), data.success ? 'success' : 'info');
        return data;
    })
    .catch(error => {
        if (progressBar) progressBar.style.width = '0%';
        console.error('AJAX error:', error);
        showNotification('Request failed: ' + error.message, 'danger');
        throw error;
    })
    .finally(() => {
        setTimeout(() => {
            if (progressBar) progressBar.style.width = '0%';
        }, 1500);
    });
}

// ========== WORKFLOW WIZARD ==========
function openWorkflowWizard() {
    const modal = new bootstrap.Modal(document.getElementById('workflowModal'));
    modal.show();
}

function initWorkflowStepper() {
    const steps = document.querySelectorAll('.workflow-step');
    steps.forEach((step, index) => {
        step.addEventListener('click', () => activateStep(index));
    });
}

function activateStep(stepIndex) {
    document.querySelectorAll('.workflow-step').forEach((step, i) => {
        step.classList.toggle('active', i === stepIndex);
        step.classList.toggle('completed', i < stepIndex);
    });
    
    // Execute step action
    const actions = ['scanNetworkPrompt()', 'detectServicesPrompt()', 'provisionPrompt()', 'exportAndAnsible()'];
    if (actions[stepIndex]) eval(actions[stepIndex]);
}

function scanNetworkPrompt() {
    const subnet = prompt('Enter subnet (e.g., 192.168.1.0/24):', '192.168.1.0/24');
    if (subnet) {
        ajaxRequest('/scan', { data: { subnet } })
            .then(() => activateStep(1));
    }
}

function detectServicesPrompt() {
    const ips = prompt('Enter IPs (comma-separated):');
    if (ips) {
        ajaxRequest('/detect', { data: { ips: ips.split(',') } })
            .then(() => activateStep(2));
    }
}

function provisionPrompt() {
    const ips = prompt('Enter IPs to provision (comma-separated):');
    if (ips) {
        ajaxRequest('/bulk_provision', { data: { ips: ips.split(',') } })
            .then(() => activateStep(3));
    }
}

function exportAndAnsible() {
    ajaxRequest('/generate_ansible')
        .then(() => {
            window.open('/export', '_blank');
            activateStep(4);
        });
}

// ========== BULK ACTIONS ==========
function initBulkActions() {
    const bulkBtn = document.getElementById('bulk-actions');
    if (bulkBtn) {
        bulkBtn.addEventListener('click', () => {
            const selectedIps = Array.from(document.querySelectorAll('input[name="device"]:checked')).map(cb => cb.value);
            if (selectedIps.length === 0) {
                showNotification('Select devices first', 'warning');
                return;
            }
            showBulkActionMenu(selectedIps);
        });
    }
}

function showBulkActionMenu(ips) {
    const actions = [
        { label: 'Provision All', action: () => bulkProvision(ips) },
        { label: 'Detect Services', action: () => bulkDetect(ips) },
        { label: 'Export Selected', action: () => bulkExport(ips) }
    ];
    
    const menuHtml = actions.map(a => 
        `<button class="dropdown-item" onclick="${a.action.toString().split('\n')[0]}">${a.label}</button>`
    ).join('');
    
    // Use Bootstrap dropdown or toast menu
    showNotification(`Selected ${ips.length} devices. Actions: ${actions.map(a => a.label).join(', ')}`, 'info');
    // TODO: Proper dropdown modal
}

// Bulk operations
function bulkProvision(ips) {
    ajaxRequest('/bulk_provision', { data: { ips } });
}

function bulkDetect(ips) {
    ajaxRequest('/detect', { data: { ips } });
}

function bulkExport(ips) {
    ajaxRequest('/export_selected', { data: { ips } })
        .then(data => {
            if (data.download_url) window.open(data.download_url, '_blank');
        });
}

function generateAnsible() {
    ajaxRequest('/ansible/inventory');
}

// Existing functions (enhanced)
function scanNetwork(subnet = null) {
    const btn = event?.target;
    toggleLoading(btn, true);
    
    ajaxRequest('/scan', {
        method: 'POST',
        data: subnet ? {subnet} : {}
    }).finally(() => toggleLoading(btn, false));
}

function provisionDevice(ip) {
    if (confirm(`Provision ${ip}?`)) {
        ajaxRequest(`/provision/${ip}`).then(() => location.reload());
    }
}

function updateStats() {
    fetch('/api/stats')
        .then(r => r.json())
        .then(updateStatCards);
}

function toggleLoading(btn, loading) {
    if (!btn) return;
    if (loading) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    } else {
        btn.disabled = false;
        btn.innerHTML = btn.dataset.original || btn.innerHTML;
    }
}

function showNotification(message, type = 'info') {
    // Existing toast logic
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const container = document.getElementById('toast-container') || createToastContainer();
    container.appendChild(toast);
    
    new bootstrap.Toast(toast).show();
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

function filterTable(inputId, tableId) {
    // Existing table filter
    const input = document.getElementById(inputId);
    input?.addEventListener('keyup', function() {
        const filter = input.value.toLowerCase();
        const table = document.getElementById(tableId);
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    });
}

function updateStatCards(stats) {
    // Dynamic stat updates
    document.querySelector('[data-stat="total"]')?.textContent = stats.total;
    // Extend as needed
}
