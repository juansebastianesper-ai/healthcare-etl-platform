let segRiesgoChart = null;
let segEdadChart = null;
let segIMCChart = null;

async function loadAnalytics() {
    try {
        const [kpiResp, statsResp, segRiesgoResp, segEdadResp, segIMCResp] = await Promise.all([
            apiRequest('/analytics/kpis/'),
            apiRequest('/analytics/estadisticas/'),
            apiRequest('/analytics/segmentacion/riesgo/'),
            apiRequest('/analytics/segmentacion/edad/'),
            apiRequest('/analytics/segmentacion/imc/'),
        ]);

        const kpis = await kpiResp.json();
        const stats = await statsResp.json();
        const segRiesgo = await segRiesgoResp.json();
        const segEdad = await segEdadResp.json();
        const segIMC = await segIMCResp.json();

        updateKPIValues(kpis);
        updateStatsTable(stats);
        createSegCharts(segRiesgo, segEdad, segIMC);

    } catch (error) {
        handleApiError(error);
    }
}

function updateKPIValues(kpis) {
    document.getElementById('kpiTotal').textContent = formatNumber(kpis.total_pacientes);
    document.getElementById('kpiCriticos').textContent = formatNumber(kpis.pacientes_criticos);
    document.getElementById('kpiHipertensos').textContent = formatNumber(kpis.hipertensos);
    document.getElementById('kpiDiabeticos').textContent = formatNumber(kpis.diabeticos);
    document.getElementById('kpiFumadores').textContent = formatNumber(kpis.fumadores);
    document.getElementById('kpiRiesgoProm').textContent = kpis.riesgo_promedio?.toFixed(2) || '0';
}

function updateStatsTable(stats) {
    const campos = ['edad', 'imc', 'glucosa', 'colesterol', 'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca', 'saturacion_oxigeno'];
    const labels = {
        edad: 'Edad', imc: 'IMC', glucosa: 'Glucosa', colesterol: 'Colesterol',
        presion_sistolica: 'Pres. Sistólica', presion_diastolica: 'Pres. Diastólica',
        frecuencia_cardiaca: 'Frec. Cardíaca', saturacion_oxigeno: 'Sat. Oxígeno'
    };

    const tbody = document.getElementById('statsBody');
    if (!tbody) return;

    tbody.innerHTML = campos.map(c => {
        const s = stats[c];
        return s ? `<tr>
            <td><strong>${labels[c]}</strong></td>
            <td>${s.media?.toFixed(2)}</td>
            <td>${s.mediana?.toFixed(2)}</td>
            <td>${s.moda?.toFixed(2)}</td>
            <td>${s.desviacion_std?.toFixed(2)}</td>
            <td>${s.minimo?.toFixed(2)}</td>
            <td>${s.maximo?.toFixed(2)}</td>
        </tr>` : '';
    }).join('');
}

function createSegCharts(segRiesgo, segEdad, segIMC) {
    const ctx1 = document.getElementById('segRiesgoChart');
    if (ctx1) {
        if (segRiesgoChart) segRiesgoChart.destroy();
        segRiesgoChart = new Chart(ctx1, {
            type: 'doughnut',
            data: {
                labels: Object.keys(segRiesgo),
                datasets: [{
                    data: Object.values(segRiesgo),
                    backgroundColor: ['#198754', '#ffc107', '#fd7e14', '#dc3545'],
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                },
            }
        });
    }

    const ctx2 = document.getElementById('segEdadChart');
    if (ctx2) {
        if (segEdadChart) segEdadChart.destroy();
        segEdadChart = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: Object.keys(segEdad),
                datasets: [{
                    label: 'Pacientes',
                    data: Object.values(segEdad).map(s => s.total),
                    backgroundColor: ['#0d6efd', '#6c757d', '#ffc107', '#fd7e14', '#dc3545'],
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    const ctx3 = document.getElementById('segIMCChart');
    if (ctx3) {
        if (segIMCChart) segIMCChart.destroy();
        const labels = {
            'BAJO_PESO': 'Bajo Peso', 'NORMAL': 'Normal', 'SOBREPESO': 'Sobrepeso',
            'OBESIDAD_I': 'Obesidad I', 'OBESIDAD_II': 'Obesidad II', 'OBESIDAD_III': 'Obesidad III'
        };
        segIMCChart = new Chart(ctx3, {
            type: 'bar',
            data: {
                labels: Object.keys(segIMC).map(k => labels[k] || k),
                datasets: [{
                    label: 'Pacientes',
                    data: Object.values(segIMC),
                    backgroundColor: ['#198754', '#0d6efd', '#ffc107', '#fd7e14', '#dc3545', '#6f42c1'],
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
