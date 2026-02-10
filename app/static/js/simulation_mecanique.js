// ============================================================
// SIMULATION MÉCANIQUE
// Chute libre, Plan incliné, Trajectoires
// Assistant ALPHA
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState, simMode;

simState = {
    h: 50,
    m: 10,
    g: 9.81,
    angle: 30,
    v0: 20,
    mu: 0.1
};

simMode = 'chute'; // 'chute', 'plan', 'trajectoire'

function initChart() {
    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Position z (m)',
                    data: [],
                    borderColor: '#e74c3c',
                    borderWidth: 3,
                    pointRadius: 0
                },
                {
                    label: 'Vitesse v (m/s)',
                    data: [],
                    borderColor: '#3498db',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: 'Temps (s)' } },
                y: { title: { display: true, text: 'Valeur' } }
            }
        }
    });
}

function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-12 mb-3">
            <label class="form-label"><strong>Mode de simulation</strong></label>
            <select id="mode" class="form-select" onchange="changeMode()">
                <option value="chute">🍎 Chute libre</option>
                <option value="plan">📐 Plan incliné</option>
                <option value="trajectoire">🎯 Trajectoire parabolique</option>
            </select>
        </div>
        <div id="dynamic-controls"></div>
        <div class="col-12">
            <button class="btn btn-success w-100" onclick="lancerSimulation()">
                <i class="fas fa-play"></i> Lancer la simulation
            </button>
        </div>
    `;

    changeMode();
}

function changeMode() {
    simMode = document.getElementById('mode').value;
    const dynControls = document.getElementById('dynamic-controls');

    if (simMode === 'chute') {
        dynControls.innerHTML = `
            <div class="col-md-4">
                <label class="form-label"><strong>Hauteur (m)</strong></label>
                <input type="range" class="form-range" id="hauteur" min="5" max="200" value="50" step="5">
                <div class="text-center"><span id="val-h" class="badge bg-danger">50 m</span></div>
            </div>
            <div class="col-md-4">
                <label class="form-label"><strong>Masse (kg)</strong></label>
                <input type="range" class="form-range" id="masse" min="1" max="100" value="10" step="1">
                <div class="text-center"><span id="val-m" class="badge bg-primary">10 kg</span></div>
            </div>
            <div class="col-md-4">
                <label class="form-label"><strong>Gravité (m/s²)</strong></label>
                <select id="gravite" class="form-select">
                    <option value="9.81">Terre (9.81)</option>
                    <option value="1.62">Lune (1.62)</option>
                    <option value="3.71">Mars (3.71)</option>
                    <option value="24.79">Jupiter (24.79)</option>
                </select>
            </div>
        `;
    } else if (simMode === 'plan') {
        dynControls.innerHTML = `
            <div class="col-md-4">
                <label class="form-label"><strong>Angle (°)</strong></label>
                <input type="range" class="form-range" id="angle" min="10" max="80" value="30" step="5">
                <div class="text-center"><span id="val-angle" class="badge bg-warning">30°</span></div>
            </div>
            <div class="col-md-4">
                <label class="form-label"><strong>Masse (kg)</strong></label>
                <input type="range" class="form-range" id="masse" min="1" max="50" value="10">
                <div class="text-center"><span id="val-m" class="badge bg-primary">10 kg</span></div>
            </div>
            <div class="col-md-4">
                <label class="form-label"><strong>Frottement μ</strong></label>
                <input type="range" class="form-range" id="mu" min="0" max="0.5" value="0.1" step="0.05">
                <div class="text-center"><span id="val-mu" class="badge bg-secondary">0.1</span></div>
            </div>
        `;
    } else {
        dynControls.innerHTML = `
            <div class="col-md-6">
                <label class="form-label"><strong>Vitesse initiale (m/s)</strong></label>
                <input type="range" class="form-range" id="v0" min="5" max="50" value="20" step="1">
                <div class="text-center"><span id="val-v0" class="badge bg-success">20 m/s</span></div>
            </div>
            <div class="col-md-6">
                <label class="form-label"><strong>Angle de tir (°)</strong></label>
                <input type="range" class="form-range" id="angle" min="10" max="80" value="45" step="5">
                <div class="text-center"><span id="val-angle" class="badge bg-info">45°</span></div>
            </div>
        `;
    }
}

function lancerSimulation() {
    if (simMode === 'chute') simulerChute();
    else if (simMode === 'plan') simulerPlan();
    else simulerTrajectoire();
}

function simulerChute() {
    simState.h = parseFloat(document.getElementById('hauteur').value);
    simState.m = parseFloat(document.getElementById('masse').value);
    simState.g = parseFloat(document.getElementById('gravite').value);

    const tMax = Math.sqrt(2 * simState.h / simState.g);
    const dt = tMax / 50;

    const labels = [], dataZ = [], dataV = [];

    for (let t = 0; t <= tMax; t += dt) {
        const z = simState.h - 0.5 * simState.g * t * t;
        const v = simState.g * t;

        labels.push(t.toFixed(2));
        dataZ.push(Math.max(0, z));
        dataV.push(v);
    }

    scopeChart.data.labels = labels;
    scopeChart.data.datasets[0].data = dataZ;
    scopeChart.data.datasets[0].label = 'Altitude z (m)';
    scopeChart.data.datasets[1].data = dataV;
    scopeChart.data.datasets[1].label = 'Vitesse v (m/s)';
    scopeChart.update();
}

function simulerPlan() {
    simState.angle = parseFloat(document.getElementById('angle').value) * Math.PI / 180;
    simState.m = parseFloat(document.getElementById('masse').value);
    simState.mu = parseFloat(document.getElementById('mu').value);

    const a = simState.g * (Math.sin(simState.angle) - simState.mu * Math.cos(simState.angle));
    const tMax = 5;
    const dt = 0.1;

    const labels = [], dataX = [], dataV = [];

    for (let t = 0; t <= tMax; t += dt) {
        const x = 0.5 * a * t * t;
        const v = a * t;

        labels.push(t.toFixed(1));
        dataX.push(x);
        dataV.push(v);
    }

    scopeChart.data.labels = labels;
    scopeChart.data.datasets[0].data = dataX;
    scopeChart.data.datasets[0].label = 'Position x (m)';
    scopeChart.data.datasets[1].data = dataV;
    scopeChart.data.datasets[1].label = 'Vitesse (m/s)';
    scopeChart.update();
}

function simulerTrajectoire() {
    simState.v0 = parseFloat(document.getElementById('v0').value);
    simState.angle = parseFloat(document.getElementById('angle').value) * Math.PI / 180;

    const vx = simState.v0 * Math.cos(simState.angle);
    const vy = simState.v0 * Math.sin(simState.angle);

    const tMax = 2 * vy / simState.g;
    const dt = tMax / 50;

    const labels = [], dataY = [], dataX = [];

    for (let t = 0; t <= tMax; t += dt) {
        const x = vx * t;
        const y = vy * t - 0.5 * simState.g * t * t;

        labels.push(x.toFixed(1));
        dataY.push(Math.max(0, y));
        dataX.push(t);
    }

    scopeChart.data.labels = labels;
    scopeChart.data.datasets[0].data = dataY;
    scopeChart.data.datasets[0].label = 'Hauteur y (m)';
    scopeChart.data.datasets[1].data = [];
    scopeChart.options.scales.x.title.text = 'Distance x (m)';
    scopeChart.update();
}

function getParametresActuels() {
    if (simMode === 'chute') {
        return { h: simState.h, m: simState.m, g: simState.g };
    } else if (simMode === 'plan') {
        return { angle: simState.angle * 180 / Math.PI, m: simState.m, mu: simState.mu };
    } else {
        return { v0: simState.v0, angle: simState.angle * 180 / Math.PI };
    }
}

function getResultatsActuels() {
    if (simMode === 'chute') {
        const tChute = Math.sqrt(2 * simState.h / simState.g);
        const vFinale = simState.g * tChute;
        return { temps_chute_s: tChute.toFixed(2), vitesse_finale_ms: vFinale.toFixed(2) };
    }
    return {};
}

initChart();
generateControls();