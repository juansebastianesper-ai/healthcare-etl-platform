async function loadAnalytics() {
    try {
        const [kpiResp, statsResp] = await Promise.all([
            apiRequest('/analytics/kpis/'),
            apiRequest('/analytics/estadisticas/'),
        ]);

        const kpis = await kpiResp.json();
        const stats = await statsResp.json();

        updateKPIValues(kpis);
        updateStatsTable(stats);

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


