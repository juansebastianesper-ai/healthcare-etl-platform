async function loadModelInfo() {
    const el = document.getElementById('modelInfo');
    if (!el) return;

    try {
        const response = await apiRequest('/ml/models/active/');
        if (response.status === 404) {
            el.innerHTML = '<div class="alert alert-warning">No hay modelo activo. Entrene uno nuevo.</div>';
            return;
        }
        if (!response.ok) throw new Error('Error al cargar modelo');
        const model = await response.json();

        el.innerHTML = `
            <p><strong>Modelo:</strong> ${model.nombre}</p>
            <p><strong>Versión:</strong> ${model.version}</p>
            <p><strong>Accuracy:</strong> ${(model.accuracy * 100).toFixed(2)}%</p>
            <p><strong>Precision:</strong> ${(model.precision * 100).toFixed(2)}%</p>
            <p><strong>Recall:</strong> ${(model.recall * 100).toFixed(2)}%</p>
            <p><strong>F1 Score:</strong> ${(model.f1_score * 100).toFixed(2)}%</p>
            <p><strong>Entrenado:</strong> ${formatDate(model.entrenado_en)}</p>
        `;
    } catch (error) {
        el.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

async function loadPredictionsHistory() {
    const tbody = document.getElementById('predictionsHistoryBody');
    if (!tbody) return;

    try {
        const response = await apiRequest('/ml/predictions/history/');
        if (!response.ok) throw new Error('Error al cargar historial');
        const predictions = await response.json();
        const items = predictions.results || predictions;

        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Sin predicciones aún</td></tr>';
            return;
        }

        tbody.innerHTML = items.map(p => `
            <tr>
                <td>${p.id}</td>
                <td>${p.paciente}</td>
                <td>${getBadgeHTML(p.prediccion)}</td>
                <td>${(p.probabilidad * 100).toFixed(1)}%</td>
                <td>${formatDate(p.fecha)}</td>
            </tr>
        `).join('');
    } catch (error) {
        handleApiError(error);
    }
}

async function makePrediction() {
    const data = {
        edad: parseFloat(document.getElementById('predEdad').value),
        imc: parseFloat(document.getElementById('predIMC').value),
        glucosa: parseFloat(document.getElementById('predGlucosa').value),
        colesterol: parseFloat(document.getElementById('predColesterol').value),
        presion_sistolica: parseFloat(document.getElementById('predPresion').value),
        frecuencia_cardiaca: parseFloat(document.getElementById('predFrecuencia').value),
        fumador: document.getElementById('predFumador').value === 'true',
    };

    try {
        const response = await apiRequest('/ml/predictions/predict/', {
            method: 'POST',
            body: data,
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.message || 'Error al predecir');
        }
        const result = await response.json();

        const alertClass = {
            BAJO: 'alert-success',
            MEDIO: 'alert-warning',
            ALTO: 'alert-warning',
            CRITICO: 'alert-danger'
        };

        const resultDiv = document.getElementById('predictResult');
        resultDiv.classList.remove('d-none');
        resultDiv.innerHTML = `
            <div class="${alertClass[result.prediccion] || 'alert-info'}">
                <h5>Riesgo: ${result.prediccion}</h5>
                <p class="mb-0"><strong>Probabilidad:</strong> ${(result.probabilidad * 100).toFixed(1)}%</p>
                <hr>
                <div class="row">
                    ${Object.entries(result.probabilidades || {}).map(([k, v]) => `
                        <div class="col-3 text-center">
                            <small>${k}</small><br>
                            <strong>${(v * 100).toFixed(1)}%</strong>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        loadPredictionsHistory();
        showToast('Predicción realizada exitosamente', 'success');
    } catch (error) {
        handleApiError(error);
    }
}

async function trainModel() {
    const resultDiv = document.getElementById('trainResult');
    resultDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-warning"></div><p>Entrenando modelo...</p></div>';

    try {
        const response = await apiRequest('/ml/models/train/', { method: 'POST' });
        if (!response.ok) throw new Error('Error al entrenar modelo');
        const data = await response.json();

        resultDiv.innerHTML = `
            <div class="alert alert-success">
                <h6>Modelo entrenado exitosamente v${data.model.version}</h6>
                <hr>
                <div class="row">
                    <div class="col-3"><small>Accuracy</small><br><strong>${(data.metrics.accuracy * 100).toFixed(2)}%</strong></div>
                    <div class="col-3"><small>Precision</small><br><strong>${(data.metrics.precision * 100).toFixed(2)}%</strong></div>
                    <div class="col-3"><small>Recall</small><br><strong>${(data.metrics.recall * 100).toFixed(2)}%</strong></div>
                    <div class="col-3"><small>F1 Score</small><br><strong>${(data.metrics.f1_score * 100).toFixed(2)}%</strong></div>
                </div>
            </div>
        `;

        loadModelInfo();
        showToast('Modelo entrenado exitosamente', 'success');
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        handleApiError(error);
    }
}

async function deletePredictionsHistory() {
    if (!confirm('¿Borrar todo el historial de predicciones?')) return;

    try {
        const response = await apiRequest('/ml/predictions/delete_history/', { method: 'DELETE' });
        if (!response.ok) throw new Error('Error al borrar historial');
        const data = await response.json();
        showToast(data.message, 'success');
        loadPredictionsHistory();
    } catch (error) {
        handleApiError(error);
    }
}
