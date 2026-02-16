// ============================================================
// SIMULATION ÉLECTRONIQUE LOGIQUE
// Portes logiques, Tables de vérité, Circuits combinatoires
// Assistant ALPHA
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState;

simState = {
    porte: 'AND',
    entree_A: 0,
    entree_B: 0,
    sortie: 0,
    historique: []
};

const PORTES_LOGIQUES = {
    'AND': (a, b) => a && b,
    'OR': (a, b) => a || b,
    'NOT': (a) => !a,
    'NAND': (a, b) => !(a && b),
    'NOR': (a, b) => !(a || b),
    'XOR': (a, b) => a !== b,
    'XNOR': (a, b) => a === b
};

function initChart() {
    // Graphique chronogramme (signaux numériques)
    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Entrée A',
                    data: [],
                    borderColor: '#3498db',
                    borderWidth: 3,
                    stepped: true,
                    fill: false
                },
                {
                    label: 'Entrée B',
                    data: [],
                    borderColor: '#2ecc71',
                    borderWidth: 3,
                    stepped: true,
                    fill: false
                },
                {
                    label: 'Sortie S',
                    data: [],
                    borderColor: '#e74c3c',
                    borderWidth: 3,
                    stepped: true,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Temps (cycles)' }
                },
                y: {
                    title: { display: true, text: 'État logique' },
                    min: -0.2,
                    max: 1.2,
                    ticks: {
                        callback: function(value) {
                            return value === 0 ? '0' : value === 1 ? '1' : '';
                        }
                    }
                }
            }
        }
    });
}

function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-md-4">
            <label class="form-label"><strong>Porte logique</strong></label>
            <select id="porte" class="form-select" onchange="updateSim()">
                <option value="AND" selected>AND (ET)</option>
                <option value="OR">OR (OU)</option>
                <option value="NOT">NOT (NON)</option>
                <option value="NAND">NAND (NON-ET)</option>
                <option value="NOR">NOR (NON-OU)</option>
                <option value="XOR">XOR (OU exclusif)</option>
                <option value="XNOR">XNOR (Équivalence)</option>
            </select>
        </div>
        <div class="col-md-4">
            <label class="form-label"><strong>Entrée A</strong></label>
            <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" id="entree_a" onchange="updateSim()" style="width: 60px; height: 30px;">
                <label class="form-check-label ms-3" id="label-a">0 (OFF)</label>
            </div>
        </div>
        <div class="col-md-4" id="container-b">
            <label class="form-label"><strong>Entrée B</strong></label>
            <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" id="entree_b" onchange="updateSim()" style="width: 60px; height: 30px;">
                <label class="form-check-label ms-3" id="label-b">0 (OFF)</label>
            </div>
        </div>
        <div class="col-12 mt-3">
            <div class="card">
                <div class="card-header bg-dark text-white">
                    <strong>Sortie S</strong>
                </div>
                <div class="card-body text-center">
                    <h1 id="sortie-value" class="display-1" style="color: #e74c3c;">0</h1>
                </div>
            </div>
        </div>
        <div class="col-12 mt-3">
            <button class="btn btn-primary w-100" onclick="ajouterAuChronogramme()">
                <i class="fas fa-plus"></i> Ajouter au chronogramme
            </button>
            <button class="btn btn-secondary w-100 mt-2" onclick="resetChronogramme()">
                <i class="fas fa-redo"></i> Réinitialiser
            </button>
        </div>
        <div class="col-12 mt-3">
            <div class="alert alert-info">
                <strong>Table de vérité :</strong>
                <table class="table table-sm mt-2" id="table-verite"></table>
            </div>
        </div>
    `;

    genererTableVerite();
}

function updateSim() {
    simState.porte = document.getElementById('porte').value;
    simState.entree_A = document.getElementById('entree_a').checked ? 1 : 0;

    // Masquer entrée B pour NOT
    const containerB = document.getElementById('container-b');
    if (simState.porte === 'NOT') {
        containerB.style.display = 'none';
        simState.entree_B = 0;
    } else {
        containerB.style.display = 'block';
        simState.entree_B = document.getElementById('entree_b').checked ? 1 : 0;
    }

    // Calculer sortie
    const fonction = PORTES_LOGIQUES[simState.porte];
    simState.sortie = fonction(simState.entree_A === 1, simState.entree_B === 1) ? 1 : 0;

    // Afficher
    document.getElementById('label-a').innerText = simState.entree_A ? '1 (ON)' : '0 (OFF)';
    if (simState.porte !== 'NOT') {
        document.getElementById('label-b').innerText = simState.entree_B ? '1 (ON)' : '0 (OFF)';
    }

    const sortieElem = document.getElementById('sortie-value');
    sortieElem.innerText = simState.sortie;
    sortieElem.style.color = simState.sortie ? '#2ecc71' : '#e74c3c';

    genererTableVerite();
}

function genererTableVerite() {
    const table = document.getElementById('table-verite');
    const fonction = PORTES_LOGIQUES[simState.porte];

    if (simState.porte === 'NOT') {
        table.innerHTML = `
            <thead><tr><th>A</th><th>S</th></tr></thead>
            <tbody>
                <tr><td>0</td><td>${fonction(false) ? 1 : 0}</td></tr>
                <tr><td>1</td><td>${fonction(true) ? 1 : 0}</td></tr>
            </tbody>
        `;
    } else {
        table.innerHTML = `
            <thead><tr><th>A</th><th>B</th><th>S</th></tr></thead>
            <tbody>
                <tr><td>0</td><td>0</td><td>${fonction(false, false) ? 1 : 0}</td></tr>
                <tr><td>0</td><td>1</td><td>${fonction(false, true) ? 1 : 0}</td></tr>
                <tr><td>1</td><td>0</td><td>${fonction(true, false) ? 1 : 0}</td></tr>
                <tr><td>1</td><td>1</td><td>${fonction(true, true) ? 1 : 0}</td></tr>
            </tbody>
        `;
    }
}

function ajouterAuChronogramme() {
    simState.historique.push({
        A: simState.entree_A,
        B: simState.entree_B,
        S: simState.sortie
    });

    // Limiter à 20 cycles
    if (simState.historique.length > 20) {
        simState.historique.shift();
    }

    // Mettre à jour le graphique
    const labels = simState.historique.map((_, i) => i);
    const dataA = simState.historique.map(h => h.A);
    const dataB = simState.historique.map(h => h.B);
    const dataS = simState.historique.map(h => h.S);

    scopeChart.data.labels = labels;
    scopeChart.data.datasets[0].data = dataA;
    scopeChart.data.datasets[1].data = dataB;
    scopeChart.data.datasets[2].data = dataS;
    scopeChart.update();
}

function resetChronogramme() {
    simState.historique = [];
    scopeChart.data.labels = [];
    scopeChart.data.datasets[0].data = [];
    scopeChart.data.datasets[1].data = [];
    scopeChart.data.datasets[2].data = [];
    scopeChart.update();
}

function getParametresActuels() {
    return {
        Porte: simState.porte,
        Entree_A: simState.entree_A,
        Entree_B: simState.entree_B
    };
}

function getResultatsActuels() {
    return {
        Sortie: simState.sortie,
        Nb_cycles: simState.historique.length
    };
}

initChart();
generateControls();
updateSim();