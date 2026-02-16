// ============================================================
// SIMULATION OPTIQUE GÉOMÉTRIQUE
// Lentilles convergentes/divergentes, Miroirs, Formation d'images
// Assistant ALPHA
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState;

simState = {
    type: 'lentille_convergente',  // lentille_convergente, lentille_divergente, miroir_concave, miroir_convexe
    focale: 10,    // cm
    position_objet: -15,  // cm (négatif = avant la lentille)
    hauteur_objet: 3,     // cm
    position_image: 0,
    hauteur_image: 0,
    grandissement: 0
};

function initChart() {
    // Pour l'optique, on utilise un graphique de type scatter pour tracer les rayons
    scopeChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Rayon incident 1',
                    data: [],
                    borderColor: '#e74c3c',
                    borderWidth: 2,
                    showLine: true,
                    pointRadius: 0
                },
                {
                    label: 'Rayon incident 2',
                    data: [],
                    borderColor: '#3498db',
                    borderWidth: 2,
                    showLine: true,
                    pointRadius: 0
                },
                {
                    label: 'Rayon réfracté 1',
                    data: [],
                    borderColor: '#e74c3c',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    showLine: true,
                    pointRadius: 0
                },
                {
                    label: 'Rayon réfracté 2',
                    data: [],
                    borderColor: '#3498db',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    showLine: true,
                    pointRadius: 0
                },
                {
                    label: 'Objet',
                    data: [],
                    borderColor: '#2ecc71',
                    borderWidth: 4,
                    showLine: true,
                    pointRadius: 5,
                    pointStyle: 'triangle'
                },
                {
                    label: 'Image',
                    data: [],
                    borderColor: '#f39c12',
                    borderWidth: 4,
                    showLine: true,
                    pointRadius: 5,
                    pointStyle: 'triangle'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Position (cm)' },
                    min: -30,
                    max: 30
                },
                y: {
                    title: { display: true, text: 'Hauteur (cm)' },
                    min: -10,
                    max: 10
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-md-3">
            <label class="form-label"><strong>Type de système</strong></label>
            <select id="type_optique" class="form-select" onchange="updateSim()">
                <option value="lentille_convergente" selected>🔍 Lentille convergente</option>
                <option value="lentille_divergente">🔎 Lentille divergente</option>
                <option value="miroir_concave">🪞 Miroir concave</option>
                <option value="miroir_convexe">🪞 Miroir convexe</option>
            </select>
        </div>
        <div class="col-md-3">
            <label class="form-label"><strong>Focale f (cm)</strong></label>
            <input type="range" class="form-range" id="focale" min="5" max="30" value="10" step="1" oninput="updateSim()">
            <div class="text-center"><span id="val-f" class="badge bg-primary">10 cm</span></div>
        </div>
        <div class="col-md-3">
            <label class="form-label"><strong>Position objet (cm)</strong></label>
            <input type="range" class="form-range" id="pos_objet" min="-50" max="-5" value="-15" step="1" oninput="updateSim()">
            <div class="text-center"><span id="val-po" class="badge bg-danger">-15 cm</span></div>
        </div>
        <div class="col-md-3">
            <label class="form-label"><strong>Hauteur objet (cm)</strong></label>
            <input type="range" class="form-range" id="hauteur_objet" min="1" max="8" value="3" step="0.5" oninput="updateSim()">
            <div class="text-center"><span id="val-ho" class="badge bg-success">3 cm</span></div>
        </div>
        <div class="col-12 mt-3">
            <div class="alert alert-info" id="info-resultat">
                <strong>Relations de conjugaison :</strong> 1/f = 1/p' - 1/p (Descartes)
            </div>
        </div>
    `;
}

function updateSim() {
    simState.type = document.getElementById('type_optique').value;
    simState.focale = parseFloat(document.getElementById('focale').value);
    simState.position_objet = parseFloat(document.getElementById('pos_objet').value);
    simState.hauteur_objet = parseFloat(document.getElementById('hauteur_objet').value);

    // Ajuster le signe de f selon le type
    let f = simState.focale;
    if (simState.type === 'lentille_divergente' || simState.type === 'miroir_convexe') {
        f = -f;
    }

    document.getElementById('val-f').innerText = simState.focale + ' cm';
    document.getElementById('val-po').innerText = simState.position_objet + ' cm';
    document.getElementById('val-ho').innerText = simState.hauteur_objet + ' cm';

    // Calculer position de l'image (relation de conjugaison)
    const p = simState.position_objet;

    // 1/f = 1/p' - 1/p  =>  p' = (f*p) / (p + f)
    simState.position_image = (f * p) / (p + f);

    // Grandissement : γ = p' / p = h' / h
    simState.grandissement = simState.position_image / p;
    simState.hauteur_image = simState.grandissement * simState.hauteur_objet;

    // Afficher les résultats
    const infoBox = document.getElementById('info-resultat');
    const nature = simState.position_image > 0 ? 'Réelle' : 'Virtuelle';
    const sens = simState.grandissement > 0 ? 'Droite' : 'Renversée';

    infoBox.innerHTML = `
        <strong>📍 Position image :</strong> ${simState.position_image.toFixed(2)} cm (${nature})<br>
        <strong>📏 Hauteur image :</strong> ${simState.hauteur_image.toFixed(2)} cm<br>
        <strong>🔍 Grandissement :</strong> γ = ${simState.grandissement.toFixed(2)} (${sens})
    `;

    tracerRayons();
}

function tracerRayons() {
    // Objet (flèche verte)
    scopeChart.data.datasets[4].data = [
        { x: simState.position_objet, y: 0 },
        { x: simState.position_objet, y: simState.hauteur_objet }
    ];

    // Image (flèche orange)
    scopeChart.data.datasets[5].data = [
        { x: simState.position_image, y: 0 },
        { x: simState.position_image, y: simState.hauteur_image }
    ];

    // Rayon 1 : Parallèle à l'axe, passe par F'
    scopeChart.data.datasets[0].data = [
        { x: simState.position_objet, y: simState.hauteur_objet },
        { x: 0, y: simState.hauteur_objet }
    ];

    scopeChart.data.datasets[2].data = [
        { x: 0, y: simState.hauteur_objet },
        { x: simState.position_image, y: simState.hauteur_image }
    ];

    // Rayon 2 : Passe par le centre optique
    scopeChart.data.datasets[1].data = [
        { x: simState.position_objet, y: simState.hauteur_objet },
        { x: 0, y: simState.hauteur_objet }
    ];

    scopeChart.data.datasets[3].data = [
        { x: 0, y: simState.hauteur_objet },
        { x: simState.position_image, y: simState.hauteur_image }
    ];

    scopeChart.update();
}

function getParametresActuels() {
    return {
        Type: simState.type,
        Focale_cm: simState.focale,
        Position_objet_cm: simState.position_objet,
        Hauteur_objet_cm: simState.hauteur_objet
    };
}

function getResultatsActuels() {
    return {
        Position_image_cm: simState.position_image.toFixed(2),
        Hauteur_image_cm: simState.hauteur_image.toFixed(2),
        Grandissement: simState.grandissement.toFixed(2),
        Nature: simState.position_image > 0 ? 'Réelle' : 'Virtuelle'
    };
}

initChart();
generateControls();
updateSim();