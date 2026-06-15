async function loadETLHistory() {
    const tbody = document.getElementById('etlHistoryBody');
    if (!tbody) return;

    try {
        const response = await apiRequest('/etl/runs/history/');
        if (!response.ok) throw new Error('Error al cargar historial');
        const runs = await response.json();
        const items = runs.results || runs;

        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No hay ejecuciones ETL</td></tr>';
            updateETLStats(items);
            return;
        }

        const estados = { COMPLETADO: 'success', ERROR: 'danger', PROCESANDO: 'info', PENDIENTE: 'secondary' };
        tbody.innerHTML = items.map(r => `
            <tr>
                <td>${r.id}</td>
                <td>${r.archivo?.split('/').pop() || r.archivo}</td>
                <td>${r.fuente_nombre || 'N/A'}</td>
                <td><span class="badge bg-${estados[r.estado] || 'secondary'}">${r.estado}</span></td>
                <td>${formatNumber(r.registros_procesados)}</td>
                <td>${formatNumber(r.registros_limpios)}</td>
                <td>${formatNumber(r.registros_errores)}</td>
                <td>${formatDate(r.fecha_inicio)}</td>
                <td><button class="btn btn-sm btn-outline-info" onclick="viewETLLog(${r.id})"><i class="bi bi-eye"></i></button></td>
            </tr>
        `).join('');

        updateETLStats(items);
    } catch (error) {
        handleApiError(error);
    }
}

async function loadETLSources() {
    const tbody = document.getElementById('etlSourcesBody');
    if (!tbody) return;

    try {
        const response = await apiRequest('/etl/sources/');
        if (!response.ok) throw new Error('Error al cargar fuentes');
        const sources = await response.json();
        const items = sources.results || sources;

        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No hay fuentes registradas</td></tr>';
            return;
        }

        tbody.innerHTML = items.map(s => `
            <tr>
                <td>${s.id}</td>
                <td>${s.nombre}</td>
                <td><span class="badge bg-info">${s.tipo_archivo}</span></td>
                <td><span class="badge bg-${s.activo ? 'success' : 'secondary'}">${s.activo ? 'Activo' : 'Inactivo'}</span></td>
            </tr>
        `).join('');
    } catch (error) {
        handleApiError(error);
    }
}

function updateETLStats(runs) {
    const total = runs.length;
    const completed = runs.filter(r => r.estado === 'COMPLETADO').length;
    const errors = runs.filter(r => r.estado === 'ERROR').length;
    const records = runs.reduce((sum, r) => sum + (r.registros_limpios || 0), 0);

    document.getElementById('totalRuns').textContent = total;
    document.getElementById('completedRuns').textContent = completed;
    document.getElementById('errorRuns').textContent = errors;
    document.getElementById('totalRecords').textContent = formatNumber(records);
}

async function uploadETL() {
    const file = document.getElementById('etlFile').files[0];
    if (!file) { showToast('Seleccione un archivo', 'warning'); return; }

    const formData = new FormData();
    formData.append('archivo', file);
    formData.append('fuente', document.getElementById('sourceName').value || 'Upload');

    const progress = document.getElementById('uploadProgress');
    const result = document.getElementById('uploadResult');
    progress.classList.remove('d-none');
    result.innerHTML = '';

    try {
        const response = await apiRequest('/etl/runs/upload/', {
            method: 'POST',
            body: formData,
        });

        progress.classList.add('d-none');

        if (response.ok) {
            const data = await response.json();
            result.innerHTML = `
                <div class="alert alert-success">
                    <strong>ETL Completado!</strong><br>
                    Registros: ${formatNumber(data.registros_limpios)}<br>
                    Errores: ${formatNumber(data.registros_errores)}
                </div>`;
            loadETLHistory();
            showToast('ETL ejecutado exitosamente', 'success');
        } else {
            const error = await response.json();
            result.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        }
    } catch (error) {
        progress.classList.add('d-none');
        result.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        handleApiError(error);
    }
}

async function viewETLLog(id) {
    try {
        const response = await apiRequest(`/etl/runs/${id}/log/`);
        if (!response.ok) throw new Error('Error al cargar log');
        const data = await response.json();

        showToast(`Log ETL #${id}: ${data.log?.substring(0, 200)}...`, 'info');
    } catch (error) {
        handleApiError(error);
    }
}

async function deleteAllData() {
    if (!confirm('¿Borrar todos los pacientes, ejecuciones ETL y fuentes?')) return;

    try {
        const response = await apiRequest('/etl/runs/delete_all/', { method: 'DELETE' });
        if (!response.ok) throw new Error('Error al borrar datos');
        const data = await response.json();
        showToast(data.message, 'success');
        loadETLHistory();
        loadETLSources();
    } catch (error) {
        handleApiError(error);
    }
}
