// ============================================================
// SIMULATION POUSSÉE D'ARCHIMÈDE — LE WELT HYDROSTATIQUE
// Bassine interactif + Treuil + Forces + Graphe temps réel
// Compatible salle_tp.html (EPS Laboratoire)
// ============================================================

const simCanvas = document.createElement('canvas');
simCanvas.id = 'simCanvas';
simCanvas.width = 420;
simCanvas.height = 480;
const simCtx = simCanvas.getContext('2d');

let scopeChart;
let forceChart;

// State
let archState = {
    masse: 10,          // kg
    volume: 5,          // Litres
    rho_fluide: 1000,   // kg/m³
    g: 9.81,            // m/s²
    treuil: 0,          // 0-100%
    liquideColor: '#3b82f6',
    liquideName: 'EAU DOUCE',
    planetName: 'TERRE'
};

// ══════════════════════════════════════════════════
//  GENERATE CONTROLS (compatible salle_tp.html)
// ══════════════════════════════════════════════════
function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <!-- SECTION 1: Objet -->
        <div class="col-12 mb-2">
            <div class="card border-0" style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:12px;">
                <div class="card-body py-2 px-3">
                    <h6 class="fw-bold mb-0" style="font-family:monospace;letter-spacing:3px;font-size:0.7rem;color:#00e1ff;">
                        ⚙ VARIABLES DU BLOC
                    </h6>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <label class="form-label fw-bold small">Masse du bloc <em>m</em></label>
            <input type="range" class="form-range" id="in-masse" min="1" max="50" step="1" value="10" oninput="computeArchimede()">
            <div class="d-flex justify-content-between">
                <small class="text-muted">1 kg</small>
                <span class="badge bg-primary" id="val-masse">10 kg</span>
                <small class="text-muted">50 kg</small>
            </div>
        </div>

        <div class="col-md-4">
            <label class="form-label fw-bold small">Volume du bloc <em>V</em></label>
            <input type="range" class="form-range" id="in-volume" min="1" max="50" step="1" value="5" oninput="computeArchimede()">
            <div class="d-flex justify-content-between">
                <small class="text-muted">1 L</small>
                <span class="badge bg-info" id="val-volume">5 L</span>
                <small class="text-muted">50 L</small>
            </div>
            <div class="text-center mt-1">
                <small class="text-muted" style="font-size:0.65rem;">Densité bloc : <strong id="val-densite-bloc">2.00</strong> kg/L</small>
            </div>
        </div>

        <div class="col-md-4">
            <label class="form-label fw-bold small text-danger">🔧 Treuil (Descente)</label>
            <input type="range" class="form-range" id="in-treuil" min="0" max="100" step="1" value="0" oninput="computeArchimede()" style="accent-color:#ff0055;">
            <div class="d-flex justify-content-between">
                <small class="text-muted">Air</small>
                <span class="badge bg-danger" id="val-treuil">0%</span>
                <small class="text-muted">Fond</small>
            </div>
            <div class="text-center mt-1">
                <small class="text-muted" style="font-size:0.6rem;">Glisser pour plonger le bloc dans la bassine</small>
            </div>
        </div>

        <!-- SECTION 2: Environnement -->
        <div class="col-12 mt-3 mb-2">
            <div class="card border-0" style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:12px;">
                <div class="card-body py-2 px-3">
                    <h6 class="fw-bold mb-0" style="font-family:monospace;letter-spacing:3px;font-size:0.7rem;color:#9d00ff;">
                        🌊 ENVIRONNEMENT
                    </h6>
                </div>
            </div>
        </div>

        <div class="col-md-6">
            <label class="form-label fw-bold small">Fluide (Liquide)</label>
            <select id="in-liquide" class="form-select" onchange="computeArchimede()">
                <option value="1000" data-color="#3b82f6" data-name="EAU DOUCE">🌊 Eau douce (1000 kg/m³)</option>
                <option value="1030" data-color="#0284c7" data-name="EAU DE MER">🌊 Eau de mer (1030 kg/m³)</option>
                <option value="800" data-color="#eab308" data-name="HUILE">🛢️ Huile moteur (800 kg/m³)</option>
                <option value="1420" data-color="#d97706" data-name="MIEL">🍯 Miel (1420 kg/m³)</option>
                <option value="13600" data-color="#94a3b8" data-name="MERCURE">⚗️ Mercure (13600 kg/m³)</option>
                <option value="680" data-color="#a3e635" data-name="ESSENCE">⛽ Essence (680 kg/m³)</option>
                <option value="1260" data-color="#a855f7" data-name="GLYCÉRINE">🧪 Glycérine (1260 kg/m³)</option>
            </select>
        </div>

        <div class="col-md-6">
            <label class="form-label fw-bold small">Planète (Gravité <em>g</em>)</label>
            <select id="in-gravite" class="form-select" onchange="computeArchimede()">
                <option value="9.81" data-name="TERRE">🌍 Terre (g = 9.81 m/s²)</option>
                <option value="1.62" data-name="LUNE">🌙 Lune (g = 1.62 m/s²)</option>
                <option value="3.71" data-name="MARS">🔴 Mars (g = 3.71 m/s²)</option>
                <option value="24.79" data-name="JUPITER">🪐 Jupiter (g = 24.79 m/s²)</option>
                <option value="8.87" data-name="VÉNUS">☀️ Vénus (g = 8.87 m/s²)</option>
                <option value="0" data-name="ISS (0g)">🛰️ ISS - Apesanteur (g = 0 m/s²)</option>
            </select>
        </div>

        <!-- SECTION 3: Télémétrie -->
        <div class="col-12 mt-3">
            <div class="card border-0 shadow-sm" style="background:linear-gradient(135deg,#020617,#0f172a);border:1px solid rgba(0,225,255,0.15);border-radius:14px;">
                <div class="card-body py-3">
                    <div class="row text-center g-2">
                        <div class="col-md-2 col-4">
                            <div class="p-2 rounded" style="background:#020408;border:1px solid #1e293b;">
                                <div style="font-size:0.55rem;color:#64748b;letter-spacing:2px;text-transform:uppercase;">Poids P</div>
                                <div class="fw-bold" style="font-size:1.1rem;color:#ff0055;text-shadow:0 0 8px #ff0055;" id="out-poids">0.0 N</div>
                            </div>
                        </div>
                        <div class="col-md-2 col-4">
                            <div class="p-2 rounded" style="background:#020408;border:1px solid #1e293b;">
                                <div style="font-size:0.55rem;color:#64748b;letter-spacing:2px;text-transform:uppercase;">Poussée F<sub>A</sub></div>
                                <div class="fw-bold" style="font-size:1.1rem;color:#00e1ff;text-shadow:0 0 8px #00e1ff;" id="out-poussee">0.0 N</div>
                            </div>
                        </div>
                        <div class="col-md-2 col-4">
                            <div class="p-2 rounded" style="background:#020408;border:1px solid #1e293b;">
                                <div style="font-size:0.55rem;color:#64748b;letter-spacing:2px;text-transform:uppercase;">Poids Apparent</div>
                                <div class="fw-bold" style="font-size:1.1rem;color:#9d00ff;text-shadow:0 0 8px #9d00ff;" id="out-apparent">0.0 N</div>
                            </div>
                        </div>
                        <div class="col-md-2 col-4">
                            <div class="p-2 rounded" style="background:#020408;border:1px solid #1e293b;">
                                <div style="font-size:0.55rem;color:#64748b;letter-spacing:2px;text-transform:uppercase;">Vol. Déplacé</div>
                                <div class="fw-bold" style="font-size:1.1rem;color:#fff;" id="out-vol-deplace">0.0 L</div>
                            </div>
                        </div>
                        <div class="col-md-2 col-4">
                            <div class="p-2 rounded" style="background:#020408;border:1px solid #1e293b;">
                                <div style="font-size:0.55rem;color:#64748b;letter-spacing:2px;text-transform:uppercase;">Immersion</div>
                                <div class="fw-bold" style="font-size:1.1rem;color:#00ff88;text-shadow:0 0 8px #00ff88;" id="out-immersion">0%</div>
                            </div>
                        </div>
                        <div class="col-md-2 col-4">
                            <div class="p-2 rounded" id="etat-container" style="background:#020408;border:1px solid #1e293b;">
                                <div style="font-size:0.55rem;color:#64748b;letter-spacing:2px;text-transform:uppercase;">État</div>
                                <div class="fw-bold" style="font-size:0.75rem;letter-spacing:1px;" id="out-etat">EN ATTENTE</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- SECTION 4: Canvas simulation + Graphe -->
        <div class="col-md-6 mt-3">
            <div class="card border-0 shadow-sm">
                <div class="card-header py-1 text-white fw-bold" style="background:linear-gradient(135deg,#0f172a,#1e3a5f);font-size:0.75rem;letter-spacing:2px;">
                    🔬 BASSINE — Vue Latérale
                </div>
                <div class="card-body p-2 text-center" style="background:#050b14;" id="sim-canvas-container">
                    <!-- Le canvas sera inséré ici -->
                </div>
            </div>
        </div>

        <div class="col-md-6 mt-3">
            <div class="card border-0 shadow-sm">
                <div class="card-header py-1 text-white fw-bold" style="background:linear-gradient(135deg,#0f172a,#1e3a5f);font-size:0.75rem;letter-spacing:2px;">
                    📈 COURBES — Forces vs Volume Immergé
                </div>
                <div class="card-body p-2" style="background:#020408;min-height:250px;">
                    <canvas id="forceChartCanvas" style="width:100%;height:230px;"></canvas>
                </div>
            </div>
        </div>

        <!-- Formules -->
        <div class="col-12 mt-2">
            <div class="card border-0 bg-light">
                <div class="card-body py-2" style="font-family:monospace;font-size:0.7rem;color:#475569;line-height:1.8;">
                    <strong>Formules d'Archimède :</strong>
                    F<sub>A</sub> = ρ<sub>fluide</sub> · V<sub>immergé</sub> · g &nbsp;│&nbsp;
                    P = m · g &nbsp;│&nbsp;
                    P<sub>apparent</sub> = P − F<sub>A</sub> &nbsp;│&nbsp;
                    Flotte si ρ<sub>bloc</sub> < ρ<sub>fluide</sub> &nbsp;│&nbsp;
                    Équilibre : P = F<sub>A</sub> ⟹ V<sub>imm</sub> = m / ρ<sub>fluide</sub>
                </div>
            </div>
        </div>
    `;

    // Insérer le canvas de simulation
    document.getElementById('sim-canvas-container').appendChild(simCanvas);

    // Init le graphe
    initForceChart();

    // Premier calcul
    computeArchimede();
}

// ══════════════════════════════════════════════════
//  INIT CHART.JS — Profil I(x) principal (scopeCanvas)
// ══════════════════════════════════════════════════
function initChart() {
    const ctx = document.getElementById('scopeCanvas').getContext('2d');
    Chart.defaults.color = '#64748b';
    Chart.defaults.font.family = 'system-ui, sans-serif';

    scopeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Poids Réel P (N)',
                    data: [],
                    borderColor: '#ff0055',
                    borderWidth: 2,
                    borderDash: [6, 4],
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: 'Poussée d\'Archimède FA (N)',
                    data: [],
                    borderColor: '#00e1ff',
                    borderWidth: 3,
                    fill: true,
                    backgroundColor: 'rgba(0, 225, 255, 0.1)',
                    pointRadius: 0
                },
                {
                    label: 'Poids Apparent (N)',
                    data: [],
                    borderColor: '#9d00ff',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false, animation: false,
            scales: {
                x: { title: { display: true, text: 'Volume Immergé (L)', font: { size: 10 } },
                     ticks: { maxTicksLimit: 10, font: { size: 8 } } },
                y: { min: 0,
                     title: { display: true, text: 'Forces (N)', font: { size: 10 } },
                     ticks: { font: { size: 8 } } }
            },
            plugins: { legend: { display: true, labels: { font: { size: 9 } } } }
        }
    });
}

// ══════════════════════════════════════════════════
//  INIT FORCE CHART (dans les controls)
// ══════════════════════════════════════════════════
function initForceChart() {
    const ctx2 = document.getElementById('forceChartCanvas');
    if (!ctx2) return;
    forceChart = new Chart(ctx2.getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Poids P (N)',
                    data: [],
                    borderColor: '#ff0055',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0
                },
                {
                    label: 'Poussée FA (N)',
                    data: [],
                    borderColor: '#00e1ff',
                    borderWidth: 3,
                    fill: true,
                    backgroundColor: 'rgba(0, 225, 255, 0.08)',
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false, animation: false,
            scales: {
                x: { title: { display: true, text: 'V immergé (L)', font: { size: 8 } },
                     ticks: { font: { size: 7 } } },
                y: { min: 0, title: { display: true, text: 'Forces (N)', font: { size: 8 } },
                     ticks: { font: { size: 7 } } }
            },
            plugins: { legend: { position: 'top', labels: { font: { size: 8 } } } }
        }
    });
}

// ══════════════════════════════════════════════════
//  MOTEUR PHYSIQUE
// ══════════════════════════════════════════════════
function computeArchimede() {
    // Lire les paramètres
    const m = parseFloat(document.getElementById('in-masse').value);
    const V = parseFloat(document.getElementById('in-volume').value); // Litres
    const V_m3 = V / 1000;
    const selLiq = document.getElementById('in-liquide');
    const rho_fluide = parseFloat(selLiq.value);
    const liquideColor = selLiq.options[selLiq.selectedIndex].dataset.color || '#3b82f6';
    const liquideName = selLiq.options[selLiq.selectedIndex].dataset.name || 'EAU';
    const selGrav = document.getElementById('in-gravite');
    const g = parseFloat(selGrav.value);
    const planetName = selGrav.options[selGrav.selectedIndex].dataset.name || 'TERRE';
    const treuilPercent = parseFloat(document.getElementById('in-treuil').value) / 100;

    // Stocker
    archState = { masse: m, volume: V, rho_fluide, g, treuil: treuilPercent * 100,
                  liquideColor, liquideName, planetName };

    // Badges UI
    document.getElementById('val-masse').innerText = m + ' kg';
    document.getElementById('val-volume').innerText = V + ' L';
    document.getElementById('val-treuil').innerText = Math.round(treuilPercent * 100) + '%';
    document.getElementById('val-densite-bloc').innerText = (m / V).toFixed(2);

    // ═══ PHYSIQUE ═══
    const rho_bloc = m / V_m3; // kg/m³
    const P = m * g; // Poids réel

    // Volume immergé théorique max (équilibre flottaison)
    let V_imm_eq_m3;
    let etat_theorique = '';

    if (g === 0) {
        V_imm_eq_m3 = 0;
        etat_theorique = 'APESANTEUR';
    } else if (rho_bloc < rho_fluide) {
        V_imm_eq_m3 = m / rho_fluide;
        etat_theorique = 'FLOTTE (Équilibre)';
    } else if (rho_bloc === rho_fluide) {
        V_imm_eq_m3 = V_m3;
        etat_theorique = 'ENTRE DEUX EAUX';
    } else {
        V_imm_eq_m3 = V_m3;
        etat_theorique = 'COULE (Au fond)';
    }

    // Immersion actuelle par le treuil
    let V_imm_actuel = treuilPercent * V_m3;
    let corde_detendue = false;

    if (rho_bloc < rho_fluide && V_imm_actuel > V_imm_eq_m3) {
        V_imm_actuel = V_imm_eq_m3;
        corde_detendue = true;
    }
    // Si plus dense, tout peut s'immerger
    if (V_imm_actuel > V_m3) V_imm_actuel = V_m3;

    // Poussée d'Archimède
    const F_A = rho_fluide * V_imm_actuel * g;

    // Poids apparent
    let P_app = P - F_A;
    if (P_app < 0) P_app = 0;

    // Immersion en %
    const immersionPct = V_m3 > 0 ? Math.round((V_imm_actuel / V_m3) * 100) : 0;

    // ═══ AFFICHAGE DIGITAL ═══
    document.getElementById('out-poids').innerText = P.toFixed(1) + ' N';
    document.getElementById('out-poussee').innerText = F_A.toFixed(1) + ' N';
    document.getElementById('out-apparent').innerText = P_app.toFixed(1) + ' N';
    document.getElementById('out-vol-deplace').innerText = (V_imm_actuel * 1000).toFixed(2) + ' L';
    document.getElementById('out-immersion').innerText = immersionPct + '%';

    // État
    const etatEl = document.getElementById('out-etat');
    const etatBox = document.getElementById('etat-container');
    if (treuilPercent === 0) {
        etatEl.innerText = '🎈 EN SUSPENSION (AIR)';
        etatEl.style.color = '#94a3b8';
        etatBox.style.borderColor = '#334155';
    } else if (g === 0) {
        etatEl.innerText = '🛰️ APESANTEUR — PAS DE POUSSÉE';
        etatEl.style.color = '#fbbf24';
        etatBox.style.borderColor = '#fbbf24';
    } else if (corde_detendue) {
        etatEl.innerText = '🟢 ' + etat_theorique + ' — CORDE DÉTENDUE';
        etatEl.style.color = '#00ff88';
        etatBox.style.borderColor = '#00ff88';
    } else if (V_imm_actuel >= V_m3 - 0.0001) {
        etatEl.innerText = '🔴 ' + etat_theorique;
        etatEl.style.color = '#ff0055';
        etatBox.style.borderColor = '#ff0055';
    } else {
        etatEl.innerText = '⏬ IMMERSION EN COURS...';
        etatEl.style.color = '#fbbf24';
        etatBox.style.borderColor = '#fbbf24';
    }

    // ═══ CANVAS SIMULATION ═══
    drawSimulation(V, V_imm_actuel * 1000, corde_detendue, treuilPercent, liquideColor, P, F_A, g);

    // ═══ GRAPHES ═══
    updateCharts(P, rho_fluide, g, V_m3, V_imm_actuel);
}

// ══════════════════════════════════════════════════
//  CANVAS 2D — BASSINE
// ══════════════════════════════════════════════════
function drawSimulation(volume_bloc, vol_imm_L, corde_detendue, treuil, liquideColor, P, F_A, g) {
    const W = simCanvas.width, H = simCanvas.height;
    simCtx.clearRect(0, 0, W, H);

    // Fond
    simCtx.fillStyle = '#050b14';
    simCtx.fillRect(0, 0, W, H);

    // Grille subtile
    simCtx.strokeStyle = 'rgba(0,225,255,0.03)';
    simCtx.lineWidth = 1;
    for (let x = 0; x < W; x += 30) { simCtx.beginPath(); simCtx.moveTo(x, 0); simCtx.lineTo(x, H); simCtx.stroke(); }
    for (let y = 0; y < H; y += 30) { simCtx.beginPath(); simCtx.moveTo(0, y); simCtx.lineTo(W, y); simCtx.stroke(); }

    // Constantes visuelles
    const bassinX = 80, bassinY = 160, bassinW = 250, bassinH = 260;
    const eauY_base = bassinY + 80;
    const elevation_eau = Math.min(vol_imm_L * 1.8, 60);
    const eauY = eauY_base - elevation_eau;

    // Taille du bloc (proportionnelle au volume)
    const taille_bloc = 35 + volume_bloc * 0.8;
    const blocX = bassinX + bassinW / 2 - taille_bloc / 2;

    // Position du bloc (treuil)
    const base_hook_y = 35;
    const max_descente = bassinY + bassinH - taille_bloc - 15;
    let target_blocY = base_hook_y + 50 + (treuil * (max_descente - base_hook_y - 50));

    if (corde_detendue) {
        const immersion_px = (vol_imm_L / volume_bloc) * taille_bloc;
        target_blocY = eauY - taille_bloc + immersion_px;
    }

    // 1) FLUIDE
    const gradFl = simCtx.createLinearGradient(bassinX, eauY, bassinX, bassinY + bassinH);
    gradFl.addColorStop(0, liquideColor + '66');
    gradFl.addColorStop(1, liquideColor + 'cc');
    simCtx.fillStyle = gradFl;
    simCtx.fillRect(bassinX, eauY, bassinW, bassinY + bassinH - eauY);

    // Surface brillante
    simCtx.beginPath();
    simCtx.moveTo(bassinX, eauY);
    simCtx.lineTo(bassinX + bassinW, eauY);
    simCtx.strokeStyle = liquideColor;
    simCtx.lineWidth = 3;
    simCtx.shadowBlur = 8;
    simCtx.shadowColor = liquideColor;
    simCtx.stroke();
    simCtx.shadowBlur = 0;

    // Petites bulles (si immersion)
    if (vol_imm_L > 0.5) {
        const t = Date.now() / 1000;
        for (let i = 0; i < 6; i++) {
            const bx = bassinX + 40 + Math.sin(t * 2 + i * 1.5) * 80;
            const by = eauY + 20 + ((t * 30 + i * 40) % (bassinY + bassinH - eauY - 20));
            simCtx.beginPath();
            simCtx.arc(bx, by, 2 + Math.sin(t + i) * 1, 0, Math.PI * 2);
            simCtx.fillStyle = 'rgba(255,255,255,0.15)';
            simCtx.fill();
        }
    }

    // 2) BASSINE (verre tech)
    simCtx.beginPath();
    simCtx.moveTo(bassinX, bassinY);
    simCtx.lineTo(bassinX, bassinY + bassinH);
    simCtx.lineTo(bassinX + bassinW, bassinY + bassinH);
    simCtx.lineTo(bassinX + bassinW, bassinY);
    simCtx.strokeStyle = '#94a3b8';
    simCtx.lineWidth = 4;
    simCtx.stroke();

    // Graduations
    for (let i = 0; i <= 5; i++) {
        const yy = bassinY + (i * bassinH / 5);
        simCtx.beginPath();
        simCtx.moveTo(bassinX, yy);
        simCtx.lineTo(bassinX + 12, yy);
        simCtx.strokeStyle = 'rgba(255,255,255,0.2)';
        simCtx.lineWidth = 1;
        simCtx.stroke();
    }

    // 3) SUPPORT + CORDE + DYNAMOMÈTRE
    // Barre du haut
    simCtx.fillStyle = '#334155';
    simCtx.fillRect(130, 20, 150, 10);
    // "Dynamomètre" (cercle)
    simCtx.beginPath();
    simCtx.arc(205, 45, 16, 0, Math.PI * 2);
    simCtx.fillStyle = '#1e293b';
    simCtx.fill();
    simCtx.strokeStyle = '#64748b';
    simCtx.lineWidth = 2;
    simCtx.stroke();
    // Texte dynamomètre
    simCtx.fillStyle = '#00e1ff';
    simCtx.font = 'bold 8px monospace';
    simCtx.textAlign = 'center';
    simCtx.fillText(P > 0 ? (P - F_A).toFixed(0) + 'N' : '0N', 205, 48);

    // Corde
    if (corde_detendue) {
        simCtx.beginPath();
        simCtx.moveTo(205, 61);
        const ctrlX = 205 + treuil * 25;
        simCtx.quadraticCurveTo(ctrlX, (61 + target_blocY) / 2, 205, target_blocY);
        simCtx.strokeStyle = '#475569';
        simCtx.lineWidth = 2;
        simCtx.setLineDash([4, 3]);
        simCtx.stroke();
        simCtx.setLineDash([]);
    } else {
        simCtx.beginPath();
        simCtx.moveTo(205, 61);
        simCtx.lineTo(205, target_blocY);
        simCtx.strokeStyle = '#e2e8f0';
        simCtx.lineWidth = 2;
        simCtx.stroke();
    }

    // 4) BLOC
    const gradBloc = simCtx.createLinearGradient(blocX, target_blocY, blocX + taille_bloc, target_blocY + taille_bloc);
    gradBloc.addColorStop(0, '#334155');
    gradBloc.addColorStop(1, '#1e293b');
    simCtx.fillStyle = gradBloc;
    simCtx.fillRect(blocX, target_blocY, taille_bloc, taille_bloc);
    simCtx.strokeStyle = '#94a3b8';
    simCtx.lineWidth = 2;
    simCtx.strokeRect(blocX, target_blocY, taille_bloc, taille_bloc);

    // Texte sur le bloc
    simCtx.fillStyle = '#fff';
    simCtx.font = 'bold 12px sans-serif';
    simCtx.textAlign = 'center';
    simCtx.fillText(archState.masse + 'kg', blocX + taille_bloc / 2, target_blocY + taille_bloc / 2 + 4);

    // 5) VECTEURS DE FORCE
    const centerBlocX = blocX + taille_bloc / 2;
    const centerBlocY = target_blocY + taille_bloc / 2;

    // Poids (vers le bas) — rouge
    if (P > 0) {
        const pLen = Math.min(Math.max(P * 0.5, 20), 70);
        drawForceArrow(simCtx, centerBlocX - 20, centerBlocY, centerBlocX - 20, centerBlocY + pLen, '#ff0055', 'P');
    }

    // Poussée (vers le haut) — cyan
    if (F_A > 0.1) {
        const faLen = Math.min(Math.max(F_A * 0.5, 15), 70);
        drawForceArrow(simCtx, centerBlocX + 20, centerBlocY, centerBlocX + 20, centerBlocY - faLen, '#00e1ff', 'FA');
    }

    // Légendes
    simCtx.fillStyle = 'rgba(148,163,184,0.5)';
    simCtx.font = '9px monospace';
    simCtx.textAlign = 'left';
    simCtx.fillText(archState.liquideName + ' | ' + archState.planetName, bassinX + 5, bassinY - 5);
}

function drawForceArrow(ctx, fromX, fromY, toX, toY, color, label) {
    const headlen = 10;
    const dx = toX - fromX;
    const dy = toY - fromY;
    const angle = Math.atan2(dy, dx);
    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.lineTo(toX - headlen * Math.cos(angle - Math.PI / 6), toY - headlen * Math.sin(angle - Math.PI / 6));
    ctx.moveTo(toX, toY);
    ctx.lineTo(toX - headlen * Math.cos(angle + Math.PI / 6), toY - headlen * Math.sin(angle + Math.PI / 6));
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.shadowBlur = 6;
    ctx.shadowColor = color;
    ctx.stroke();
    ctx.shadowBlur = 0;

    ctx.fillStyle = color;
    ctx.font = 'bold 11px monospace';
    ctx.textAlign = 'left';
    ctx.fillText(label, toX + 10, toY + 4);
}

// ══════════════════════════════════════════════════
//  GRAPHES
// ══════════════════════════════════════════════════
function updateCharts(Poids, rho, g, V_m3, V_imm_actuel_m3) {
    const max_vol_L = V_m3 * 1000;
    const points = 25;
    const labels = [], dataP = [], dataFA = [], dataPApp = [];

    for (let i = 0; i <= points; i++) {
        const vL = (i / points) * max_vol_L;
        labels.push(vL.toFixed(1));
        dataP.push(Poids);
        const fa = rho * (vL / 1000) * g;
        dataFA.push(fa);
        dataPApp.push(Math.max(Poids - fa, 0));
    }

    const maxForce = Math.max(Poids, rho * V_m3 * g) * 1.2;

    // Chart principal (scopeCanvas)
    if (scopeChart) {
        scopeChart.data.labels = labels;
        scopeChart.data.datasets[0].data = dataP;
        scopeChart.data.datasets[1].data = dataFA;
        scopeChart.data.datasets[2].data = dataPApp;
        scopeChart.options.scales.y.max = maxForce;
        scopeChart.update();
    }

    // Chart secondaire (dans les controls)
    if (forceChart) {
        forceChart.data.labels = labels;
        forceChart.data.datasets[0].data = dataP;
        forceChart.data.datasets[1].data = dataFA;
        forceChart.options.scales.y.max = maxForce;
        forceChart.update();
    }
}

// ══════════════════════════════════════════════════
//  ANIMATION LOOP (bulles dans la bassine)
// ══════════════════════════════════════════════════
let animFrame;
function animateLoop() {
    animFrame = requestAnimationFrame(animateLoop);
    if (archState.treuil > 5) {
        // Redraw uniquement si le treuil est en action
        computeArchimede();
    }
}

// ══════════════════════════════════════════════════
//  API COMPATIBLE salle_tp.html
// ══════════════════════════════════════════════════
function getParametresActuels() {
    return {
        Masse_kg: archState.masse,
        Volume_L: archState.volume,
        Rho_fluide_kgm3: archState.rho_fluide,
        Gravite_ms2: archState.g,
        Treuil_pct: archState.treuil,
        Fluide: archState.liquideName,
        Planete: archState.planetName
    };
}

function getResultatsActuels() {
    const V_m3 = archState.volume / 1000;
    const P = archState.masse * archState.g;
    const treuilPct = archState.treuil / 100;
    let V_imm = treuilPct * V_m3;
    const rho_bloc = archState.masse / V_m3;
    if (rho_bloc < archState.rho_fluide) {
        const V_eq = archState.masse / archState.rho_fluide;
        if (V_imm > V_eq) V_imm = V_eq;
    }
    if (V_imm > V_m3) V_imm = V_m3;

    const FA = archState.rho_fluide * V_imm * archState.g;
    const P_app = Math.max(P - FA, 0);

    return {
        Poids_N: P.toFixed(2),
        Poussee_Archimede_N: FA.toFixed(2),
        Poids_Apparent_N: P_app.toFixed(2),
        Volume_Deplace_L: (V_imm * 1000).toFixed(3),
        Densite_bloc_kgL: (archState.masse / archState.volume).toFixed(2),
        Flotte: rho_bloc < archState.rho_fluide ? 'Oui' : 'Non',
        Fluide: archState.liquideName,
        Planete: archState.planetName
    };
}

// ══════════════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════════════
initChart();
generateControls();

