// ============================================================
// SIMULATION OPTIQUE ONDULATOIRE — LE WELT ENGINE v2
// Fusion: ancien moteur EPS + nouveau moteur Welt Quantum Lab
// Young, Lloyd, Fresnel (biprisme + miroirs), Billet, Meslin
// + Vue 3D Three.js + Analyse Fourier + Banc Optique 2D avancé
// ============================================================

/* ════════════════════════════════════════════════
   STATE GLOBAL
════════════════════════════════════════════════ */
let simState = {
    experience: 'young',
    lambda: 532,
    distance_sources: 0.5,
    distance_ecran: 1000,
    largeur_fente: 0.1,
    angle_biprisme: 1,
    angle_miroirs: 0.5,
    // Nouveaux paramètres Welt
    n: 1.0,        // indice milieu
    V: 1.0,        // visibilité / cohérence
    ratio: 1.0,    // I1/I2
    z: 2.0,        // distance écran 3D
    nHarm: 8,      // harmoniques Fourier
    win: 0,        // fenêtrage Hann
    // Données calculées
    xs: [], Is: [], phi0: 0,
    I1: 1, I2: 1, Imax: 4, Imin: 0,
    lam_eff: 532, i_mm: 0,
    laserColor: 'rgb(0,229,255)'
};

let scopeChart, diagramCanvas;
let currentView = '2d';

const EXPERIENCES = {
    'young': {
        nom: '👥 Fentes de Young',
        description: 'Deux fentes parallèles éclairées par une source monochromatique',
        welt: 'young', nb_sources: 2
    },
    'lloyd': {
        nom: '🪞 Miroir de Lloyd',
        description: 'Source + image virtuelle par réflexion sur un miroir plan (Δφ=π)',
        welt: 'lloyd', nb_sources: 2
    },
    'fresnel_biprisme': {
        nom: '🔺 Biprisme de Fresnel',
        description: 'Deux prismes accolés créent deux sources virtuelles',
        welt: 'biprism', nb_sources: 2
    },
    'fresnel_miroirs': {
        nom: '🪞🪞 Miroirs de Fresnel',
        description: 'Deux miroirs plans inclinés créent deux sources virtuelles',
        welt: 'biprism', nb_sources: 2
    },
    'billet': {
        nom: '⚡ Bilentille de Billet',
        description: 'Lentille coupée en deux formant deux images',
        welt: 'billet', nb_sources: 2
    },
    'meslin': {
        nom: '🔲 Semi-Lentilles de Meslin',
        description: 'Deux demi-lentilles avec cohérence partielle — anneaux',
        welt: 'meslin', nb_sources: 2
    }
};

/* ════════════════════════════════════════════════
   UTILS
════════════════════════════════════════════════ */
function wavelengthToRGB(wl) {
    let r=0, g=0, b=0;
    if(wl>=380&&wl<440){r=-(wl-440)/60;g=0;b=1;}
    else if(wl>=440&&wl<490){r=0;g=(wl-440)/50;b=1;}
    else if(wl>=490&&wl<510){r=0;g=1;b=-(wl-510)/20;}
    else if(wl>=510&&wl<580){r=(wl-510)/70;g=1;b=0;}
    else if(wl>=580&&wl<645){r=1;g=-(wl-645)/65;b=0;}
    else if(wl>=645&&wl<=780){r=1;g=0;b=0;}
    let f = wl<420?0.3+0.7*(wl-380)/40 : wl<=700?1 : 0.3+0.7*(750-wl)/50;
    return {
        r: Math.round(r*f*255),
        g: Math.round(g*f*255),
        b: Math.round(b*f*255),
        css: `rgb(${Math.round(r*f*255)},${Math.round(g*f*255)},${Math.round(b*f*255)})`
    };
}

/* ════════════════════════════════════════════════
   GENERATE CONTROLS (compatible avec salle_tp.html)
════════════════════════════════════════════════ */
function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-12 mb-3">
            <label class="form-label fw-bold">Expérience d'interférences</label>
            <select id="experience" class="form-select" onchange="changerExperience()">
                ${Object.keys(EXPERIENCES).map(key =>
                    `<option value="${key}">${EXPERIENCES[key].nom}</option>`
                ).join('')}
            </select>
            <div class="alert alert-info mt-2 mb-0 small" id="description-exp">
                ${EXPERIENCES['young'].description}
            </div>
        </div>

        <div class="col-md-3">
            <label class="form-label fw-bold">Longueur d'onde λ (nm)</label>
            <input type="range" class="form-range" id="lambda" min="380" max="750" value="532" step="1" oninput="updateSim()">
            <div class="text-center">
                <span id="val-lambda" class="badge" style="background:rgb(0,229,0)">532 nm</span>
            </div>
        </div>

        <div class="col-md-3" id="container-distance-sources">
            <label class="form-label fw-bold">Distance sources a (mm)</label>
            <input type="range" class="form-range" id="distance_sources" min="0.1" max="5" value="1.0" step="0.05" oninput="updateSim()">
            <div class="text-center"><span id="val-a" class="badge bg-primary">1.00 mm</span></div>
        </div>

        <div class="col-md-3">
            <label class="form-label fw-bold">Distance écran D (m)</label>
            <input type="range" class="form-range" id="distance_ecran" min="500" max="5000" value="2000" step="100" oninput="updateSim()">
            <div class="text-center"><span id="val-d" class="badge bg-secondary">2.0 m</span></div>
        </div>

        <div class="col-md-3" id="container-param-specifique"></div>

        <!-- Paramètres Welt avancés -->
        <div class="col-12 mt-2">
            <div class="card border-0 bg-light">
                <div class="card-body py-2">
                    <div class="row g-2 align-items-center">
                        <div class="col-md-3">
                            <label class="form-label small fw-bold mb-0">Milieu</label>
                            <select id="in-n" class="form-select form-select-sm" onchange="updateSim()">
                                <option value="1.00">Air (n=1.00)</option>
                                <option value="1.33">Eau (n=1.33)</option>
                                <option value="1.50">Verre (n=1.50)</option>
                                <option value="2.42">Diamant (n=2.42)</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label small fw-bold mb-0">Visibilité V</label>
                            <div class="d-flex align-items-center gap-1">
                                <input type="range" class="form-range" id="in-V" min="0" max="1" step="0.01" value="1" oninput="updateSim()">
                                <span class="badge bg-danger" id="v-V" style="min-width:42px">100%</span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label small fw-bold mb-0">I₁/I₂</label>
                            <div class="d-flex align-items-center gap-1">
                                <input type="range" class="form-range" id="in-ratio" min="0.1" max="1.0" step="0.05" value="1.0" oninput="updateSim()">
                                <span class="badge bg-info" id="v-ratio" style="min-width:42px">1.00</span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label small fw-bold mb-0">N Harm. Fourier</label>
                            <div class="d-flex align-items-center gap-1">
                                <input type="range" class="form-range" id="in-nharm" min="1" max="20" step="1" value="8" oninput="computeFFT()">
                                <span class="badge bg-dark" id="v-nharm" style="min-width:32px">8</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Résultats -->
        <div class="col-12 mt-3">
            <div class="card border-0 shadow-sm">
                <div class="card-header text-white fw-bold" style="background: linear-gradient(135deg, #0f172a, #1e3a5f);">
                    📊 Télémétrie Quantique
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-md-2 col-4">
                            <h5 class="text-primary fw-900 mb-0" id="val-interfrange">—</h5>
                            <small class="text-muted" style="font-size:0.65rem">Interfrange i</small>
                        </div>
                        <div class="col-md-2 col-4">
                            <h5 class="text-success fw-900 mb-0" id="val-ordre-max">—</h5>
                            <small class="text-muted" style="font-size:0.65rem">Ordre Max</small>
                        </div>
                        <div class="col-md-2 col-4">
                            <h5 class="text-warning fw-900 mb-0" id="val-contraste">—</h5>
                            <small class="text-muted" style="font-size:0.65rem">Contraste V</small>
                        </div>
                        <div class="col-md-2 col-4">
                            <h5 class="text-danger fw-900 mb-0" id="val-Imax">—</h5>
                            <small class="text-muted" style="font-size:0.65rem">I_max</small>
                        </div>
                        <div class="col-md-2 col-4">
                            <h5 class="fw-900 mb-0" style="color:#b8860b" id="val-Imin">—</h5>
                            <small class="text-muted" style="font-size:0.65rem">I_min</small>
                        </div>
                        <div class="col-md-2 col-4">
                            <h5 class="fw-900 mb-0 text-info" id="val-phi0">—</h5>
                            <small class="text-muted" style="font-size:0.65rem">Saut φ₀</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Schéma du dispositif (ancien) + Bande spectrale -->
        <div class="col-12 mt-3">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-dark text-white fw-bold">
                    🔬 Banc Optique — Vue de Dessus
                </div>
                <div class="card-body p-2" style="background: #010208;">
                    <canvas id="diagramCanvas" width="700" height="220" style="width:100%;border-radius:8px;"></canvas>
                </div>
            </div>
        </div>

        <!-- Bande longueur d'onde -->
        <div class="col-12 mt-2">
            <div style="height:16px;border-radius:4px;background:linear-gradient(to right,#8b00ff,#0000ff,#00cfff,#00ff00,#ffff00,#ff7f00,#ff0000);opacity:.75;border:1px solid rgba(0,0,0,.1);"></div>
        </div>

        <!-- Formules -->
        <div class="col-12 mt-2">
            <div class="card border-0 bg-light">
                <div class="card-body py-2" style="font-family:monospace;font-size:0.75rem;color:#475569;line-height:1.8;">
                    <strong>Formules :</strong>
                    i = λ·D / (n·a) &nbsp;│&nbsp;
                    δ = a·x / D &nbsp;│&nbsp;
                    Δφ = 2π·δ/λ' + φ₀ &nbsp;│&nbsp;
                    I = I₁+I₂+2√(I₁I₂)·V·cos(Δφ) &nbsp;│&nbsp;
                    F{I}(ν) = ∫ I(x)·e^(-2πiνx) dx
                </div>
            </div>
        </div>
    `;

    diagramCanvas = document.getElementById('diagramCanvas');
    changerExperience();
}

/* ════════════════════════════════════════════════
   CHANGE EXPERIENCE
════════════════════════════════════════════════ */
function changerExperience() {
    simState.experience = document.getElementById('experience').value;
    const exp = EXPERIENCES[simState.experience];
    document.getElementById('description-exp').innerText = exp.description;

    const containerParam = document.getElementById('container-param-specifique');

    if (simState.experience === 'fresnel_biprisme') {
        containerParam.innerHTML = `
            <label class="form-label fw-bold">Angle biprisme (°)</label>
            <input type="range" class="form-range" id="angle_biprisme" min="0.5" max="5" value="1" step="0.1" oninput="updateSim()">
            <div class="text-center"><span id="val-angle-bi" class="badge bg-info">1°</span></div>
        `;
    } else if (simState.experience === 'fresnel_miroirs') {
        containerParam.innerHTML = `
            <label class="form-label fw-bold">Angle miroirs (°)</label>
            <input type="range" class="form-range" id="angle_miroirs" min="0.1" max="2" value="0.5" step="0.1" oninput="updateSim()">
            <div class="text-center"><span id="val-angle-mir" class="badge bg-info">0.5°</span></div>
        `;
    } else if (simState.experience === 'lloyd') {
        containerParam.innerHTML = `
            <label class="form-label fw-bold">Hauteur source (mm)</label>
            <input type="range" class="form-range" id="hauteur_lloyd" min="0.5" max="5" value="2" step="0.5" oninput="updateSim()">
            <div class="text-center"><span id="val-lloyd" class="badge bg-info">2 mm</span></div>
        `;
    } else if (simState.experience === 'meslin') {
        containerParam.innerHTML = `
            <label class="form-label fw-bold">Largeur fente (mm)</label>
            <input type="range" class="form-range" id="largeur_meslin" min="0.1" max="1" value="0.3" step="0.05" oninput="updateSim()">
            <div class="text-center"><span id="val-meslin" class="badge bg-info">0.3 mm</span></div>
        `;
    } else {
        containerParam.innerHTML = '';
    }

    updateSim();
}

/* ════════════════════════════════════════════════
   UPDATE SIM — MOTEUR PHYSIQUE COMPLET WELT
════════════════════════════════════════════════ */
function updateSim() {
    // Lire tous les paramètres
    simState.lambda = parseFloat(document.getElementById('lambda').value);
    simState.distance_sources = parseFloat(document.getElementById('distance_sources').value);
    simState.distance_ecran = parseFloat(document.getElementById('distance_ecran').value);
    simState.n = parseFloat(document.getElementById('in-n').value);
    simState.V = parseFloat(document.getElementById('in-V').value);
    simState.ratio = parseFloat(document.getElementById('in-ratio').value);

    // Paramètres spécifiques anciens
    if (simState.experience === 'fresnel_biprisme') {
        simState.angle_biprisme = parseFloat(document.getElementById('angle_biprisme').value);
        document.getElementById('val-angle-bi').innerText = simState.angle_biprisme + '°';
        const n = 1.5;
        const alpha_rad = simState.angle_biprisme * Math.PI / 180;
        simState.distance_sources = 2 * (n - 1) * alpha_rad * simState.distance_ecran / 2;
    } else if (simState.experience === 'fresnel_miroirs') {
        simState.angle_miroirs = parseFloat(document.getElementById('angle_miroirs').value);
        document.getElementById('val-angle-mir').innerText = simState.angle_miroirs + '°';
        const alpha_rad = simState.angle_miroirs * Math.PI / 180;
        simState.distance_sources = 2 * 50 * Math.sin(alpha_rad);
    } else if (simState.experience === 'lloyd') {
        const hauteur = parseFloat(document.getElementById('hauteur_lloyd').value);
        document.getElementById('val-lloyd').innerText = hauteur + ' mm';
        simState.distance_sources = 2 * hauteur;
    } else if (simState.experience === 'meslin') {
        simState.largeur_fente = parseFloat(document.getElementById('largeur_meslin').value);
        document.getElementById('val-meslin').innerText = simState.largeur_fente + ' mm';
    }

    // Couleur spectrale
    const col = wavelengthToRGB(simState.lambda);
    simState.laserColor = col.css;

    // UI badges
    const lamBadge = document.getElementById('val-lambda');
    lamBadge.style.background = col.css;
    lamBadge.style.color = (simState.lambda > 550 && simState.lambda < 620) ? '#000' : '#fff';
    lamBadge.innerText = simState.lambda + ' nm';
    document.getElementById('val-a').innerText = simState.distance_sources.toFixed(2) + ' mm';
    document.getElementById('val-d').innerText = (simState.distance_ecran / 1000).toFixed(1) + ' m';
    document.getElementById('v-V').innerText = Math.round(simState.V * 100) + '%';
    document.getElementById('v-ratio').innerText = simState.ratio.toFixed(2);

    // ════ PHYSIQUE WELT ════
    const lam_eff = simState.lambda / simState.n; // nm effectif dans le milieu
    const a_mm = simState.distance_sources;
    const D_m = simState.distance_ecran / 1000;
    const phi0 = simState.experience === 'lloyd' ? Math.PI : 0;
    const I1 = 1.0, I2 = simState.ratio;
    const Imax = I1 + I2 + 2 * Math.sqrt(I1 * I2) * simState.V;
    const Imin = I1 + I2 - 2 * Math.sqrt(I1 * I2) * simState.V;

    // Interfrange
    let i_mm = (simState.experience !== 'meslin')
        ? (lam_eff * 1e-6 * D_m) / (a_mm * 1e-3)
        : 0;

    // Stocker
    simState.phi0 = phi0;
    simState.I1 = I1; simState.I2 = I2;
    simState.Imax = Imax; simState.Imin = Imin;
    simState.lam_eff = lam_eff;
    simState.i_mm = i_mm;

    // Signal
    const N = 512;
    const xs = [], Is = [];
    for (let k = 0; k < N; k++) {
        const x = -5 + 10 * k / (N - 1); // mm
        xs.push(x);
        let dph;
        if (simState.experience !== 'meslin') {
            const delta = (a_mm * 1e-3 * x * 1e-3) / D_m;
            dph = 2 * Math.PI * delta / (lam_eff * 1e-9) + phi0;
        } else {
            const z1 = D_m + a_mm / 2000, z2 = D_m - a_mm / 2000;
            const delta = (a_mm * 1e-3) + (Math.pow(x * 1e-3, 2) / 2) * (1 / z1 - 1 / z2);
            dph = 2 * Math.PI * delta / (lam_eff * 1e-9);
        }
        let I = I1 + I2 + 2 * Math.sqrt(I1 * I2) * simState.V * Math.cos(dph);

        // Enveloppe diffraction pour Meslin
        if (simState.experience === 'meslin' && simState.largeur_fente > 0) {
            const b_m = simState.largeur_fente * 1e-3;
            const beta = (Math.PI * b_m * x * 1e-3) / (simState.lambda * 1e-9 * D_m);
            if (beta !== 0) I *= Math.pow(Math.sin(beta) / beta, 2);
        }

        // Lloyd: pas de franges côté miroir
        if (simState.experience === 'lloyd' && x < 0) I = I1;

        Is.push(I);
    }
    simState.xs = xs;
    simState.Is = Is;

    // Ordre max visible
    const ordre_max = i_mm > 0 ? Math.floor(5 / i_mm) : 0;

    // Affichage Télémétrie
    document.getElementById('val-interfrange').innerText =
        simState.experience === 'meslin' ? 'Anneaux' : i_mm.toFixed(3) + ' mm';
    document.getElementById('val-ordre-max').innerText = ordre_max || '—';
    document.getElementById('val-contraste').innerText = simState.V.toFixed(2);
    document.getElementById('val-Imax').innerText = Imax.toFixed(2) + ' I₀';
    document.getElementById('val-Imin').innerText = Imin.toFixed(2) + ' I₀';
    document.getElementById('val-phi0').innerText = phi0 === 0 ? '0 rad' : 'π rad';

    // Dessiner
    updateSigChart();
    dessinerBancOptique();
    computeFFT();
}

/* ════════════════════════════════════════════════
   CHART: Profil I(x) — Chart.js
════════════════════════════════════════════════ */
function initChart() {
    const ctx = document.getElementById('scopeCanvas').getContext('2d');
    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'I(x)', data: [],
                    borderColor: '#00e5ff', borderWidth: 2,
                    fill: true, backgroundColor: 'rgba(0,229,255,0.12)',
                    pointRadius: 0, tension: 0.3
                },
                {
                    label: 'Enveloppe', data: [],
                    borderColor: 'rgba(255,170,0,0.5)', borderWidth: 1,
                    borderDash: [4, 3], pointRadius: 0, fill: false
                }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false, animation: false,
            scales: {
                x: { title: { display: true, text: 'Position x (mm)', font: { size: 10 } },
                     ticks: { maxTicksLimit: 10, font: { size: 8 } } },
                y: { min: 0, max: 4.5,
                     title: { display: true, text: 'Intensité I / I₀', font: { size: 10 } },
                     ticks: { font: { size: 8 } } }
            },
            plugins: { legend: { display: true, labels: { font: { size: 9 } } } }
        }
    });
}

function updateSigChart() {
    if (!scopeChart) return;
    const c = simState.laserColor;
    const env = simState.xs.map(() => simState.Imax);
    scopeChart.data.labels = simState.xs;
    scopeChart.data.datasets[0].data = simState.Is;
    scopeChart.data.datasets[0].borderColor = c;
    scopeChart.data.datasets[0].backgroundColor = c.replace('rgb', 'rgba').replace(')', ',0.1)');
    scopeChart.data.datasets[1].data = env;
    scopeChart.options.scales.y.max = Math.max(simState.Imax * 1.15, 2);
    scopeChart.update();
}

/* ════════════════════════════════════════════════
   BANC OPTIQUE 2D — Canvas avancé style Welt
════════════════════════════════════════════════ */
function dessinerBancOptique() {
    const canvas = diagramCanvas;
    if (!canvas) return;
    const W = canvas.width, H = canvas.height;
    const ctx2d = canvas.getContext('2d');
    ctx2d.clearRect(0, 0, W, H);

    const col = wavelengthToRGB(simState.lambda);
    const c = col.css;
    const d = simState.experience;
    const srcX = 60, scrX = W - 50, cY = H / 2;
    const gap = Math.max(simState.distance_sources * 18, 10);

    // Grille
    ctx2d.strokeStyle = 'rgba(0,229,255,0.04)'; ctx2d.lineWidth = 1;
    for (let x = 0; x < W; x += 30) { ctx2d.beginPath(); ctx2d.moveTo(x, 0); ctx2d.lineTo(x, H); ctx2d.stroke(); }
    for (let y = 0; y < H; y += 30) { ctx2d.beginPath(); ctx2d.moveTo(0, y); ctx2d.lineTo(W, y); ctx2d.stroke(); }

    // Axe optique
    ctx2d.strokeStyle = 'rgba(100,116,139,0.4)'; ctx2d.lineWidth = 1; ctx2d.setLineDash([6, 4]);
    ctx2d.beginPath(); ctx2d.moveTo(0, cY); ctx2d.lineTo(W, cY); ctx2d.stroke();
    ctx2d.setLineDash([]);

    const alpha = c.replace('rgb', 'rgba').replace(')', '');

    if (d === 'young' || d === 'fresnel_biprisme' || d === 'fresnel_miroirs' || d === 'billet') {
        const s1Y = cY - gap / 2, s2Y = cY + gap / 2;

        if (d === 'young') {
            ctx2d.fillStyle = 'rgba(100,116,139,0.5)';
            ctx2d.fillRect(W * 0.38 - 3, 0, 6, s1Y - 12);
            ctx2d.fillRect(W * 0.38 - 3, s1Y + 12, 6, (s2Y - s1Y) - 24);
            ctx2d.fillRect(W * 0.38 - 3, s2Y + 12, 6, H);
        } else if (d === 'fresnel_biprisme') {
            ctx2d.beginPath();
            ctx2d.moveTo(W * 0.35, cY); ctx2d.lineTo(W * 0.35 + 28, cY - 40); ctx2d.lineTo(W * 0.35 + 28, cY + 40); ctx2d.closePath();
            ctx2d.fillStyle = 'rgba(100,180,255,0.08)'; ctx2d.fill();
            ctx2d.strokeStyle = '#94a3b8'; ctx2d.lineWidth = 1.5; ctx2d.stroke();
        } else if (d === 'fresnel_miroirs') {
            const ang = simState.angle_miroirs * Math.PI / 180;
            ctx2d.strokeStyle = '#e2e8f0'; ctx2d.lineWidth = 3;
            ctx2d.save(); ctx2d.translate(W * 0.35, cY); ctx2d.rotate(-ang);
            ctx2d.beginPath(); ctx2d.moveTo(0, 0); ctx2d.lineTo(80, 0); ctx2d.stroke(); ctx2d.restore();
            ctx2d.save(); ctx2d.translate(W * 0.35, cY); ctx2d.rotate(ang);
            ctx2d.beginPath(); ctx2d.moveTo(0, 0); ctx2d.lineTo(80, 0); ctx2d.stroke(); ctx2d.restore();
            ctx2d.fillStyle = 'rgba(226,232,240,0.5)'; ctx2d.font = 'bold 8px sans-serif';
            ctx2d.fillText('M₁', W * 0.35 + 35, cY - 12); ctx2d.fillText('M₂', W * 0.35 + 35, cY + 18);
        }

        // Cônes lumineux
        [s1Y, s2Y].forEach((sy, i) => {
            const gr = ctx2d.createLinearGradient(srcX, sy, scrX, cY);
            gr.addColorStop(0, `${alpha},0.35)`);
            gr.addColorStop(1, `${alpha},0)`);
            ctx2d.beginPath();
            ctx2d.moveTo(srcX, sy);
            ctx2d.lineTo(scrX, cY - (45 + i * 6));
            ctx2d.lineTo(scrX, cY + (45 - i * 6));
            ctx2d.closePath();
            ctx2d.fillStyle = gr; ctx2d.fill();
            // Point source
            ctx2d.beginPath(); ctx2d.arc(srcX, sy, 5, 0, Math.PI * 2);
            ctx2d.fillStyle = c; ctx2d.shadowBlur = 10; ctx2d.shadowColor = c; ctx2d.fill();
            ctx2d.shadowBlur = 0;
        });

    } else if (d === 'lloyd') {
        const s1Y = cY - gap / 2;
        ctx2d.beginPath(); ctx2d.arc(srcX, s1Y, 5, 0, Math.PI * 2);
        ctx2d.fillStyle = c; ctx2d.shadowBlur = 10; ctx2d.shadowColor = c; ctx2d.fill(); ctx2d.shadowBlur = 0;
        // Miroir
        ctx2d.strokeStyle = '#e2e8f0'; ctx2d.lineWidth = 3;
        ctx2d.beginPath(); ctx2d.moveTo(100, cY); ctx2d.lineTo(scrX - 50, cY); ctx2d.stroke();
        ctx2d.fillStyle = 'rgba(226,232,240,0.5)'; ctx2d.font = 'bold 9px sans-serif';
        ctx2d.fillText('MIROIR', 110, cY - 6);
        // Rayon direct
        ctx2d.strokeStyle = c; ctx2d.lineWidth = 1.5;
        ctx2d.beginPath(); ctx2d.moveTo(srcX, s1Y); ctx2d.lineTo(scrX, cY - 35); ctx2d.stroke();
        // Rayon réfléchi
        ctx2d.setLineDash([5, 4]);
        ctx2d.beginPath(); ctx2d.moveTo(srcX, s1Y); ctx2d.lineTo(W * 0.5, cY); ctx2d.lineTo(scrX, cY + 35); ctx2d.stroke();
        ctx2d.setLineDash([]);
        ctx2d.fillStyle = 'rgba(255,45,94,0.8)'; ctx2d.font = 'bold 9px sans-serif';
        ctx2d.fillText('Δφ=π', W * 0.5 + 6, cY + 16);

    } else if (d === 'meslin') {
        ctx2d.strokeStyle = 'rgba(100,180,255,0.6)'; ctx2d.lineWidth = 2;
        ctx2d.beginPath(); ctx2d.ellipse(W * 0.4, cY - 20, 18, 36, 0, 0, Math.PI * 2); ctx2d.stroke();
        ctx2d.beginPath(); ctx2d.ellipse(W * 0.4 + 40, cY + 20, 18, 36, 0, 0, Math.PI * 2); ctx2d.stroke();
        ctx2d.fillStyle = 'rgba(100,180,255,0.06)';
        ctx2d.beginPath(); ctx2d.ellipse(W * 0.4, cY - 20, 18, 36, 0, 0, Math.PI * 2); ctx2d.fill();
        ctx2d.beginPath(); ctx2d.ellipse(W * 0.4 + 40, cY + 20, 18, 36, 0, 0, Math.PI * 2); ctx2d.fill();
        ctx2d.fillStyle = 'rgba(100,180,255,0.5)'; ctx2d.font = 'bold 8px sans-serif';
        ctx2d.fillText('L₁', W * 0.4 - 6, cY - 16); ctx2d.fillText('L₂', W * 0.4 + 34, cY + 24);
        // Source unique
        ctx2d.beginPath(); ctx2d.arc(srcX, cY, 6, 0, Math.PI * 2);
        ctx2d.fillStyle = c; ctx2d.shadowBlur = 12; ctx2d.shadowColor = c; ctx2d.fill(); ctx2d.shadowBlur = 0;
        const gr = ctx2d.createLinearGradient(srcX, cY, scrX, cY);
        gr.addColorStop(0, `${alpha},0.3)`); gr.addColorStop(1, `${alpha},0)`);
        ctx2d.beginPath(); ctx2d.moveTo(srcX, cY); ctx2d.lineTo(scrX, cY - 50); ctx2d.lineTo(scrX, cY + 50); ctx2d.closePath();
        ctx2d.fillStyle = gr; ctx2d.fill();
    }

    // Écran
    ctx2d.strokeStyle = 'rgba(148,163,184,0.7)'; ctx2d.lineWidth = 5; ctx2d.lineCap = 'round';
    ctx2d.beginPath(); ctx2d.moveTo(scrX, 15); ctx2d.lineTo(scrX, H - 15); ctx2d.stroke();
    ctx2d.fillStyle = 'rgba(148,163,184,0.5)'; ctx2d.font = 'bold 9px sans-serif';
    ctx2d.fillText('ÉCRAN', scrX - 32, 12);

    // Franges sur l'écran
    const pH = H - 30;
    for (let y = 0; y < pH; y++) {
        const idx = Math.round(y / pH * (simState.Is.length - 1));
        const iv = simState.Is[idx] || 1;
        const brt = Math.min(iv / simState.Imax, 1);
        ctx2d.fillStyle = `rgba(${col.r},${col.g},${col.b},${brt * 0.8})`;
        ctx2d.fillRect(scrX + 6, 15 + y, 14, 1);
    }

    // Nom du dispositif
    ctx2d.fillStyle = 'rgba(0,229,255,0.7)'; ctx2d.font = 'bold 10px sans-serif';
    ctx2d.fillText(EXPERIENCES[simState.experience].nom, 10, 16);
}

/* ════════════════════════════════════════════════
   FOURIER ANALYSIS (DFT)
════════════════════════════════════════════════ */
let fftChart;

function dft(signal) {
    const N = signal.length;
    const Re = new Array(N).fill(0);
    const Im = new Array(N).fill(0);
    for (let k = 0; k < N; k++) {
        for (let n = 0; n < N; n++) {
            const ang = 2 * Math.PI * k * n / N;
            Re[k] += signal[n] * Math.cos(ang);
            Im[k] -= signal[n] * Math.sin(ang);
        }
        Re[k] /= N; Im[k] /= N;
    }
    return { Re, Im };
}

function idft(Re, Im, nHarm) {
    const N = Re.length;
    const out = new Array(N).fill(0);
    for (let n = 0; n < N; n++) {
        for (let k = 0; k < Math.min(nHarm, N); k++) {
            const ang = 2 * Math.PI * k * n / N;
            out[n] += Re[k] * Math.cos(ang) - Im[k] * Math.sin(ang);
        }
        for (let k = N - Math.min(nHarm, N); k < N; k++) {
            const ang = 2 * Math.PI * k * n / N;
            out[n] += Re[k] * Math.cos(ang) - Im[k] * Math.sin(ang);
        }
    }
    return out;
}

function computeFFT() {
    const nhEl = document.getElementById('in-nharm');
    if (!nhEl) return;
    const nH = parseInt(nhEl.value);
    document.getElementById('v-nharm').textContent = nH;

    if (!simState.Is || simState.Is.length < 4) return;

    // Downsample pour vitesse
    const Nd = 128;
    const step = Math.floor(simState.Is.length / Nd);
    const sub = [];
    for (let i = 0; i < Nd; i++) sub.push(simState.Is[i * step] || 0);

    const { Re, Im } = dft(sub);
    const mod = Re.map((r, i) => Math.sqrt(r * r + Im[i] * Im[i]));
    const rec = idft(Re, Im, nH);

    // Si pas de canvas FFT dédié, ne rien faire (le chart principal suffit)
    // En mode salle_tp, on overlay la reconstruction sur le chart principal
    if (scopeChart && scopeChart.data.datasets.length >= 2) {
        // Upscale reconstruction vers N=512
        const recFull = [];
        for (let i = 0; i < simState.Is.length; i++) {
            const srcIdx = Math.min(Math.floor(i / step), Nd - 1);
            recFull.push(rec[srcIdx]);
        }

        // Ajouter ou mettre à jour le dataset reconstruction
        if (scopeChart.data.datasets.length < 3) {
            scopeChart.data.datasets.push({
                label: 'Reconstruction (' + nH + ' harm.)',
                data: recFull,
                borderColor: 'rgba(0,255,159,0.6)',
                borderWidth: 1.5,
                borderDash: [3, 2],
                pointRadius: 0, fill: false
            });
        } else {
            scopeChart.data.datasets[2].data = recFull;
            scopeChart.data.datasets[2].label = 'Reconstruction (' + nH + ' harm.)';
        }
        scopeChart.update();
    }
}

/* ════════════════════════════════════════════════
   API: getParametresActuels / getResultatsActuels
   (compatibilité avec salle_tp.html)
════════════════════════════════════════════════ */
function getParametresActuels() {
    return {
        Experience: simState.experience,
        Lambda_nm: simState.lambda,
        Distance_sources_mm: simState.distance_sources.toFixed(2),
        Distance_ecran_mm: simState.distance_ecran,
        Indice_milieu: simState.n,
        Visibilite: simState.V,
        Ratio_I1_I2: simState.ratio,
        Dispositif: EXPERIENCES[simState.experience].nom
    };
}

function getResultatsActuels() {
    return {
        Interfrange_mm: simState.i_mm > 0 ? simState.i_mm.toFixed(3) : 'Anneaux',
        I_max: simState.Imax.toFixed(2),
        I_min: simState.Imin.toFixed(2),
        Contraste: simState.V.toFixed(2),
        Saut_phase: simState.phi0 === 0 ? '0' : 'π',
        Experience: EXPERIENCES[simState.experience].nom
    };
}

/* ════════════════════════════════════════════════
   INIT
════════════════════════════════════════════════ */
initChart();
generateControls();

