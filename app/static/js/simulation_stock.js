// ============================================================
// SIMULATION GESTION STOCK & FLUX
// Modèle de Wilson, Flux tendu
// Assistant ALPHA
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState;

simState = {
    demande: 1000,     // Unités/mois
    cout_commande: 50,
    cout_stockage: 2,
    delai: 5,          // jours
    stock_initial: 200
};

function initChart() {
    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Niveau de stock',
                    data: [],
                    borderColor: '#3498db',
                    borderWidth: 2,
                    fill: true,
                    backgroundColor: 'rgba(52, 152, 219, 0.2)'
                },
                {
                    label: 'Seuil de réapprovisionnement',
                    data: [],
                    borderColor: '#e74c3c',
                    borderWidth: 1,
                    borderDash: [10, 5],
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: 'Temps (jours)' } },
                y: { title: { display: true, text: 'Quantité en stock' }, beginAtZero: true }
            }
        }
    });
}

function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-md-3">
            <label class="form-label"><strong>Demande (unités/mois)</strong></label>
            <input type="range" class="form-range" id="demande" min="100" max="5000" value="1000" step="100">
            <div class="text-center"><span id="val-demande" class="badge bg-primary">1000</span></div>
        </div>
        <div class="col-md-3">
            <label class="form-label"><strong>Coût commande (€)</strong></label>
            <input type="range" class="form-range" id="cout_cmd" min="10" max="200" value="50" step="10">
            <div class="text-center"><span id="val-cmd" class="badge bg-warning">50 €</span></div>
        </div>
        <div class="col-md-3">
            <label class="form-label"><strong>Coût stockage (€/unité/mois)</strong></label>
            <input type="range" class="form-range" id="cout_stock" min="0.5" max="10" value="2" step="0.5">
            <div class="text-center"><span id="val-stock" class="badge bg-info">2 €</span></div>
        </div>
        <div class="col-md-3">
            <label class="form-label"><strong>Délai livraison (jours)</strong></label>
            <input type="range" class="form-range" id="delai" min="1" max="30" value="5" step="1">
            <div class="text-center"><span id="val-delai" class="badge bg-secondary">5 j</span></div>
        </div>
    `;

    document.getElementById('demande').addEventListener('input', updateSim);
    document.getElementById('cout_cmd').addEventListener('input', updateSim);
    document.getElementById('cout_stock').addEventListener('input', updateSim);
    document.getElementById('delai').addEventListener('input', updateSim);
}

function updateSim() {
    simState.demande = parseFloat(document.getElementById('demande').value);
    simState.cout_commande = parseFloat(document.getElementById('cout_cmd').value);
    simState.cout_stockage = parseFloat(document.getElementById('cout_stock').value);
    simState.delai = parseFloat(document.getElementById('delai').value);

    document.getElementById('val-demande').innerText = simState.demande;
    document.getElementById('val-cmd').innerText = simState.cout_commande + ' €';
    document.getElementById('val-stock').innerText = simState.cout_stockage + ' €';
    document.getElementById('val-delai').innerText = simState.delai + ' j';

    simulerStock();
}

function simulerStock() {
    // Modèle de Wilson (Quantité Économique de Commande)
    const D = simState.demande;
    const Cc = simState.cout_commande;
    const Cp = simState.cout_stockage;

    const QEC = Math.sqrt((2 * D * Cc) / Cp);
    const demande_jour = D / 30;
    const seuil_reappro = demande_jour * simState.delai;

    const jours = 90;
    let stock = simState.stock_initial;
    const labels = [];
    const niveaux = [];
    const seuils = [];

    for (let jour = 0; jour < jours; jour++) {
        // Consommation quotidienne
        stock -= demande_jour;

        // Réapprovisionnement si sous le seuil
        if (stock <= seuil_reappro) {
            stock += QEC;
        }

        labels.push(jour);
        niveaux.push(Math.max(0, stock));
        seuils.push(seuil_reappro);
    }

    scopeChart.data.labels = labels;
    scopeChart.data.datasets[0].data = niveaux;
    scopeChart.data.datasets[1].data = seuils;
    scopeChart.update();
}

function getParametresActuels() {
    return {
        Demande_mois: simState.demande,
        Cout_commande: simState.cout_commande,
        Cout_stockage: simState.cout_stockage,
        Delai_jours: simState.delai
    };
}

function getResultatsActuels() {
    const D = simState.demande;
    const Cc = simState.cout_commande;
    const Cp = simState.cout_stockage;
    const QEC = Math.sqrt((2 * D * Cc) / Cp);

    return {
        QEC_unites: QEC.toFixed(0),
        Seuil_reappro: ((D / 30) * simState.delai).toFixed(0),
        Cout_total_annuel: ((D / QEC) * Cc + (QEC / 2) * Cp * 12).toFixed(2)
    };
}

initChart();
generateControls();
updateSim();