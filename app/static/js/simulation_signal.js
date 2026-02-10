// ============================================================
// SIMULATION TRAITEMENT DU SIGNAL
// Analyse de Fourier, Filtrage
// Assistant ALPHA
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState;

simState = {
    freq: 5,
    amplitude: 1,
    noise: 0.2,
    filter: 5,
    signal: [],
    filtered: []
};

function initChart() {
    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Signal bruité',
                    data: [],
                    borderColor: '#95a5a6',
                    borderWidth: 1,
                    pointRadius: 0
                },
                {
                    label: 'Signal filtré',
                    data: [],
                    borderColor: '#2ecc71',
                    borderWidth: 2,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: { title: { display: true, text: 'Temps (s)' } },
                y: { title: { display: true, text: 'Amplitude' }, min: -2, max: 2 }
            }
        }
    });
}

function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-md-4">
            <label class="form-label"><strong>Fréquence (Hz)</strong></label>
            <input type="range" class="form-range" id="freq" min="1" max="20" value="5" step="1">
            <div class="text-center"><span id="val-freq" class="badge bg-primary">5 Hz</span></div>
        </div>
        <div class="col-md-4">
            <label class="form-label"><strong>Niveau de bruit (%)</strong></label>
            <input type="range" class="form-range" id="noise" min="0" max="100" value="20" step="5">
            <div class="text-center"><span id="val-noise" class="badge bg-danger">20 %</span></div>
        </div>
        <div class="col-md-4">
            <label class="form-label"><strong>Taille filtre (pts)</strong></label>
            <input type="range" class="form-range" id="filter" min="1" max="50" value="5" step="1">
            <div class="text-center"><span id="val-filter" class="badge bg-success">5 pts</span></div>
        </div>
    `;

    document.getElementById('freq').addEventListener('input', updateSignal);
    document.getElementById('noise').addEventListener('input', updateSignal);
    document.getElementById('filter').addEventListener('input', updateSignal);
}

function updateSignal() {
    simState.freq = parseFloat(document.getElementById('freq').value);
    simState.noise = parseFloat(document.getElementById('noise').value) / 100;
    simState.filter = parseInt(document.getElementById('filter').value);

    document.getElementById('val-freq').innerText = simState.freq + ' Hz';
    document.getElementById('val-noise').innerText = (simState.noise * 100) + ' %';
    document.getElementById('val-filter').innerText = simState.filter + ' pts';

    generateSignal();
}

function generateSignal() {
    const n = 200;
    const dt = 0.01;
    const omega = 2 * Math.PI * simState.freq;

    const labels = [];
    const signalBruit = [];
    const signalFiltre = [];

    // Génération signal + bruit
    for (let i = 0; i < n; i++) {
        const t = i * dt;
        const clean = simState.amplitude * Math.sin(omega * t);
        const noisy = clean + (Math.random() - 0.5) * 2 * simState.noise;

        labels.push(t.toFixed(2));
        signalBruit.push(noisy);
    }

    // Filtrage (moyenne mobile)
    for (let i = 0; i < n; i++) {
        let sum = 0;
        let count = 0;

        for (let j = Math.max(0, i - simState.filter); j <= Math.min(n - 1, i + simState.filter); j++) {
            sum += signalBruit[j];
            count++;
        }

        signalFiltre.push(sum / count);
    }

    scopeChart.data.labels = labels;
    scopeChart.data.datasets[0].data = signalBruit;
    scopeChart.data.datasets[1].data = signalFiltre;
    scopeChart.update();

    simState.signal = signalBruit;
    simState.filtered = signalFiltre;
}

function getParametresActuels() {
    return {
        Frequence_Hz: simState.freq,
        Bruit_pourcent: (simState.noise * 100).toFixed(0),
        Taille_filtre: simState.filter
    };
}

function getResultatsActuels() {
    const snr_avant = calculerSNR(simState.signal);
    const snr_apres = calculerSNR(simState.filtered);

    return {
        SNR_avant_dB: snr_avant.toFixed(2),
        SNR_apres_dB: snr_apres.toFixed(2),
        Amelioration_dB: (snr_apres - snr_avant).toFixed(2)
    };
}

function calculerSNR(signal) {
    const mean = signal.reduce((a, b) => a + b, 0) / signal.length;
    const variance = signal.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / signal.length;
    return 10 * Math.log10(1 / variance);
}

initChart();
generateControls();
updateSignal();