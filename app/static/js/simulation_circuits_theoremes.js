// ============================================================
// SIMULATION THÉORÈMES DES CIRCUITS ÉLECTRIQUES
// Superposition, Thévenin, Norton, Millman, Kirchhoff
// Assistant KAYT
// ============================================================

const ctx = document.getElementById('scopeCanvas').getContext('2d');
let scopeChart, simState, circuitCanvas;

simState = {
    theoreme: 'superposition',
    E1: 12,
    E2: 6,
    R1: 100,
    R2: 200,
    R3: 150,
    RL: 300,
    resultat: {}
};

const THEOREMES = {
    'superposition': {
        nom: '➕ Théorème de superposition',
        description: 'Calcul en activant une source à la fois',
        formule: 'I_total = I₁ + I₂ + ... + Iₙ'
    },
    'thevenin': {
        nom: '🔋 Théorème de Thévenin',
        description: 'Réduction à une source de tension + résistance série',
        formule: 'E_th = V_ab (circuit ouvert), R_th = R_équivalente'
    },
    'norton': {
        nom: '⚡ Théorème de Norton',
        description: 'Réduction à une source de courant + résistance parallèle',
        formule: 'I_N = I_cc, R_N = R_th'
    },
    'millman': {
        nom: '🎛️ Théorème de Millman',
        description: 'Calcul de potentiel pour branches en parallèle',
        formule: 'V = (ΣE/R) / (Σ1/R)'
    },
    'kirchhoff': {
        nom: '🔄 Lois de Kirchhoff',
        description: 'KCL (courants) + KVL (tensions)',
        formule: 'ΣI = 0 (nœuds), ΣU = 0 (mailles)'
    }
};

function initChart() {
    // Diagramme en barres pour comparer les résultats
    scopeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Tension (V)', 'Courant (mA)', 'Puissance (mW)'],
            datasets: [{
                label: 'Résultats',
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(231, 76, 60, 0.6)',
                    'rgba(52, 152, 219, 0.6)',
                    'rgba(46, 204, 113, 0.6)'
                ],
                borderColor: [
                    'rgba(231, 76, 60, 1)',
                    'rgba(52, 152, 219, 1)',
                    'rgba(46, 204, 113, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
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
            <label class="form-label"><strong>Théorème à appliquer</strong></label>
            <select id="theoreme" class="form-select" onchange="changerTheoreme()">
                ${Object.keys(THEOREMES).map(key => 
                    `<option value="${key}">${THEOREMES[key].nom}</option>`
                ).join('')}
            </select>
            <div class="alert alert-info mt-2 mb-0">
                <strong>${THEOREMES['superposition'].description}</strong><br>
                <code>${THEOREMES['superposition'].formule}</code>
            </div>
        </div>
        
        <div class="col-md-3">
            <label class="form-label"><strong>Source E₁ (V)</strong></label>
            <input type="range" class="form-range" id="e1" min="1" max="24" value="12" step="1" oninput="calculer()">
            <div class="text-center"><span id="val-e1" class="badge bg-danger">12 V</span></div>
        </div>
        
        <div class="col-md-3">
            <label class="form-label"><strong>Source E₂ (V)</strong></label>
            <input type="range" class="form-range" id="e2" min="0" max="24" value="6" step="1" oninput="calculer()">
            <div class="text-center"><span id="val-e2" class="badge bg-warning">6 V</span></div>
        </div>
        
        <div class="col-md-3">
            <label class="form-label"><strong>Résistance R₁ (Ω)</strong></label>
            <input type="range" class="form-range" id="r1" min="10" max="1000" value="100" step="10" oninput="calculer()">
            <div class="text-center"><span id="val-r1" class="badge bg-primary">100 Ω</span></div>
        </div>
        
        <div class="col-md-3">
            <label class="form-label"><strong>Résistance R₂ (Ω)</strong></label>
            <input type="range" class="form-range" id="r2" min="10" max="1000" value="200" step="10" oninput="calculer()">
            <div class="text-center"><span id="val-r2" class="badge bg-primary">200 Ω</span></div>
        </div>
        
        <div class="col-md-4">
            <label class="form-label"><strong>Résistance R₃ (Ω)</strong></label>
            <input type="range" class="form-range" id="r3" min="10" max="1000" value="150" step="10" oninput="calculer()">
            <div class="text-center"><span id="val-r3" class="badge bg-secondary">150 Ω</span></div>
        </div>
        
        <div class="col-md-4">
            <label class="form-label"><strong>Charge R_L (Ω)</strong></label>
            <input type="range" class="form-range" id="rl" min="50" max="1000" value="300" step="10" oninput="calculer()">
            <div class="text-center"><span id="val-rl" class="badge bg-success">300 Ω</span></div>
        </div>
        
        <div class="col-md-4 d-flex align-items-end">
            <button class="btn btn-primary w-100" onclick="calculer()">
                <i class="fas fa-calculator"></i> Calculer
            </button>
        </div>
        
        <div class="col-12 mt-3">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <strong>📊 Résultats détaillés</strong>
                </div>
                <div class="card-body" id="resultats-detailles">
                    <p class="text-muted">Cliquez sur "Calculer" pour voir les résultats</p>
                </div>
            </div>
        </div>
        
        <div class="col-12 mt-3">
            <div class="card">
                <div class="card-header bg-dark text-white">
                    <strong>🔌 Schéma du circuit</strong>
                </div>
                <div class="card-body text-center" style="background: #f8f9fa;">
                    <canvas id="circuitCanvas" width="600" height="300"></canvas>
                </div>
            </div>
        </div>
    `;

    circuitCanvas = document.getElementById('circuitCanvas');
    changerTheoreme();
}

function changerTheoreme() {
    simState.theoreme = document.getElementById('theoreme').value;
    const theoreme = THEOREMES[simState.theoreme];

    const alertBox = document.querySelector('.alert-info');
    alertBox.innerHTML = `
        <strong>${theoreme.description}</strong><br>
        <code>${theoreme.formule}</code>
    `;

    calculer();
}

function calculer() {
    // Récupération des paramètres
    simState.E1 = parseFloat(document.getElementById('e1').value);
    simState.E2 = parseFloat(document.getElementById('e2').value);
    simState.R1 = parseFloat(document.getElementById('r1').value);
    simState.R2 = parseFloat(document.getElementById('r2').value);
    simState.R3 = parseFloat(document.getElementById('r3').value);
    simState.RL = parseFloat(document.getElementById('rl').value);

    // Mise à jour badges
    document.getElementById('val-e1').innerText = simState.E1 + ' V';
    document.getElementById('val-e2').innerText = simState.E2 + ' V';
    document.getElementById('val-r1').innerText = simState.R1 + ' Ω';
    document.getElementById('val-r2').innerText = simState.R2 + ' Ω';
    document.getElementById('val-r3').innerText = simState.R3 + ' Ω';
    document.getElementById('val-rl').innerText = simState.RL + ' Ω';

    // Calculs selon le théorème
    let resultat = {};

    if (simState.theoreme === 'superposition') {
        resultat = calculerSuperposition();
    } else if (simState.theoreme === 'thevenin') {
        resultat = calculerThevenin();
    } else if (simState.theoreme === 'norton') {
        resultat = calculerNorton();
    } else if (simState.theoreme === 'millman') {
        resultat = calculerMillman();
    } else if (simState.theoreme === 'kirchhoff') {
        resultat = calculerKirchhoff();
    }

    simState.resultat = resultat;
    afficherResultats(resultat);
    dessinerCircuit();

    // Mettre à jour le graphique
    scopeChart.data.datasets[0].data = [
        resultat.tension || 0,
        (resultat.courant || 0) * 1000,
        (resultat.puissance || 0) * 1000
    ];
    scopeChart.update();
}

function calculerSuperposition() {
    // Contribution de E1 (E2 = 0)
    const Req1 = simState.R1 + (simState.R2 * simState.RL) / (simState.R2 + simState.RL);
    const I1_total = simState.E1 / Req1;
    const I1_RL = I1_total * simState.R2 / (simState.R2 + simState.RL);

    // Contribution de E2 (E1 = 0)
    const Req2 = simState.R2 + (simState.R1 * simState.RL) / (simState.R1 + simState.RL);
    const I2_total = simState.E2 / Req2;
    const I2_RL = I2_total * simState.R1 / (simState.R1 + simState.RL);

    // Superposition
    const I_RL = I1_RL + I2_RL;
    const V_RL = I_RL * simState.RL;
    const P_RL = V_RL * I_RL;

    return {
        tension: V_RL,
        courant: I_RL,
        puissance: P_RL,
        details: `
            <strong>Étape 1 :</strong> E₁ seule (E₂ = 0)<br>
            I₁(R_L) = ${(I1_RL * 1000).toFixed(2)} mA<br><br>
            
            <strong>Étape 2 :</strong> E₂ seule (E₁ = 0)<br>
            I₂(R_L) = ${(I2_RL * 1000).toFixed(2)} mA<br><br>
            
            <strong>Superposition :</strong><br>
            I_total = I₁ + I₂ = ${(I_RL * 1000).toFixed(2)} mA
        `
    };
}

function calculerThevenin() {
    // E_th = tension à vide aux bornes de RL
    const E_th = (simState.E1 * simState.R2 - simState.E2 * simState.R1) / (simState.R1 + simState.R2);

    // R_th = résistance équivalente vue de RL (sources éteintes)
    const R_th = (simState.R1 * simState.R2) / (simState.R1 + simState.R2);

    // Courant et tension dans RL
    const I_RL = E_th / (R_th + simState.RL);
    const V_RL = I_RL * simState.RL;
    const P_RL = V_RL * I_RL;

    return {
        tension: V_RL,
        courant: I_RL,
        puissance: P_RL,
        E_th: E_th,
        R_th: R_th,
        details: `
            <strong>Générateur de Thévenin :</strong><br>
            E_th = ${E_th.toFixed(2)} V<br>
            R_th = ${R_th.toFixed(2)} Ω<br><br>
            
            <strong>Circuit équivalent :</strong><br>
            I = E_th / (R_th + R_L) = ${(I_RL * 1000).toFixed(2)} mA
        `
    };
}

function calculerNorton() {
    // I_N = courant de court-circuit
    const I_N = (simState.E1 / simState.R1) + (simState.E2 / simState.R2);

    // R_N = R_th
    const R_N = (simState.R1 * simState.R2) / (simState.R1 + simState.R2);

    // Courant dans RL (diviseur de courant)
    const I_RL = I_N * R_N / (R_N + simState.RL);
    const V_RL = I_RL * simState.RL;
    const P_RL = V_RL * I_RL;

    return {
        tension: V_RL,
        courant: I_RL,
        puissance: P_RL,
        I_N: I_N,
        R_N: R_N,
        details: `
            <strong>Générateur de Norton :</strong><br>
            I_N = ${(I_N * 1000).toFixed(2)} mA<br>
            R_N = ${R_N.toFixed(2)} Ω<br><br>
            
            <strong>Diviseur de courant :</strong><br>
            I_L = I_N × R_N/(R_N + R_L) = ${(I_RL * 1000).toFixed(2)} mA
        `
    };
}

function calculerMillman() {
    // Potentiel du nœud
    const numerateur = simState.E1 / simState.R1 + simState.E2 / simState.R2;
    const denominateur = 1 / simState.R1 + 1 / simState.R2 + 1 / simState.RL;

    const V_noeud = numerateur / denominateur;
    const I_RL = V_noeud / simState.RL;
    const P_RL = V_noeud * I_RL;

    return {
        tension: V_noeud,
        courant: I_RL,
        puissance: P_RL,
        details: `
            <strong>Théorème de Millman :</strong><br>
            V = (ΣE/R) / (Σ1/R)<br><br>
            
            Numérateur = ${numerateur.toFixed(4)}<br>
            Dénominateur = ${denominateur.toFixed(4)}<br><br>
            
            V_nœud = ${V_noeud.toFixed(2)} V
        `
    };
}

function calculerKirchhoff() {
    // Résolution par système (simplifiée pour un circuit à 2 mailles)
    // Maille 1 : E1 - R1*I1 - RL*(I1-I2) = 0
    // Maille 2 : E2 - R2*I2 - RL*(I2-I1) = 0

    const a11 = simState.R1 + simState.RL;
    const a12 = -simState.RL;
    const a21 = -simState.RL;
    const a22 = simState.R2 + simState.RL;

    const det = a11 * a22 - a12 * a21;

    const I1 = (simState.E1 * a22 - simState.E2 * a12) / det;
    const I2 = (a11 * simState.E2 - a21 * simState.E1) / det;

    const I_RL = I1 - I2;
    const V_RL = I_RL * simState.RL;
    const P_RL = V_RL * I_RL;

    return {
        tension: V_RL,
        courant: I_RL,
        puissance: P_RL,
        details: `
            <strong>Lois de Kirchhoff :</strong><br>
            Maille 1 : E₁ - R₁I₁ - R_L(I₁-I₂) = 0<br>
            Maille 2 : E₂ - R₂I₂ - R_L(I₂-I₁) = 0<br><br>
            
            <strong>Solution :</strong><br>
            I₁ = ${(I1 * 1000).toFixed(2)} mA<br>
            I₂ = ${(I2 * 1000).toFixed(2)} mA<br>
            I_L = I₁ - I₂ = ${(I_RL * 1000).toFixed(2)} mA
        `
    };
}

function afficherResultats(resultat) {
    const container = document.getElementById('resultats-detailles');
    container.innerHTML = `
        <div class="row text-center mb-3">
            <div class="col-md-4">
                <h4 class="text-danger">${resultat.tension.toFixed(2)} V</h4>
                <small>Tension aux bornes de R_L</small>
            </div>
            <div class="col-md-4">
                <h4 class="text-primary">${(resultat.courant * 1000).toFixed(2)} mA</h4>
                <small>Courant dans R_L</small>
            </div>
            <div class="col-md-4">
                <h4 class="text-success">${(resultat.puissance * 1000).toFixed(2)} mW</h4>
                <small>Puissance dissipée</small>
            </div>
        </div>
        <hr>
        ${resultat.details}
    `;
}

function dessinerCircuit() {
    const canvas = circuitCanvas;
    const ctx2d = canvas.getContext('2d');

    ctx2d.clearRect(0, 0, canvas.width, canvas.height);

    ctx2d.strokeStyle = '#2c3e50';
    ctx2d.lineWidth = 2;
    ctx2d.font = '14px Arial';
    ctx2d.fillStyle = '#2c3e50';

    // Circuit simple : E1-R1 en série avec E2-R2, le tout alimente RL

    // Source E1
    ctx2d.beginPath();
    ctx2d.arc(100, 100, 15, 0, 2 * Math.PI);
    ctx2d.stroke();
    ctx2d.fillText(`E₁=${simState.E1}V`, 70, 95);

    // R1
    ctx2d.strokeRect(150, 90, 60, 20);
    ctx2d.fillText(`R₁=${simState.R1}Ω`, 155, 130);

    // Connexion au nœud central
    ctx2d.beginPath();
    ctx2d.moveTo(115, 100);
    ctx2d.lineTo(150, 100);
    ctx2d.stroke();

    ctx2d.beginPath();
    ctx2d.moveTo(210, 100);
    ctx2d.lineTo(300, 100);
    ctx2d.stroke();

    // Source E2
    ctx2d.beginPath();
    ctx2d.arc(100, 200, 15, 0, 2 * Math.PI);
    ctx2d.stroke();
    ctx2d.fillText(`E₂=${simState.E2}V`, 70, 195);

    // R2
    ctx2d.strokeRect(150, 190, 60, 20);
    ctx2d.fillText(`R₂=${simState.R2}Ω`, 155, 230);

    // Connexion
    ctx2d.beginPath();
    ctx2d.moveTo(115, 200);
    ctx2d.lineTo(150, 200);
    ctx2d.stroke();

    ctx2d.beginPath();
    ctx2d.moveTo(210, 200);
    ctx2d.lineTo(300, 200);
    ctx2d.stroke();

    // Nœud central
    ctx2d.fillStyle = '#e74c3c';
    ctx2d.beginPath();
    ctx2d.arc(300, 150, 5, 0, 2 * Math.PI);
    ctx2d.fill();

    ctx2d.strokeStyle = '#2c3e50';
    ctx2d.beginPath();
    ctx2d.moveTo(300, 100);
    ctx2d.lineTo(300, 200);
    ctx2d.stroke();

    // RL (charge)
    ctx2d.strokeStyle = '#27ae60';
    ctx2d.lineWidth = 3;
    ctx2d.strokeRect(350, 130, 80, 40);
    ctx2d.fillStyle = '#27ae60';
    ctx2d.fillText(`R_L=${simState.RL}Ω`, 360, 160);

    // Connexions RL
    ctx2d.strokeStyle = '#2c3e50';
    ctx2d.lineWidth = 2;
    ctx2d.beginPath();
    ctx2d.moveTo(300, 150);
    ctx2d.lineTo(350, 150);
    ctx2d.stroke();

    ctx2d.beginPath();
    ctx2d.moveTo(430, 150);
    ctx2d.lineTo(500, 150);
    ctx2d.lineTo(500, 100);
    ctx2d.lineTo(85, 100);
    ctx2d.stroke();

    ctx2d.beginPath();
    ctx2d.moveTo(500, 150);
    ctx2d.lineTo(500, 200);
    ctx2d.lineTo(85, 200);
    ctx2d.stroke();

    // Masse
    ctx2d.beginPath();
    ctx2d.moveTo(40, 100);
    ctx2d.lineTo(40, 200);
    ctx2d.stroke();

    for (let i = 0; i < 4; i++) {
        ctx2d.beginPath();
        ctx2d.moveTo(40 - 5 - i * 3, 200 + i * 5);
        ctx2d.lineTo(40 + 5 + i * 3, 200 + i * 5);
        ctx2d.stroke();
    }

    ctx2d.beginPath();
    ctx2d.moveTo(40, 100);
    ctx2d.lineTo(85, 100);
    ctx2d.stroke();

    ctx2d.beginPath();
    ctx2d.moveTo(40, 200);
    ctx2d.lineTo(85, 200);
    ctx2d.stroke();
}

function getParametresActuels() {
    return {
        Theoreme: simState.theoreme,
        E1_V: simState.E1,
        E2_V: simState.E2,
        R1_Ohm: simState.R1,
        R2_Ohm: simState.R2,
        RL_Ohm: simState.RL
    };
}

function getResultatsActuels() {
    return {
        Tension_V: simState.resultat.tension?.toFixed(2),
        Courant_mA: (simState.resultat.courant * 1000)?.toFixed(2),
        Puissance_mW: (simState.resultat.puissance * 1000)?.toFixed(2)
    };
}

initChart();
generateControls();