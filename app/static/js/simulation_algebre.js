// ============================================================
// SIMULATION ALGÈBRE & TRANSFORMATIONS
// Matrices, Rotations, Compressions, Transformations linéaires
// Assistant ALPHA
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState;

simState = {
    transformation: 'rotation',  // rotation, homothetie, cisaillement, projection
    angle: 45,           // degrés
    facteur_x: 1.5,
    facteur_y: 1.5,
    cisaillement: 0.5,
    points_originaux: [],
    points_transformes: []
};

function initChart() {
    scopeChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Figure originale',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.3)',
                    borderWidth: 2,
                    showLine: true,
                    pointRadius: 5
                },
                {
                    label: 'Figure transformée',
                    data: [],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.3)',
                    borderWidth: 2,
                    showLine: true,
                    pointRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'x' },
                    min: -5,
                    max: 5
                },
                y: {
                    title: { display: true, text: 'y' },
                    min: -5,
                    max: 5
                }
            }
        }
    });
}

function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-md-3">
            <label class="form-label"><strong>Transformation</strong></label>
            <select id="transformation" class="form-select" onchange="changerTransformation()">
                <option value="rotation" selected>🔄 Rotation</option>
                <option value="homothetie">🔍 Homothétie (Zoom)</option>
                <option value="cisaillement">📐 Cisaillement (Shear)</option>
                <option value="projection">📽️ Projection</option>
                <option value="reflexion">🪞 Réflexion</option>
            </select>
        </div>
        <div id="controles-dynamiques" class="col-md-9">
            <!-- Généré dynamiquement -->
        </div>
        <div class="col-12 mt-3">
            <label class="form-label"><strong>Figure de base</strong></label>
            <div class="btn-group w-100">
                <button class="btn btn-outline-primary" onclick="chargerFigure('carre')">Carré</button>
                <button class="btn btn-outline-primary" onclick="chargerFigure('triangle')">Triangle</button>
                <button class="btn btn-outline-primary" onclick="chargerFigure('maison')">Maison</button>
                <button class="btn btn-outline-primary" onclick="chargerFigure('etoile')">Étoile</button>
            </div>
        </div>
        <div class="col-12 mt-3">
            <div class="alert alert-secondary">
                <strong>Matrice de transformation :</strong>
                <pre id="matrice-display" class="mt-2 mb-0"></pre>
            </div>
        </div>
    `;

    chargerFigure('carre');
    changerTransformation();
}

function changerTransformation() {
    simState.transformation = document.getElementById('transformation').value;
    const controles = document.getElementById('controles-dynamiques');

    if (simState.transformation === 'rotation') {
        controles.innerHTML = `
            <div class="col-12">
                <label class="form-label"><strong>Angle de rotation (°)</strong></label>
                <input type="range" class="form-range" id="angle" min="0" max="360" value="45" step="5" oninput="updateTransformation()">
                <div class="text-center"><span id="val-angle" class="badge bg-primary">45°</span></div>
            </div>
        `;
    } else if (simState.transformation === 'homothetie') {
        controles.innerHTML = `
            <div class="col-6">
                <label class="form-label"><strong>Facteur X</strong></label>
                <input type="range" class="form-range" id="facteur_x" min="0.5" max="3" value="1.5" step="0.1" oninput="updateTransformation()">
                <div class="text-center"><span id="val-fx" class="badge bg-primary">1.5</span></div>
            </div>
            <div class="col-6">
                <label class="form-label"><strong>Facteur Y</strong></label>
                <input type="range" class="form-range" id="facteur_y" min="0.5" max="3" value="1.5" step="0.1" oninput="updateTransformation()">
                <div class="text-center"><span id="val-fy" class="badge bg-primary">1.5</span></div>
            </div>
        `;
    } else if (simState.transformation === 'cisaillement') {
        controles.innerHTML = `
            <div class="col-12">
                <label class="form-label"><strong>Facteur de cisaillement</strong></label>
                <input type="range" class="form-range" id="cisaillement" min="-2" max="2" value="0.5" step="0.1" oninput="updateTransformation()">
                <div class="text-center"><span id="val-cis" class="badge bg-warning">0.5</span></div>
            </div>
        `;
    }

    updateTransformation();
}

function updateTransformation() {
    let matrice = [[1, 0], [0, 1]];  // Matrice identité

    if (simState.transformation === 'rotation') {
        simState.angle = parseFloat(document.getElementById('angle').value);
        document.getElementById('val-angle').innerText = simState.angle + '°';

        const rad = simState.angle * Math.PI / 180;
        matrice = [
            [Math.cos(rad), -Math.sin(rad)],
            [Math.sin(rad), Math.cos(rad)]
        ];

    } else if (simState.transformation === 'homothetie') {
        simState.facteur_x = parseFloat(document.getElementById('facteur_x').value);
        simState.facteur_y = parseFloat(document.getElementById('facteur_y').value);

        document.getElementById('val-fx').innerText = simState.facteur_x.toFixed(1);
        document.getElementById('val-fy').innerText = simState.facteur_y.toFixed(1);

        matrice = [
            [simState.facteur_x, 0],
            [0, simState.facteur_y]
        ];

    } else if (simState.transformation === 'cisaillement') {
        simState.cisaillement = parseFloat(document.getElementById('cisaillement').value);
        document.getElementById('val-cis').innerText = simState.cisaillement.toFixed(1);

        matrice = [
            [1, simState.cisaillement],
            [0, 1]
        ];

    } else if (simState.transformation === 'projection') {
        matrice = [
            [1, 0],
            [0, 0]
        ];

    } else if (simState.transformation === 'reflexion') {
        matrice = [
            [1, 0],
            [0, -1]
        ];
    }

    // Afficher la matrice
    document.getElementById('matrice-display').innerText =
        `[ ${matrice[0][0].toFixed(2)}  ${matrice[0][1].toFixed(2)} ]\n[ ${matrice[1][0].toFixed(2)}  ${matrice[1][1].toFixed(2)} ]`;

    // Appliquer transformation
    appliquerTransformation(matrice);
}

function chargerFigure(type) {
    if (type === 'carre') {
        simState.points_originaux = [
            {x: -1, y: -1},
            {x: 1, y: -1},
            {x: 1, y: 1},
            {x: -1, y: 1},
            {x: -1, y: -1}
        ];
    } else if (type === 'triangle') {
        simState.points_originaux = [
            {x: 0, y: 2},
            {x: -1.5, y: -1},
            {x: 1.5, y: -1},
            {x: 0, y: 2}
        ];
    } else if (type === 'maison') {
        simState.points_originaux = [
            {x: -1, y: 0}, {x: -1, y: 1}, {x: 1, y: 1}, {x: 1, y: 0}, {x: -1, y: 0},
            {x: -1, y: 1}, {x: 0, y: 2}, {x: 1, y: 1}
        ];
    } else if (type === 'etoile') {
        const pts = [];
        for (let i = 0; i < 10; i++) {
            const angle = (i * 36) * Math.PI / 180;
            const r = i % 2 === 0 ? 2 : 1;
            pts.push({x: r * Math.cos(angle), y: r * Math.sin(angle)});
        }
        pts.push(pts[0]);
        simState.points_originaux = pts;
    }

    updateTransformation();
}

function appliquerTransformation(matrice) {
    simState.points_transformes = simState.points_originaux.map(p => {
        return {
            x: matrice[0][0] * p.x + matrice[0][1] * p.y,
            y: matrice[1][0] * p.x + matrice[1][1] * p.y
        };
    });

    scopeChart.data.datasets[0].data = simState.points_originaux;
    scopeChart.data.datasets[1].data = simState.points_transformes;
    scopeChart.update();
}

function getParametresActuels() {
    return {
        Transformation: simState.transformation,
        Angle: simState.angle,
        Facteur_X: simState.facteur_x,
        Facteur_Y: simState.facteur_y
    };
}

function getResultatsActuels() {
    return {
        Nb_points: simState.points_originaux.length,
        Type_transformation: simState.transformation
    };
}

initChart();
generateControls();