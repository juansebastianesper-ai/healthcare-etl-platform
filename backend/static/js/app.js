function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer') || (() => {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999;';
        document.body.appendChild(container);
        return container;
    })();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>`;
    toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

function showLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2 text-muted">Cargando...</p></div>';
}

function handleApiError(error) {
    console.error('API Error:', error);
    showToast(error.message || 'Error en la operación', 'danger');
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function getBadgeHTML(riesgo) {
    const map = { BAJO: 'success', MEDIO: 'warning', ALTO: 'orange', CRITICO: 'danger' };
    return `<span class="badge bg-${map[riesgo] || 'secondary'}">${riesgo}</span>`;
}

function formatNumber(num) {
    return new Intl.NumberFormat('es-MX').format(num || 0);
}

function getRoleBadge(role) {
    const map = { ADMIN: 'danger', MEDICO: 'primary', ANALISTA: 'info' };
    return `<span class="badge bg-${map[role] || 'secondary'}">${role}</span>`;
}
