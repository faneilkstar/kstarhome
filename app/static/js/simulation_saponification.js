// ============================================================
// SIMULATION SAPONIFICATION
// Production de savon à partir d'un triglycéride + base
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState, reactionRunning = false;

simState = {
    type_huile: 'olive',  // olive, coco, palme
    concentration_naoh: 10,  // mol/L
    temperature: 80,  // °C
    temps_reaction: 0,
    taux_conversion: 0,
    masse_savon: 0,
    glycerol_produit: 0
};

// Données des huiles
const huiles = {
    'olive': { nom: 'Huile d\'olive', indice_sap: 189, couleur: '#90EE90' },
    'coco': { nom: 'Huile de coco', indice_sap: 257, couleur: '#FFFACD' },
    'palme': { nom: 'Huile de palme', indice_sap: 199, couleur: '#FFD700' }
};

function initChart() {
    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Taux de conversion (%)',
                    data: [],
                    borderColor: '#2ecc71',
                    borderWidth: 3,
                    fill: true,
                    backgroundColor: 'rgba(46, 204, 113, 0.2)',
                    yAxisID: 'y1'
                },
                {
                    label: 'Masse de savon (g)',
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
                x: { title: { display: true, text: 'Temps (min)' } },
                y1: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Conversion (%)' },
                    min: 0,
                    max: 100
                },
                y2: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Masse savon (g)' },
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
            <label class="form-label"><strong>Type d'huile</strong></label>
            <select id="type_huile" class="form-select" onchange="updateParams()">
                <option value="olive" selected>Huile d'olive</option>
                <option value="coco">Huile de coco</option>
                <option value="palme">Huile de palme</option>
            </select>
        </div>
        <div class="col-md-4">
            <label class="form-label"><strong>Concentration NaOH (mol/L)</strong></label>
            <input type="range" class="form-range" id="conc_naoh" min="5" max="20" value="10" step="1" oninput="updateParams()">
            <div class="text-center"><span id="val-naoh" class="badge bg-warning">10 M</span></div>
        </div>
        <div class="col-md-4">
            <label class="form-label"><strong>Température (°C)</strong></label>
            <input type="range" class="form-range" id="temperature" min="60" max="100" value="80" step="5" oninput="updateParams()">
            <div class="text-center"><span id="val-temp" class="badge bg-danger">80 °C</span></div>
        </div>
        <div class="col-12 mt-3">
            <div class="alert alert-info">
                <strong>Réaction :</strong><br>
                Triglycéride + 3 NaOH → Glycérol + 3 Savon (sel de sodium d'acide gras)
            </div>
        </div>
        <div class="col-12">
            <button class="btn btn-success btn-lg w-100" onclick="toggleReaction()">
                <i class="fas fa-flask"></i> <span id="btn-text">Lancer la saponification</span>
            </button>
        </div>
    `;
}

function updateParams() {
    simState.type_huile = document.getElementById('type_huile').value;
    simState.concentration_naoh = parseFloat(document.getElementById('conc_naoh').value);
    simState.temperature = parseFloat(document.getElementById('temperature').value);

    document.getElementById('val-naoh').innerText = simState.concentration_naoh + ' M';
    document.getElementById('val-temp').innerText = simState.temperature + ' °C';
}

let dataLabels = [];
let dataConversion = [];
let dataSavon = [];

function toggleReaction() {
    reactionRunning = !reactionRunning;
    const btn = document.getElementById('btn-text');

    if (reactionRunning) {
        btn.innerHTML = '<i class="fas fa-pause"></i> Pause';
        runReaction();
    } else {
        btn.innerHTML = '<i class="fas fa-play"></i> Reprendre';
    }
}

function runReaction() {
    if (!reactionRunning) return;

    simState.temps_reaction += 0.5;  // 0.5 minute

    // Calcul du taux de conversion (cinétique simplifié)
    // Dépend de la température et de la concentration
    const k = 0.05 * (simState.temperature / 80) * (simState.concentration_naoh / 10);
    simState.taux_conversion = 100 * (1 - Math.exp(-k * simState.temps_reaction));

    // Masse de savon produite (supposons 100g d'huile initiale)
    const masse_huile = 100;  // g
    const indice_sap = huiles[simState.type_huile].indice_sap;
    simState.masse_savon = (masse_huile * indice_sap / 1000) * (simState.taux_conversion / 100);

    // Glycérol (sous-produit)
    simState.glycerol_produit = simState.masse_savon * 0.1;  // Approximation

    // Ajouter aux données
    dataLabels.push(simState.temps_reaction.toFixed(1));
    dataConversion.push(simState.taux_conversion);
    dataSavon.push(simState.masse_savon);

    // Limiter à 100 points
    if (dataLabels.length > 100) {
        dataLabels.shift();
        dataConversion.shift();
        dataSavon.shift();
    }

    // Mettre à jour le graphique
    scopeChart.data.labels = dataLabels;
    scopeChart.data.datasets[0].data = dataConversion;
    scopeChart.data.datasets[1].data = dataSavon;
    scopeChart.update('none');

    // Arrêter à 99% de conversion
    if (simState.taux_conversion < 99) {
        setTimeout(runReaction, 200);
    } else {
        reactionRunning = false;
        document.getElementById('btn-text').innerHTML = '<i class="fas fa-check"></i> Réaction terminée';
    }
}

function getParametresActuels() {
    return {
        Type_huile: huiles[simState.type_huile].nom,
        Concentration_NaOH_M: simState.concentration_naoh,
        Temperature_C: simState.temperature
    };
}

function getResultatsActuels() {
    return {
        Taux_conversion_pourcent: simState.taux_conversion.toFixed(2),
        Masse_savon_g: simState.masse_savon.toFixed(2),
        Glycerol_g: simState.glycerol_produit.toFixed(2),
        Temps_reaction_min: simState.temps_reaction.toFixed(1)
    };
}

initChart();
generateControls();
updateParams();