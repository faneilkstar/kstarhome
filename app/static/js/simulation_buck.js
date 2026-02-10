// ============================================================
// SIMULATION CONVERTISSEUR BUCK (Hacheur abaisseur)
// Génie Électrique - Assistant KAYT
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState, animationFrame;

// État de la simulation
simState = {
    vin: 24,
    alpha: 0.5,
    L: 0.001,      // Henry
    C: 0.0001,     // Farad
    R: 10,         // Ohm
    vout: 0,
    il: 0,
    t: 0,
    ripple: 0
};

// Initialisation du graphique
function initChart() {
    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Vout (Tension sortie)',
                    data: [],
                    borderColor: '#28a745',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1
                },
                {
                    label: 'Consigne (Vin × α)',
                    data: [],
                    borderColor: '#dc3545',
                    borderDash: [5, 5],
                    borderWidth: 1.5,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: {
                    display: true,
                    title: { display: true, text: 'Temps' }
                },
                y: {
                    beginAtZero: true,
                    max: 60,
                    title: { display: true, text: 'Tension (V)' }
                }
            },
            plugins: {
                legend: { display: true, position: 'top' }
            }
        }
    });
}

// Génération des contrôles HTML
function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-md-3">
            <label class="form-label"><strong>Vin (V)</strong></label>
            <input type="range" class="form-range" id="vin" min="5" max="50" value="24" step="1">
            <div class="text-center">
                <span id="val-vin" class="badge bg-primary fs-6">24 V</span>
            </div>
        </div>
        <div class="col-md-3">
            <label class="form-label"><strong>Alpha (Duty Cycle)</strong></label>
            <input type="range" class="form-range" id="alpha" min="0.1" max="0.9" step="0.05" value="0.5">
            <div class="text-center">
                <span id="val-alpha" class="badge bg-primary fs-6">0.5</span>
            </div>
        </div>
        <div class="col-md-3">
            <label class="form-label"><strong>Inductance L (mH)</strong></label>
            <input type="range" class="form-range" id="inductance" min="0.1" max="5" step="0.1" value="1">
            <div class="text-center">
                <span id="val-l" class="badge bg-secondary fs-6">1 mH</span>
            </div>
        </div>
        <div class="col-md-3">
            <label class="form-label"><strong>Condensateur C (µF)</strong></label>
            <input type="range" class="form-range" id="capa" min="10" max="500" step="10" value="100">
            <div class="text-center">
                <span id="val-c" class="badge bg-secondary fs-6">100 µF</span>
            </div>
        </div>
    `;

    // Event listeners
    document.getElementById('vin').addEventListener('input', updateParams);
    document.getElementById('alpha').addEventListener('input', updateParams);
    document.getElementById('inductance').addEventListener('input', updateParams);
    document.getElementById('capa').addEventListener('input', updateParams);
}

function updateParams() {
    simState.vin = parseFloat(document.getElementById('vin').value);
    simState.alpha = parseFloat(document.getElementById('alpha').value);
    simState.L = parseFloat(document.getElementById('inductance').value) * 1e-3;
    simState.C = parseFloat(document.getElementById('capa').value) * 1e-6;

    document.getElementById('val-vin').innerText = simState.vin + ' V';
    document.getElementById('val-alpha').innerText = simState.alpha.toFixed(2);
    document.getElementById('val-l').innerText = (simState.L * 1000).toFixed(1) + ' mH';
    document.getElementById('val-c').innerText = (simState.C * 1e6).toFixed(0) + ' µF';
}

// Moteur physique (intégration d'Euler)
let dataBuffer = [];
const maxPoints = 100;

function runPhysics() {
    const dt = 1e-6;  // 1 microseconde
    const T = 1 / 20000;  // Période de commutation 20 kHz

    for (let i = 0; i < 500; i++) {
        simState.t += dt;
        const cycleTime = simState.t % T;

        let di_dt = 0;
        if (cycleTime < simState.alpha * T) {
            di_dt = (simState.vin - simState.vout) / simState.L;
        } else {
            di_dt = -simState.vout / simState.L;
        }

        const dv_dt = (simState.il - simState.vout / simState.R) / simState.C;

        simState.il += di_dt * dt;
        simState.vout += dv_dt * dt;

        if (simState.vout < 0) simState.vout = 0;
    }

    // Mise à jour graphique
    if (dataBuffer.length > maxPoints) dataBuffer.shift();
    dataBuffer.push(simState.vout);

    scopeChart.data.labels = Array.from({length: dataBuffer.length}, (_, i) => i);
    scopeChart.data.datasets[0].data = dataBuffer;
    scopeChart.data.datasets[1].data = Array(dataBuffer.length).fill(simState.vin * simState.alpha);
    scopeChart.update('none');

    animationFrame = requestAnimationFrame(runPhysics);
}

// Fonctions pour l'enregistrement (appelées par salle_tp.html)
function getParametresActuels() {
    return {
        Vin: simState.vin,
        alpha: simState.alpha,
        L_mH: simState.L * 1000,
        C_uF: simState.C * 1e6,
        R: simState.R
    };
}

function getResultatsActuels() {
    const ripple = Math.abs(simState.vout - simState.vin * simState.alpha);
    return {
        Vout: simState.vout.toFixed(2),
        Vout_theorique: (simState.vin * simState.alpha).toFixed(2),
        Courant_L: simState.il.toFixed(3),
        Ripple: ripple.toFixed(3)
    };
}

// Initialisation
initChart();
generateControls();
updateParams();
runPhysics();