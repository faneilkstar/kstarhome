// ============================================================
// SIMULATION THERMODYNAMIQUE
// Cycle de Carnot, Échangeurs de chaleur
// Assistant ALPHA / ETA
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState;

simState = {
    T_chaude: 500,   // Kelvin
    T_froide: 300,
    Q_in: 1000,      // Joules
    type: 'carnot'
};

function initChart() {
    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Pression (kPa)',
                    data: [],
                    borderColor: '#e74c3c',
                    borderWidth: 3,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: 'Volume (m³)' } },
                y: { title: { display: true, text: 'Pression (kPa)' } }
            }
        }
    });
}

function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-md-4">
            <label class="form-label"><strong>Temp. source chaude (K)</strong></label>
            <input type="range" class="form-range" id="t_chaude" min="400" max="800" value="500" step="10">
            <div class="text-center"><span id="val-tc" class="badge bg-danger">500 K</span></div>
        </div>
        <div class="col-md-4">
            <label class="form-label"><strong>Temp. source froide (K)</strong></label>
            <input type="range" class="form-range" id="t_froide" min="250" max="400" value="300" step="10">
            <div class="text-center"><span id="val-tf" class="badge bg-info">300 K</span></div>
        </div>
        <div class="col-md-4">
            <label class="form-label"><strong>Chaleur entrée (kJ)</strong></label>
            <input type="range" class="form-range" id="q_in" min="100" max="5000" value="1000" step="100">
            <div class="text-center"><span id="val-q" class="badge bg-warning">1000 kJ</span></div>
        </div>
    `;

    document.getElementById('t_chaude').addEventListener('input', updateCycle);
    document.getElementById('t_froide').addEventListener('input', updateCycle);
    document.getElementById('q_in').addEventListener('input', updateCycle);
}

function updateCycle() {
    simState.T_chaude = parseFloat(document.getElementById('t_chaude').value);
    simState.T_froide = parseFloat(document.getElementById('t_froide').value);
    simState.Q_in = parseFloat(document.getElementById('q_in').value);

    document.getElementById('val-tc').innerText = simState.T_chaude + ' K';
    document.getElementById('val-tf').innerText = simState.T_froide + ' K';
    document.getElementById('val-q').innerText = simState.Q_in + ' kJ';

    tracerCycleCarnot();
}

function tracerCycleCarnot() {
    // Cycle de Carnot dans le diagramme P-V
    const V1 = 1, V2 = 2, V3 = 4, V4 = 2.5;
    const R = 8.314;
    const n = 1;

    const volumes = [];
    const pressions = [];

    // 1->2 : Expansion isotherme à T_chaude
    for (let V = V1; V <= V2; V += 0.05) {
        volumes.push(V);
        pressions.push((n * R * simState.T_chaude) / V / 1000);
    }

    // 2->3 : Expansion adiabatique
    const gamma = 1.4;
    for (let V = V2; V <= V3; V += 0.05) {
        volumes.push(V);
        const P = ((n * R * simState.T_chaude) / V2) * Math.pow(V2 / V, gamma) / 1000;
        pressions.push(P);
    }

    // 3->4 : Compression isotherme à T_froide
    for (let V = V3; V >= V4; V -= 0.05) {
        volumes.push(V);
        pressions.push((n * R * simState.T_froide) / V / 1000);
    }

    // 4->1 : Compression adiabatique
    for (let V = V4; V >= V1; V -= 0.05) {
        volumes.push(V);
        const P = ((n * R * simState.T_froide) / V4) * Math.pow(V4 / V, gamma) / 1000;
        pressions.push(P);
    }

    scopeChart.data.labels = volumes.map(v => v.toFixed(2));
    scopeChart.data.datasets[0].data = pressions;
    scopeChart.update();
}

function getParametresActuels() {
    return {
        T_chaude_K: simState.T_chaude,
        T_froide_K: simState.T_froide,
        Q_entree_kJ: simState.Q_in
    };
}

function getResultatsActuels() {
    const rendement_carnot = 1 - (simState.T_froide / simState.T_chaude);
    const W_utile = simState.Q_in * rendement_carnot;
    const Q_out = simState.Q_in - W_utile;

    return {
        Rendement_Carnot: (rendement_carnot * 100).toFixed(2) + ' %',
        Travail_utile_kJ: W_utile.toFixed(2),
        Chaleur_rejetee_kJ: Q_out.toFixed(2)
    };
}

initChart();
generateControls();
updateCycle();