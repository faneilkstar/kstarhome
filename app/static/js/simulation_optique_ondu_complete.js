// ============================================================
// SIMULATION OPTIQUE ONDULATOIRE - VERSION COMPLÈTE
// Young, Lloyd, Fresnel (biprisme + miroirs), Billet, Meslin
// Assistant ALPHA
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState, diagramCanvas;

simState = {
    experience: 'young',
    lambda: 600,
    distance_sources: 0.5,
    distance_ecran: 1000,
    largeur_fente: 0.1,
    angle_biprisme: 1,
    angle_miroirs: 0.5
};

const EXPERIENCES = {
    'young': {
        nom: '👥 Fentes de Young',
        description: 'Deux fentes parallèles éclairées par une source monochromatique',
        nb_sources: 2,
        schema: 'young'
    },
    'lloyd': {
        nom: '🪞 Miroir de Lloyd',
        description: 'Source + image virtuelle par réflexion sur un miroir plan',
        nb_sources: 2,
        schema: 'lloyd'
    },
    'fresnel_biprisme': {
        nom: '🔺 Biprisme de Fresnel',
        description: 'Deux prismes accolés créent deux sources virtuelles',
        nb_sources: 2,
        schema: 'biprisme'
    },
    'fresnel_miroirs': {
        nom: '🪞🪞 Miroirs de Fresnel',
        description: 'Deux miroirs plans inclinés créent deux sources virtuelles',
        nb_sources: 2,
        schema: 'miroirs'
    },
    'billet': {
        nom: '⚡ Bilentille de Billet',
        description: 'Lentille coupée en deux formant deux images',
        nb_sources: 2,
        schema: 'billet'
    },
    'meslin': {
        nom: '🔲 Fentes de Meslin',
        description: 'Deux fentes larges avec cohérence partielle',
        nb_sources: 2,
        schema: 'meslin'
    }
};

function initChart() {
    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Intensité lumineuse',
                data: [],
                borderColor: '#f39c12',
                backgroundColor: 'rgba(243, 156, 18, 0.3)',
                borderWidth: 2,
                fill: true,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Position sur l\'écran (mm)' }
                },
                y: {
                    title: { display: true, text: 'Intensité (u.a.)' },
                    beginAtZero: true,
                    max: 1.2
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
        <div class="col-12 mb-3">
            <label class="form-label"><strong>Expérience d'interférences</strong></label>
            <select id="experience" class="form-select" onchange="changerExperience()">
                ${Object.keys(EXPERIENCES).map(key => 
                    `<option value="${key}">${EXPERIENCES[key].nom}</option>`
                ).join('')}
            </select>
            <div class="alert alert-info mt-2 mb-0" id="description-exp">
                ${EXPERIENCES['young'].description}
            </div>
        </div>
        
        <div class="col-md-3">
            <label class="form-label"><strong>Longueur d'onde λ (nm)</strong></label>
            <input type="range" class="form-range" id="lambda" min="400" max="700" value="600" step="10" oninput="updateSim()">
            <div class="text-center">
                <span id="val-lambda" class="badge" style="background: rgb(255, 150, 0)">600 nm</span>
            </div>
        </div>
        
        <div class="col-md-3" id="container-distance-sources">
            <label class="form-label"><strong>Distance sources a (mm)</strong></label>
            <input type="range" class="form-range" id="distance_sources" min="0.1" max="2" value="0.5" step="0.1" oninput="updateSim()">
            <div class="text-center"><span id="val-a" class="badge bg-primary">0.5 mm</span></div>
        </div>
        
        <div class="col-md-3">
            <label class="form-label"><strong>Distance écran D (m)</strong></label>
            <input type="range" class="form-range" id="distance_ecran" min="500" max="3000" value="1000" step="100" oninput="updateSim()">
            <div class="text-center"><span id="val-d" class="badge bg-secondary">1 m</span></div>
        </div>
        
        <div class="col-md-3" id="container-param-specifique">
            <!-- Paramètre spécifique selon l'expérience -->
        </div>
        
        <div class="col-12 mt-3">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <strong>📊 Résultats</strong>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4 text-center">
                            <h4 class="text-primary" id="val-interfrange">-</h4>
                            <small>Interfrange (mm)</small>
                        </div>
                        <div class="col-md-4 text-center">
                            <h4 class="text-success" id="val-ordre-max">-</h4>
                            <small>Ordre maximal</small>
                        </div>
                        <div class="col-md-4 text-center">
                            <h4 class="text-warning" id="val-contraste">-</h4>
                            <small>Contraste</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-12 mt-3">
            <div class="card">
                <div class="card-header bg-dark text-white">
                    <strong>🔬 Schéma du dispositif</strong>
                </div>
                <div class="card-body text-center" style="background: #f8f9fa;">
                    <canvas id="diagramCanvas" width="600" height="250"></canvas>
                </div>
            </div>
        </div>
    `;

    diagramCanvas = document.getElementById('diagramCanvas');
    changerExperience();
}

function changerExperience() {
    simState.experience = document.getElementById('experience').value;
    const exp = EXPERIENCES[simState.experience];

    document.getElementById('description-exp').innerText = exp.description;

    // Paramètres spécifiques
    const containerParam = document.getElementById('container-param-specifique');

    if (simState.experience === 'fresnel_biprisme') {
        containerParam.innerHTML = `
            <label class="form-label"><strong>Angle biprisme (°)</strong></label>
            <input type="range" class="form-range" id="angle_biprisme" min="0.5" max="5" value="1" step="0.1" oninput="updateSim()">
            <div class="text-center"><span id="val-angle-bi" class="badge bg-info">1°</span></div>
        `;
    } else if (simState.experience === 'fresnel_miroirs') {
        containerParam.innerHTML = `
            <label class="form-label"><strong>Angle miroirs (°)</strong></label>
            <input type="range" class="form-range" id="angle_miroirs" min="0.1" max="2" value="0.5" step="0.1" oninput="updateSim()">
            <div class="text-center"><span id="val-angle-mir" class="badge bg-info">0.5°</span></div>
        `;
    } else if (simState.experience === 'lloyd') {
        containerParam.innerHTML = `
            <label class="form-label"><strong>Hauteur source (mm)</strong></label>
            <input type="range" class="form-range" id="hauteur_lloyd" min="0.5" max="5" value="2" step="0.5" oninput="updateSim()">
            <div class="text-center"><span id="val-lloyd" class="badge bg-info">2 mm</span></div>
        `;
    } else if (simState.experience === 'meslin') {
        containerParam.innerHTML = `
            <label class="form-label"><strong>Largeur fente (mm)</strong></label>
            <input type="range" class="form-range" id="largeur_meslin" min="0.1" max="1" value="0.3" step="0.05" oninput="updateSim()">
            <div class="text-center"><span id="val-meslin" class="badge bg-info">0.3 mm</span></div>
        `;
    } else {
        containerParam.innerHTML = '';
    }

    updateSim();
}

function updateSim() {
    // Récupérer tous les paramètres
    simState.lambda = parseFloat(document.getElementById('lambda').value);
    simState.distance_sources = parseFloat(document.getElementById('distance_sources').value);
    simState.distance_ecran = parseFloat(document.getElementById('distance_ecran').value);

    // Paramètres spécifiques
    if (simState.experience === 'fresnel_biprisme') {
        simState.angle_biprisme = parseFloat(document.getElementById('angle_biprisme').value);
        document.getElementById('val-angle-bi').innerText = simState.angle_biprisme + '°';

        // Calcul distance entre sources virtuelles
        const n = 1.5;  // Indice du verre
        const alpha_rad = simState.angle_biprisme * Math.PI / 180;
        simState.distance_sources = 2 * (n - 1) * alpha_rad * simState.distance_ecran / 2;

    } else if (simState.experience === 'fresnel_miroirs') {
        simState.angle_miroirs = parseFloat(document.getElementById('angle_miroirs').value);
        document.getElementById('val-angle-mir').innerText = simState.angle_miroirs + '°';

        // Distance entre sources = 2 * d * sin(α)
        const alpha_rad = simState.angle_miroirs * Math.PI / 180;
        simState.distance_sources = 2 * 50 * Math.sin(alpha_rad);  // d = 50mm

    } else if (simState.experience === 'lloyd') {
        const hauteur = parseFloat(document.getElementById('hauteur_lloyd').value);
        document.getElementById('val-lloyd').innerText = hauteur + ' mm';
        simState.distance_sources = 2 * hauteur;

    } else if (simState.experience === 'meslin') {
        simState.largeur_fente = parseFloat(document.getElementById('largeur_meslin').value);
        document.getElementById('val-meslin').innerText = simState.largeur_fente + ' mm';
    }

    // Mise à jour badges
    const couleur = wavelengthToRGB(simState.lambda);
    document.getElementById('val-lambda').style.background = `rgb(${couleur.r}, ${couleur.g}, ${couleur.b})`;
    document.getElementById('val-lambda').innerText = simState.lambda + ' nm';
    document.getElementById('val-a').innerText = simState.distance_sources.toFixed(2) + ' mm';
    document.getElementById('val-d').innerText = (simState.distance_ecran / 1000).toFixed(1) + ' m';

    calculerInterferences();
    dessinerSchema();
}

function calculerInterferences() {
    const lambda_m = simState.lambda * 1e-9;
    const a_m = simState.distance_sources * 1e-3;
    const D_m = simState.distance_ecran * 1e-3;

    // Interfrange
    const interfrange = (lambda_m * D_m / a_m) * 1000;

    // Ordre maximal visible
    const largeur_observation = 20;  // mm
    const ordre_max = Math.floor(largeur_observation / (2 * interfrange));

    // Affichage
    document.getElementById('val-interfrange').innerText = interfrange.toFixed(3) + ' mm';
    document.getElementById('val-ordre-max').innerText = ordre_max;

    // Calcul figure d'interférence
    const n_points = 300;
    const positions = [];
    const intensites = [];

    for (let i = 0; i < n_points; i++) {
        const x = (i / n_points - 0.5) * largeur_observation;
        const x_m = x * 1e-3;

        // Différence de marche
        const delta = (a_m * x_m) / D_m;

        // Déphasage
        const phi = (2 * Math.PI * delta) / lambda_m;

        // Intensité de base
        let intensite = Math.pow(Math.cos(phi / 2), 2);

        // Modifications selon l'expérience
        if (simState.experience === 'lloyd') {
            // Changement de phase de π à la réflexion
            intensite = Math.pow(Math.sin(phi / 2), 2);
        }

        if (simState.experience === 'meslin') {
            // Enveloppe de diffraction
            const b_m = simState.largeur_fente * 1e-3;
            const beta = (Math.PI * b_m * x_m) / (lambda_m * D_m);

            if (beta !== 0) {
                const enveloppe = Math.pow(Math.sin(beta) / beta, 2);
                intensite *= enveloppe;
            }
        }

        positions.push(x.toFixed(2));
        intensites.push(intensite);
    }

    // Calcul du contraste
    const Imax = Math.max(...intensites);
    const Imin = Math.min(...intensites);
    const contraste = ((Imax - Imin) / (Imax + Imin) * 100).toFixed(1);
    document.getElementById('val-contraste').innerText = contraste + ' %';

    scopeChart.data.labels = positions;
    scopeChart.data.datasets[0].data = intensites;
    scopeChart.update();
}

function dessinerSchema() {
    const canvas = diagramCanvas;
    const ctx2d = canvas.getContext('2d');

    // Effacer
    ctx2d.clearRect(0, 0, canvas.width, canvas.height);

    // Échelle
    const centerY = canvas.height / 2;
    const centerX = 100;

    ctx2d.strokeStyle = '#2c3e50';
    ctx2d.fillStyle = '#2c3e50';
    ctx2d.lineWidth = 2;

    if (simState.experience === 'young') {
        // Deux fentes
        ctx2d.fillRect(centerX - 5, centerY - 30, 10, 25);
        ctx2d.fillRect(centerX - 5, centerY + 5, 10, 25);
        ctx2d.clearRect(centerX - 3, centerY - 28, 6, 20);
        ctx2d.clearRect(centerX - 3, centerY + 7, 6, 20);

        // Écran
        ctx2d.fillRect(500, 50, 5, 150);

        // Rayons
        ctx2d.strokeStyle = '#e74c3c';
        ctx2d.setLineDash([5, 5]);
        ctx2d.beginPath();
        ctx2d.moveTo(centerX, centerY - 15);
        ctx2d.lineTo(500, centerY);
        ctx2d.stroke();

        ctx2d.strokeStyle = '#3498db';
        ctx2d.beginPath();
        ctx2d.moveTo(centerX, centerY + 15);
        ctx2d.lineTo(500, centerY);
        ctx2d.stroke();
        ctx2d.setLineDash([]);

    } else if (simState.experience === 'lloyd') {
        // Source
        ctx2d.fillStyle = '#f39c12';
        ctx2d.beginPath();
        ctx2d.arc(centerX, centerY - 30, 8, 0, 2 * Math.PI);
        ctx2d.fill();

        // Miroir
        ctx2d.strokeStyle = '#7f8c8d';
        ctx2d.lineWidth = 4;
        ctx2d.beginPath();
        ctx2d.moveTo(centerX - 50, centerY + 50);
        ctx2d.lineTo(centerX + 300, centerY + 50);
        ctx2d.stroke();

        // Image virtuelle
        ctx2d.fillStyle = 'rgba(243, 156, 18, 0.5)';
        ctx2d.beginPath();
        ctx2d.arc(centerX, centerY + 110, 8, 0, 2 * Math.PI);
        ctx2d.fill();
        ctx2d.setLineDash([3, 3]);
        ctx2d.strokeStyle = '#95a5a6';
        ctx2d.stroke();
        ctx2d.setLineDash([]);

    } else if (simState.experience === 'fresnel_biprisme') {
        // Biprisme
        ctx2d.fillStyle = 'rgba(52, 152, 219, 0.3)';
        ctx2d.beginPath();
        ctx2d.moveTo(centerX + 50, centerY - 40);
        ctx2d.lineTo(centerX + 80, centerY);
        ctx2d.lineTo(centerX + 50, centerY + 40);
        ctx2d.closePath();
        ctx2d.fill();
        ctx2d.stroke();

        // Source
        ctx2d.fillStyle = '#f39c12';
        ctx2d.beginPath();
        ctx2d.arc(centerX, centerY, 6, 0, 2 * Math.PI);
        ctx2d.fill();

    } else if (simState.experience === 'fresnel_miroirs') {
        // Deux miroirs inclinés
        ctx2d.strokeStyle = '#7f8c8d';
        ctx2d.lineWidth = 4;

        const angle = simState.angle_miroirs * Math.PI / 180;

        ctx2d.save();
        ctx2d.translate(centerX + 100, centerY);
        ctx2d.rotate(-angle);
        ctx2d.beginPath();
        ctx2d.moveTo(0, 0);
        ctx2d.lineTo(100, 0);
        ctx2d.stroke();
        ctx2d.restore();

        ctx2d.save();
        ctx2d.translate(centerX + 100, centerY);
        ctx2d.rotate(angle);
        ctx2d.beginPath();
        ctx2d.moveTo(0, 0);
        ctx2d.lineTo(100, 0);
        ctx2d.stroke();
        ctx2d.restore();

        // Source
        ctx2d.fillStyle = '#f39c12';
        ctx2d.beginPath();
        ctx2d.arc(centerX, centerY, 6, 0, 2 * Math.PI);
        ctx2d.fill();
    }

    // Texte
    ctx2d.fillStyle = '#2c3e50';
    ctx2d.font = 'bold 14px Arial';
    ctx2d.fillText(EXPERIENCES[simState.experience].nom, 10, 20);
}

function wavelengthToRGB(wavelength) {
    let r = 0, g = 0, b = 0;

    if (wavelength >= 380 && wavelength < 440) {
        r = -(wavelength - 440) / (440 - 380);
        b = 1.0;
    } else if (wavelength >= 440 && wavelength < 490) {
        g = (wavelength - 440) / (490 - 440);
        b = 1.0;
    } else if (wavelength >= 490 && wavelength < 510) {
        g = 1.0;
        b = -(wavelength - 510) / (510 - 490);
    } else if (wavelength >= 510 && wavelength < 580) {
        r = (wavelength - 510) / (580 - 510);
        g = 1.0;
    } else if (wavelength >= 580 && wavelength < 645) {
        r = 1.0;
        g = -(wavelength - 645) / (645 - 580);
    } else if (wavelength >= 645 && wavelength <= 780) {
        r = 1.0;
    }

    return {
        r: Math.round(r * 255),
        g: Math.round(g * 255),
        b: Math.round(b * 255)
    };
}

function getParametresActuels() {
    return {
        Experience: simState.experience,
        Lambda_nm: simState.lambda,
        Distance_sources_mm: simState.distance_sources.toFixed(2),
        Distance_ecran_mm: simState.distance_ecran
    };
}

function getResultatsActuels() {
    const lambda_m = simState.lambda * 1e-9;
    const a_m = simState.distance_sources * 1e-3;
    const D_m = simState.distance_ecran * 1e-3;
    const interfrange = (lambda_m * D_m / a_m) * 1000;

    return {
        Interfrange_mm: interfrange.toFixed(3),
        Experience: EXPERIENCES[simState.experience].nom
    };
}

initChart();
generateControls();