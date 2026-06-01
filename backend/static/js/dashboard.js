let riesgoChart = null;
let sexoChart = null;
let imcChart = null;
let edadChart = null;

function getEl(id) {
    return document.getElementById(id);
}

function setText(id, value) {
    const el = getEl(id);
    if (el) el.textContent = value;
}

async function refreshDashboard() {
    try {
        const response = await apiRequest('/dashboard/');
        if (!response.ok) {
            setText('lastUpdate', 'Error al cargar dashboard');
            return;
        }
        const data = await response.json();

        updateKPIs(data.kpis);
        updateCharts(data.kpis);
        updateSegmentacionEdad(data.segmentacion_edad);
        updateMLInfo(data.ml);
        updateETLInfo(data.etl);
        setText('lastUpdate', 'Última actualización: ' + new Date().toLocaleTimeString('es-MX'));

    } catch (error) {
        setText('lastUpdate', 'Error: ' + error.message);
    }
}

function updateKPIs(kpis) {
    if (!kpis) return;
    setText('totalPacientes', formatNumber(kpis.total_pacientes));
    setText('pacientesCriticos', formatNumber(kpis.pacientes_criticos));
    setText('riesgoPromedio', (kpis.riesgo_promedio || 0).toFixed(2));
    setText('etlExitosos', formatNumber(kpis.total_pacientes || 0));
}

function updateCharts(kpis) {
    if (!kpis) return;
    const ctxRiesgo = getEl('riesgoChart');
    if (ctxRiesgo) {
        if (riesgoChart) riesgoChart.destroy();
        const labels = Object.keys(kpis.distribucion_riesgo || {});
        const data = Object.values(kpis.distribucion_riesgo || {});
        if (labels.length > 0) {
            riesgoChart = new Chart(ctxRiesgo, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Pacientes',
                        data: data,
                        backgroundColor: ['#198754', '#ffc107', '#fd7e14', '#dc3545'],
                        borderWidth: 0,
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true, grid: { display: false } } }
                }
            });
        }
    }

    const ctxSexo = getEl('sexoChart');
    if (ctxSexo) {
        if (sexoChart) sexoChart.destroy();
        const m = kpis.distribucion_sexo?.M || 0;
        const f = kpis.distribucion_sexo?.F || 0;
        if (m + f > 0) {
            sexoChart = new Chart(ctxSexo, {
                type: 'pie',
                data: {
                    labels: ['Masculino', 'Femenino'],
                    datasets: [{ data: [m, f], backgroundColor: ['#0d6efd', '#dc3545'] }]
                },
                options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
            });
        }
    }

    const ctxIMC = getEl('imcChart');
    if (ctxIMC) {
        if (imcChart) imcChart.destroy();
        const imcLabels = {
            'BAJO_PESO': 'Bajo Peso', 'NORMAL': 'Normal', 'SOBREPESO': 'Sobrepeso',
            'OBESIDAD_I': 'Obesidad I', 'OBESIDAD_II': 'Obesidad II', 'OBESIDAD_III': 'Obesidad III'
        };
        const keys = Object.keys(kpis.distribucion_imc || {});
        if (keys.length > 0) {
            imcChart = new Chart(ctxIMC, {
                type: 'bar',
                data: {
                    labels: keys.map(k => imcLabels[k] || k),
                    datasets: [{
                        label: 'Pacientes',
                        data: Object.values(kpis.distribucion_imc),
                        backgroundColor: '#0dcaf0',
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true } }
                }
            });
        }
    }
}

function updateSegmentacionEdad(segmentacion) {
    const ctxEdad = getEl('edadChart');
    if (!ctxEdad || !segmentacion) return;
    if (edadChart) edadChart.destroy();

    const labels = Object.keys(segmentacion);
    if (labels.length === 0) return;

    edadChart = new Chart(ctxEdad, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total',
                    data: Object.values(segmentacion).map(s => s.total || 0),
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13,110,253,0.1)',
                    fill: true, tension: 0.4,
                },
                {
                    label: 'Críticos',
                    data: Object.values(segmentacion).map(s => s.criticos || 0),
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220,53,69,0.1)',
                    fill: true, tension: 0.4,
                }
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

function updateMLInfo(ml) {
    const el = getEl('mlInfo');
    if (!el || !ml) return;
    if (ml.modelo_activo) {
        el.innerHTML = `
            <p><strong>Modelo:</strong> Random Forest v${ml.modelo_version || '?'}</p>
            <p><strong>Accuracy:</strong> ${ml.modelo_accuracy ? (ml.modelo_accuracy * 100).toFixed(2) + '%' : 'N/A'}</p>
            <p><strong>Predicciones:</strong> ${formatNumber(ml.predicciones_totales || 0)}</p>
        `;
    } else {
        el.innerHTML = '<p class="text-muted">No hay modelo entrenado. Ve a la sección ML para entrenar uno.</p>';
    }
}

function updateETLInfo(etl) {
    const el = getEl('etlInfo');
    if (!el || !etl) return;
    if (etl.ultimo_ejecucion) {
        el.innerHTML = `
            <p><strong>Archivo:</strong> ${etl.ultimo_ejecucion.archivo || 'N/A'}</p>
            <p><strong>Registros:</strong> ${formatNumber(etl.ultimo_ejecucion.registros || 0)}</p>
            <p><strong>Fecha:</strong> ${formatDate(etl.ultimo_ejecucion.fecha)}</p>
            <p><strong>Total ETL:</strong> ${formatNumber(etl.total || 0)} ejecuciones</p>
        `;
    }
}
