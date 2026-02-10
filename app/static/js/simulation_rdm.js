// ============================================================
// SIMULATION RDM - POUTRE EN FLEXION
// Génie Civil - Assistant ETA
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState;

simState = {
    L: 4,          // Longueur poutre (m)
    q: 5000,       // Charge répartie (N/m)
    E: 210e9,      // Module Young (acier)
    I: 1e-5,       // Inertie (m^4)
    points: []
};

function initChart() {
    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Moment fléchissant M(x)',
                    data: [],
                    borderColor: '#e74c3c',
                    borderWidth: 3,
                    fill: false,
                    yAxisID: 'y1'
                },
                {
                    label: 'Flèche δ(x)',
                    data: [],
                    borderColor: '#3498db',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    yAxisID: 'y2'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Position x (m)' }
                },
                y1: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Moment (N.m)', color: '#e74c3c' }
                },
                y2: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Flèche (mm)', color: '#3498db' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
}

function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-md-4">
            <label class="form-label"><strong>Longueur L (m)</strong></label>
            <input type="range" class="form-range" id="longueur" min="2" max="10" value="4" step="0.5">
            <div class="text-center">
                <span id="val-l" class="badge bg-danger fs-6">4 m</span>
            </div>
        </div>
        <div class="col-md-4">
            <label class="form-label"><strong>Charge q (kN/m)</strong></label>
            <input type="range" class="form-range" id="charge" min="1" max="20" value="5" step="1">
            <div class="text-center">
                <span id="val-q" class="badge bg-warning fs-6">5 kN/m</span>
            </div>
        </div>
        <div class="col-md-4">
            <label class="form-label"><strong>Inertie I (cm⁴)</strong></label>
            <input type="range" class="form-range" id="inertie" min="50" max="500" value="100" step="10">
            <div class="text-center">
                <span id="val-i" class="badge bg-info fs-6">100 cm⁴</span>
            </div>
        </div>
    `;

    document.getElementById('longueur').addEventListener('input', updateSim);
    document.getElementById('charge').addEventListener('input', updateSim);
    document.getElementById('inertie').addEventListener('input', updateSim);
}

function updateSim() {
    simState.L = parseFloat(document.getElementById('longueur').value);
    simState.q = parseFloat(document.getElementById('charge').value) * 1000; // kN -> N
    simState.I = parseFloat(document.getElementById('inertie').value) * 1e-8; // cm^4 -> m^4

    document.getElementById('val-l').innerText = simState.L + ' m';
    document.getElementById('val-q').innerText = (simState.q / 1000) + ' kN/m';
    document.getElementById('val-i').innerText = (simState.I * 1e8) + ' cm⁴';

    calculerPoutre();
}

function calculerPoutre() {
    const n = 50;
    const dx = simState.L / n;

    const labels = [];
    const moments = [];
    const fleches = [];

    for (let i = 0; i <= n; i++) {
        const x = i * dx;

        // Moment fléchissant (poutre bi-appuyée, charge répartie)
        const M = (simState.q * x / 2) * (simState.L - x);

        // Flèche (formule exacte)
        const delta = -(simState.q / (24 * simState.E * simState.I)) * x *
                      (Math.pow(simState.L, 3) - 2 * simState.L * x * x + Math.pow(x, 3));

        labels.push(x.toFixed(2));
        moments.push(M);
        fleches.push(delta * 1000); // m -> mm
    }

    scopeChart.data.labels = labels;
    scopeChart.data.datasets[0].data = moments;
    scopeChart.data.datasets[1].data = fleches;
    scopeChart.update();
}

function getParametresActuels() {
    return {
        Longueur_m: simState.L,
        Charge_N_m: simState.q,
        Module_Young_GPa: simState.E / 1e9,
        Inertie_cm4: simState.I * 1e8
    };
}

function getResultatsActuels() {
    const Mmax = (simState.q * Math.pow(simState.L, 2)) / 8;
    const deltaMax = (5 * simState.q * Math.pow(simState.L, 4)) / (384 * simState.E * simState.I);

    return {
        Moment_max_Nm: Mmax.toFixed(0),
        Fleche_max_mm: (deltaMax * 1000).toFixed(2),
        Position_Mmax_m: (simState.L / 2).toFixed(2)
    };
}

initChart();
generateControls();
updateSim();