let currentPage = 1;

async function loadPacientes(page) {
    const tbody = document.getElementById('pacientesBody');
    if (!tbody) return;
    if (typeof page !== 'number') page = currentPage;
    currentPage = page;

    const params = new URLSearchParams({ page, ordering: '-id' });
    const urlParams = new URLSearchParams(window.location.search);
    for (const key of urlParams.keys()) {
        if (!params.has(key) && ['riesgo', 'sexo', 'fumador', 'hipertenso', 'diabetico', 'imc_clasificacion', 'imc_min', 'imc_max'].includes(key)) {
            params.set(key, urlParams.get(key));
        }
    }
    const search = document.getElementById('searchPaciente')?.value?.trim();
    if (search) params.set('search', search);
    const riesgo = document.getElementById('filterRiesgo')?.value;
    if (riesgo) params.set('riesgo', riesgo);
    const sexo = document.getElementById('filterSexo')?.value;
    if (sexo) params.set('sexo', sexo);
    const imc = document.getElementById('filterIMC')?.value;
    if (imc) params.set('imc_clasificacion', imc);
    const imcMin = document.getElementById('filterIMCMin')?.value;
    if (imcMin) params.set('imc_min', imcMin);
    const imcMax = document.getElementById('filterIMCMax')?.value;
    if (imcMax) params.set('imc_max', imcMax);

    showLoading('pacientesBody');

    try {
        const response = await apiRequest(`/etl/pacientes/?${params}`);
        if (!response.ok) throw new Error('Error al cargar pacientes');
        const data = await response.json();

        if (data.results?.length === 0) {
            tbody.innerHTML = '<tr><td colspan="12" class="text-center text-muted">No se encontraron pacientes</td></tr>';
            return;
        }

        tbody.innerHTML = data.results.map(p => `
            <tr>
                <td>${p.id}</td>
                <td><strong>${p.nombre}</strong></td>
                <td>${p.edad}</td>
                <td>${p.sexo === 'M' ? 'Masculino' : 'Femenino'}</td>
                <td>${p.imc?.toFixed(1) || 'N/A'}</td>
                <td>${p.glucosa?.toFixed(0) || 'N/A'}</td>
                <td>${p.colesterol?.toFixed(0) || 'N/A'}</td>
                <td>${p.presion_sistolica?.toFixed(0) || 'N/A'}</td>
                <td>${p.presion_diastolica?.toFixed(0) || 'N/A'}</td>
                <td>${getBadgeHTML(p.riesgo)}</td>
                <td>${p.fumador ? '<span class="badge bg-danger">Sí</span>' : '<span class="badge bg-secondary">No</span>'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="predictPaciente(${p.id})" title="Predecir riesgo">
                        <i class="bi bi-cpu"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        updatePagination(data.count, page);
    } catch (error) {
        handleApiError(error);
    }
}

function updatePagination(total, page) {
    const pagination = document.getElementById('pacientesPagination');
    if (!pagination) return;

    const totalPages = Math.ceil(total / 25);
    if (totalPages <= 1) { pagination.innerHTML = ''; return; }

    let html = '';
    if (page > 1) {
        html += `<li class="page-item"><button class="page-link" onclick="loadPacientes(${page - 1})">Anterior</button></li>`;
    }
    for (let i = Math.max(1, page - 2); i <= Math.min(totalPages, page + 2); i++) {
        html += `<li class="page-item ${i === page ? 'active' : ''}"><button class="page-link" onclick="loadPacientes(${i})">${i}</button></li>`;
    }
    if (page < totalPages) {
        html += `<li class="page-item"><button class="page-link" onclick="loadPacientes(${page + 1})">Siguiente</button></li>`;
    }
    pagination.innerHTML = html;
}

async function predictPaciente(id) {
    try {
        const response = await apiRequest('/ml/predictions/predict_patient/', {
            method: 'POST',
            body: { paciente_id: id },
        });

        if (response.ok) {
            const data = await response.json();
            const alertClass = {
                BAJO: 'alert-success',
                MEDIO: 'alert-warning',
                ALTO: 'alert-orange',
                CRITICO: 'alert-danger'
            };

            document.getElementById('predictResult').innerHTML = `
                <div class="${alertClass[data.prediccion] || 'alert-info'}">
                    <h5>Predicción: ${data.prediccion}</h5>
                    <p>Probabilidad: ${(data.probabilidad * 100).toFixed(1)}%</p>
                    <hr>
                    ${Object.entries(data.probabilidades || {}).map(([k, v]) =>
                        `<small>${k}: ${(v * 100).toFixed(1)}%</small><br>`
                    ).join('')}
                </div>`;
            new bootstrap.Modal(document.getElementById('predictModal')).show();
        }
    } catch (error) {
        handleApiError(error);
    }
}

async function exportPacientes() {
    window.open('/api/reports/excel/pacientes/', '_blank');
}
