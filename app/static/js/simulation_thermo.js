<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Le Welt - Thermodynamique & Cycles de Puissance</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --tech-dark: #010205;
            --tech-panel: rgba(10, 15, 30, 0.85);
            --neon-cyan: #00e1ff;
            --neon-purple: #b026ff;
            --neon-green: #10b981;
            --neon-orange: #f59e0b;
            --neon-red: #ff0055;
            --neon-blue: #3b82f6;
        }

        body {
            background-color: var(--tech-dark);
            color: #e2e8f0;
            font-family: 'Rajdhani', sans-serif;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(255, 0, 85, 0.05) 0%, transparent 60%),
                linear-gradient(to right, rgba(0, 225, 255, 0.02) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(0, 225, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 40px 40px, 40px 40px;
        }

        .orbitron { font-family: 'Orbitron', sans-serif; }

        .panel {
            background: var(--tech-panel);
            border: 1px solid rgba(255, 0, 85, 0.2);
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(255, 0, 85, 0.05);
            backdrop-filter: blur(12px);
        }

        input[type="range"] {
            -webkit-appearance: none; width: 100%; height: 4px;
            background: rgba(255, 255, 255, 0.1); border-radius: 5px; outline: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none; appearance: none; width: 14px; height: 14px;
            border-radius: 50%; background: var(--neon-red); cursor: pointer;
            box-shadow: 0 0 10px var(--neon-red); transition: transform 0.2s;
        }
        input[type="range"]::-webkit-slider-thumb:hover { transform: scale(1.3); }

        select, button { outline: none; transition: all 0.3s ease; }
        
        .digital-screen {
            background: #000; border: 1px solid #1e293b; border-radius: 6px;
            font-family: 'Orbitron', monospace; box-shadow: inset 0 0 15px rgba(0,0,0,0.8);
        }

        .btn-glow:hover { box-shadow: 0 0 15px currentColor; }
        
        .equadif-box {
            font-family: 'Courier New', Courier, monospace;
            background: rgba(0, 0, 0, 0.6);
            border-left: 3px solid var(--neon-red);
        }

        .chart-tab.active { background: rgba(255, 0, 85, 0.2); border-color: var(--neon-red); color: var(--neon-red); }
        .chart-tab { background: transparent; border-color: #334155; color: #94a3b8; transition: all 0.3s; }
    </style>
</head>
<body class="min-h-screen p-4 flex flex-col items-center">

    <div class="w-full max-w-[1400px] mb-4 text-center">
        <h1 class="text-3xl md:text-4xl font-black orbitron text-transparent bg-clip-text bg-gradient-to-r from-[#ff0055] via-[#f59e0b] to-[#00e1ff] tracking-widest uppercase">
            LABORATOIRE LE WELT : THERMODYNAMIQUE
        </h1>
        <p class="text-slate-400 font-bold tracking-widest mt-1 uppercase text-xs md:text-sm">
            Cycles de Carnot, Diagrammes d'État (P-V & T-S) et Machines Thermiques
        </p>
    </div>

    <div class="w-full max-w-[1400px] grid grid-cols-1 lg:grid-cols-12 gap-4 h-full">
        
        <!-- PANNEAU DE CONTRÔLE (Gauche) -->
        <div class="lg:col-span-3 panel rounded-2xl p-4 flex flex-col gap-4">
            
            <!-- SÉLECTEUR DE MODULE -->
            <div class="bg-black/50 border border-[#ff0055] p-2 rounded-lg">
                <label class="block text-[10px] font-bold text-[#ff0055] uppercase tracking-widest mb-1">Architecture Thermique</label>
                <select id="mode-select" class="w-full bg-transparent text-white font-bold text-xs orbitron cursor-pointer" onchange="updateSim()">
                    <option value="moteur">MOTEUR THERMIQUE (Création Travail)</option>
                    <option value="froid">MACHINE FRIGORIFIQUE / POMPE À CHALEUR</option>
                </select>
            </div>

            <!-- VARIABLES D'ÉTAT -->
            <div class="space-y-4">
                
                <div>
                    <label class="flex justify-between text-[10px] font-bold text-[#ff0055] uppercase mb-1">
                        <span>Source Chaude ($T_C$)</span>
                        <span id="val-tc" class="text-[#ff0055]">500 K</span>
                    </label>
                    <input type="range" id="in-tc" min="300" max="1500" step="10" value="500" style="accent-color: var(--neon-red);" oninput="updateSim()">
                </div>

                <div>
                    <label class="flex justify-between text-[10px] font-bold text-[#00e1ff] uppercase mb-1">
                        <span>Source Froide ($T_F$)</span>
                        <span id="val-tf" class="text-[#00e1ff]">300 K</span>
                    </label>
                    <input type="range" id="in-tf" min="50" max="400" step="10" value="300" style="accent-color: var(--neon-cyan);" oninput="updateSim()">
                </div>

                <div class="pt-2 border-t border-slate-700">
                    <label class="flex justify-between text-[10px] font-bold text-slate-300 uppercase mb-1">
                        <span>Taux de Compression ($V_2/V_1$)</span>
                        <span id="val-vratio">2.0</span>
                    </label>
                    <input type="range" id="in-vratio" min="1.5" max="10" step="0.5" value="2.0" style="accent-color: var(--neon-purple);" oninput="updateSim()">
                </div>

                <!-- IRRÉVERSIBILITÉS -->
                <div class="pt-2 border-t border-slate-700">
                    <label class="flex justify-between text-[10px] font-bold text-[#f59e0b] uppercase mb-1">
                        <span>Irréversibilités (Entropie Créée)</span>
                        <span id="val-irrev">0%</span>
                    </label>
                    <input type="range" id="in-irrev" min="0" max="80" step="5" value="0" style="accent-color: var(--neon-orange);" oninput="updateSim()">
                    <p class="text-[8px] text-slate-500 mt-1">Frottements mécaniques et fuites thermiques.</p>
                </div>
            </div>
            
            <div class="mt-auto pt-2 flex flex-col gap-2">
                <button id="btn-play" onclick="toggleSim()" class="w-full bg-[#10b981]/20 text-[#10b981] border border-[#10b981] p-2 rounded font-bold orbitron text-xs btn-glow">
                    DÉMARRER LE CYCLE MOTEUR
                </button>
                <button onclick="exportCSV()" class="w-full bg-transparent text-[#94a3b8] border border-slate-600 p-2 rounded font-bold orbitron text-[10px] uppercase tracking-widest hover:bg-slate-800 transition-colors">
                    EXPORTER DONNÉES P-V (CSV)
                </button>
            </div>
        </div>

        <!-- ZONE D'ANALYSE GRAPHIQUE (Centre) -->
        <div class="lg:col-span-5 panel rounded-2xl p-4 flex flex-col relative min-h-[450px]">
            <div class="flex justify-between items-center mb-2 border-b border-slate-700 pb-2">
                <h2 class="orbitron text-md font-bold text-white uppercase tracking-widest flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-red-500 animate-pulse" id="rec-light" style="display:none;"></div>
                    Oscilloscope Thermodynamique
                </h2>
                <div class="flex gap-1">
                    <button onclick="switchChart('pv')" id="tab-pv" class="chart-tab active text-[9px] border px-2 py-1 rounded font-bold uppercase tracking-wider">Clapeyron (P-V)</button>
                    <button onclick="switchChart('ts')" id="tab-ts" class="chart-tab text-[9px] border px-2 py-1 rounded font-bold uppercase tracking-wider">Entropique (T-S)</button>
                </div>
            </div>

            <!-- Conteneurs Graphiques -->
            <div class="flex-1 w-full bg-[#010205] rounded border border-slate-700 p-2 relative min-h-[300px]">
                <canvas id="pvChart" style="display:block;"></canvas>
                <canvas id="tsChart" style="display:none;"></canvas>
            </div>
            
            <!-- Équations Dynamiques -->
            <div class="w-full equadif-box p-3 rounded-lg mt-3 text-[11px] text-slate-300">
                <div class="text-[#ff0055] font-bold mb-1 uppercase border-b border-slate-700 pb-1">Bilan Énergétique (1er Principe)</div>
                <div class="grid grid-cols-3 gap-2 text-center mt-2">
                    <div>
                        <div class="text-[#ff0055]">$Q_{chaud}$ (Apporté)</div>
                        <div class="font-bold text-white mt-1"><span id="eq-qc">0.0</span> kJ</div>
                    </div>
                    <div>
                        <div class="text-[#10b981]">$W_{net}$ (Travail Utile)</div>
                        <div class="font-bold text-white mt-1"><span id="eq-w">0.0</span> kJ</div>
                    </div>
                    <div>
                        <div class="text-[#00e1ff]">$Q_{froid}$ (Rejeté)</div>
                        <div class="font-bold text-white mt-1"><span id="eq-qf">0.0</span> kJ</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- APPAREIL DE TÉLÉMÉTRIE ET PISTON (Droite) -->
        <div class="lg:col-span-4 panel rounded-2xl p-4 flex flex-col gap-3">
            <h2 class="orbitron text-md font-bold text-white uppercase tracking-widest border-b border-slate-700 pb-2">
                Télémétrie & Chambre à Gaz
            </h2>
            
            <!-- Animation Piston 2D -->
            <div class="w-full bg-[#010205] rounded border border-slate-700 p-2 relative h-[180px] flex items-center justify-center overflow-hidden">
                <canvas id="pistonCanvas" width="300" height="150"></canvas>
                <div class="absolute top-2 left-2 text-[9px] font-mono text-[#00e1ff]" id="piston-phase">PHASE: ISOTHERME</div>
            </div>

            <!-- Télémétrie Numérique -->
            <div class="mt-2 space-y-2">
                <div class="digital-screen p-2 flex justify-between items-center border-l-4 border-[#10b981]">
                    <span class="text-[9px] text-slate-400 uppercase" id="lbl-perf">Rendement Carnot ($\eta$)</span>
                    <span class="text-lg font-bold text-[#10b981]" id="out-perf">0.00 %</span>
                </div>
                <div class="digital-screen p-2 flex justify-between items-center border-l-4 border-[#f59e0b]">
                    <span class="text-[9px] text-slate-400 uppercase" id="lbl-real-perf">Rendement Réel ($\eta_{reel}$)</span>
                    <span class="text-lg font-bold text-[#f59e0b]" id="out-real-perf">0.00 %</span>
                </div>
                <div class="digital-screen p-2 flex justify-between items-center border-l-4 border-[#b026ff]">
                    <span class="text-[9px] text-slate-400 uppercase">Création d'Entropie ($S_{gen}$)</span>
                    <span class="text-sm font-bold text-[#b026ff]" id="out-entropy">0.00 J/K</span>
                </div>
            </div>
            
            <p class="text-[9px] text-slate-500 mt-2 text-justify">
                Le théorème de Sadi Carnot stipule que l'efficacité d'une machine thermique opérant entre deux sources est strictement bornée par la différence de température. L'ajout d'irréversibilités contracte l'aire du cycle, ruinant le travail mécanique disponible.
            </p>
        </div>
    </div>

    <script>
        // --- CONSTANTES PHYSIQUES ---
        const R = 8.314; // J/(mol.K)
        const n = 1; // moles
        const gamma = 1.4; // Gaz diatomique (air)
        const V1 = 0.01; // m3 initial
        
        // --- ETAT GLOBAL ---
        let Tc = 500, Tf = 300, v_ratio = 2.0, irrev = 0;
        let mode = 'moteur'; // ou 'froid'
        
        let pvData = [];
        let tsData = [];
        let currentDotPv = {x: 0, y: 0};
        let currentDotTs = {x: 0, y: 0};
        
        let W_net = 0, Qc = 0, Qf = 0, efficiency = 0;
        
        // Moteur de temps
        let isRunning = false;
        let cycleTime = 0;
        let reqAnim;

        // --- CHART.JS GLOBALS ---
        let pvChart, tsChart;

        function initCharts() {
            Chart.defaults.color = '#64748b';
            Chart.defaults.font.family = 'Rajdhani';

            // Graphe P-V (Clapeyron)
            const ctxPv = document.getElementById('pvChart').getContext('2d');
            pvChart = new Chart(ctxPv, {
                type: 'scatter',
                data: {
                    datasets: [
                        { label: 'Cycle P-V', data: [], borderColor: '#ff0055', backgroundColor: 'rgba(255, 0, 85, 0.1)', borderWidth: 3, showLine: true, fill: true, pointRadius: 0 },
                        { label: 'État Actuel', data: [], backgroundColor: '#fff', pointRadius: 6, pointBorderColor: '#ff0055', pointBorderWidth: 2 }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false, animation: false,
                    scales: { 
                        x: { title: {display: true, text: 'Volume (m³)'}, min: 0 }, 
                        y: { title: {display: true, text: 'Pression (kPa)'}, min: 0 } 
                    },
                    plugins: { legend: { display: false } }
                }
            });

            // Graphe T-S (Entropique)
            const ctxTs = document.getElementById('tsChart').getContext('2d');
            tsChart = new Chart(ctxTs, {
                type: 'scatter',
                data: {
                    datasets: [
                        { label: 'Cycle T-S', data: [], borderColor: '#00e1ff', backgroundColor: 'rgba(0, 225, 255, 0.1)', borderWidth: 3, showLine: true, fill: true, pointRadius: 0 },
                        { label: 'État Actuel', data: [], backgroundColor: '#fff', pointRadius: 6, pointBorderColor: '#00e1ff', pointBorderWidth: 2 }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false, animation: false,
                    scales: { 
                        x: { title: {display: true, text: 'Entropie S (J/K)'} }, 
                        y: { title: {display: true, text: 'Température T (K)'}, min: 0 } 
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }

        function switchChart(tab) {
            document.getElementById('tab-pv').className = tab === 'pv' ? 'chart-tab active text-[9px] border px-2 py-1 rounded font-bold uppercase tracking-wider' : 'chart-tab text-[9px] border px-2 py-1 rounded font-bold uppercase tracking-wider';
            document.getElementById('tab-ts').className = tab === 'ts' ? 'chart-tab active text-[9px] border px-2 py-1 rounded font-bold uppercase tracking-wider' : 'chart-tab text-[9px] border px-2 py-1 rounded font-bold uppercase tracking-wider';
            
            document.getElementById('pvChart').style.display = tab === 'pv' ? 'block' : 'none';
            document.getElementById('tsChart').style.display = tab === 'ts' ? 'block' : 'none';
        }

        // --- MATHÉMATIQUES DU CYCLE DE CARNOT ---
        function calculateCarnot() {
            pvData = []; tsData = [];
            
            // Calcul des volumes
            const V2 = V1 * v_ratio;
            // Transformation Adiabatique: T_C * V2^(y-1) = T_F * V3^(y-1)
            const V3 = V2 * Math.pow(Tc / Tf, 1 / (gamma - 1));
            // Transformation Adiabatique 2: T_C * V1^(y-1) = T_F * V4^(y-1)
            const V4 = V1 * Math.pow(Tc / Tf, 1 / (gamma - 1));

            // Calcul Thermodynamique Théorique
            Qc = n * R * Tc * Math.log(V2 / V1);
            Qf = n * R * Tf * Math.log(V3 / V4); // Valeur absolue rejetée
            
            // Irréversibilités (On réduit le travail utile, la chaleur rejetée augmente)
            const factor = 1 - (irrev / 100);
            W_net = (Qc - Qf) * factor; 
            const Q_pertes = (Qc - Qf) * (1 - factor);
            const Qf_reel = Qf + Q_pertes;

            // Rendements
            efficiency = 1 - (Tf / Tc);
            const real_efficiency = W_net / Qc;

            // Mise à jour de l'UI
            document.getElementById('eq-qc').innerText = (Qc / 1000).toFixed(2);
            document.getElementById('eq-w').innerText = (W_net / 1000).toFixed(2);
            document.getElementById('eq-qf').innerText = (Qf_reel / 1000).toFixed(2);
            
            // Gestion Affichage COP vs Rendement
            if (mode === 'moteur') {
                document.getElementById('lbl-perf').innerText = "Rendement Carnot (η)";
                document.getElementById('out-perf').innerText = (efficiency * 100).toFixed(1) + " %";
                document.getElementById('lbl-real-perf').innerText = "Rendement Réel (η_reel)";
                document.getElementById('out-real-perf').innerText = (real_efficiency * 100).toFixed(1) + " %";
            } else {
                document.getElementById('lbl-perf').innerText = "COP Idéal (Carnot)";
                const cop = Tf / (Tc - Tf);
                document.getElementById('out-perf').innerText = cop.toFixed(2);
                document.getElementById('lbl-real-perf').innerText = "COP Réel";
                document.getElementById('out-real-perf').innerText = (cop * factor).toFixed(2);
            }

            // Entropie Générée
            const deltaS = Q_pertes / Tf;
            document.getElementById('out-entropy').innerText = deltaS.toFixed(2) + " J/K";

            // --- GÉNÉRATION DES COURBES ---
            const steps = 30;
            let S0 = 10; // Référence entropie

            // Helper pour ajouter un point
            const addPoint = (V, T, S) => {
                const P = (n * R * T) / V / 1000; // kPa
                pvData.push({x: V, y: P, T: T});
                tsData.push({x: S, y: T, V: V});
            };

            // 1. Expansion Isotherme (T_C) : 1 -> 2
            let dS_iso_c = n * R * Math.log(V2/V1);
            for(let i=0; i<=steps; i++) {
                let V = V1 + (V2-V1)*(i/steps);
                let S = S0 + dS_iso_c*(i/steps);
                addPoint(V, Tc, S);
            }

            // 2. Expansion Adiabatique : 2 -> 3
            let S_act = tsData[tsData.length-1].x;
            for(let i=1; i<=steps; i++) {
                let V = V2 + (V3-V2)*(i/steps);
                let T = Tc * Math.pow(V2/V, gamma-1);
                // Si irréversibilité, l'entropie augmente pendant l'adiabatique théorique
                let S_irr = S_act + (deltaS/2)*(i/steps); 
                addPoint(V, T, S_irr);
            }

            // 3. Compression Isotherme (T_F) : 3 -> 4
            S_act = tsData[tsData.length-1].x;
            let dS_iso_f = n * R * Math.log(V3/V4);
            for(let i=1; i<=steps; i++) {
                let V = V3 - (V3-V4)*(i/steps);
                let S = S_act - dS_iso_f*(i/steps);
                addPoint(V, Tf, S);
            }

            // 4. Compression Adiabatique : 4 -> 1
            S_act = tsData[tsData.length-1].x;
            for(let i=1; i<=steps; i++) {
                let V = V4 - (V4-V1)*(i/steps);
                let T = Tf * Math.pow(V4/V, gamma-1);
                let S_irr = S_act - (S_act - S0)*(i/steps); // Retourne à S0
                addPoint(V, T, S_irr);
            }

            // Si Pompe à chaleur, on inverse l'ordre des données du tracé
            if (mode === 'froid') {
                pvData.reverse();
                tsData.reverse();
            }

            pvChart.data.datasets[0].data = pvData;
            tsChart.data.datasets[0].data = tsData;
            pvChart.update();
            tsChart.update();
        }

        function updateSim() {
            // Lecture UI
            mode = document.getElementById('mode-select').value;
            Tc = parseFloat(document.getElementById('in-tc').value);
            Tf = parseFloat(document.getElementById('in-tf').value);
            
            // Check logique thermo
            if(Tf >= Tc) {
                Tf = Tc - 10;
                document.getElementById('in-tf').value = Tf;
            }

            v_ratio = parseFloat(document.getElementById('in-vratio').value);
            irrev = parseFloat(document.getElementById('in-irrev').value);

            document.getElementById('val-tc').innerText = Tc + " K";
            document.getElementById('val-tf').innerText = Tf + " K";
            document.getElementById('val-vratio').innerText = v_ratio.toFixed(1);
            document.getElementById('val-irrev').innerText = irrev + "%";

            // Changer les couleurs si on est en mode froid
            if(mode === 'froid') {
                document.documentElement.style.setProperty('--neon-red', '#3b82f6'); // Bleu dominant
                document.getElementById('btn-play').innerText = "DÉMARRER POMPE À CHALEUR";
            } else {
                document.documentElement.style.setProperty('--neon-red', '#ff0055'); // Rouge dominant
                document.getElementById('btn-play').innerText = "DÉMARRER CYCLE MOTEUR";
            }

            calculateCarnot();
            if(!isRunning) drawPiston(0); // Dessine l'état initial
        }

        // --- ANIMATION CANVAS 2D DU PISTON ---
        function drawPiston(progress) {
            const ctxP = document.getElementById('pistonCanvas').getContext('2d');
            const w = 300, h = 150;
            ctxP.clearRect(0, 0, w, h);

            // Interpolation pour trouver l'état actuel dans les tableaux Data
            if(pvData.length === 0) return;
            const idx = Math.floor(progress * (pvData.length - 1));
            const state = pvData[idx];
            const stateTs = tsData[idx];

            // Update Point Actuel Graphes
            pvChart.data.datasets[1].data = [{x: state.x, y: state.y}];
            tsChart.data.datasets[1].data = [{x: stateTs.x, y: stateTs.y}];
            pvChart.update();
            tsChart.update();

            // Dimensions de base du piston
            const pistonX = 40;
            const pistonY = 30;
            const pistonH = 90;
            
            // Max Volume pour échelle
            let maxV = 0; pvData.forEach(d => {if(d.x > maxV) maxV = d.x;});
            const lengthPixels = (state.x / maxV) * 180 + 20; 

            // Couleur du gaz basée sur la température
            const tempRatio = (state.T - Tf) / (Tc - Tf);
            const r = Math.round(tempRatio * 255);
            const b = Math.round((1 - tempRatio) * 255);
            const gasColor = `rgba(${r}, 0, ${b}, 0.5)`;

            // 1. Cylindre
            ctxP.fillStyle = "rgba(255,255,255,0.1)";
            ctxP.fillRect(pistonX, pistonY, 200, pistonH);
            ctxP.strokeStyle = "#94a3b8";
            ctxP.lineWidth = 4;
            ctxP.strokeRect(pistonX, pistonY, 200, pistonH);

            // 2. Gaz à l'intérieur
            ctxP.fillStyle = gasColor;
            ctxP.fillRect(pistonX, pistonY, lengthPixels, pistonH);

            // Particules de gaz (vitesse selon Température)
            ctxP.fillStyle = `rgb(${r}, 100, ${b})`;
            for(let i=0; i<30; i++) {
                let px = pistonX + Math.random() * lengthPixels;
                let py = pistonY + Math.random() * pistonH;
                ctxP.beginPath(); ctxP.arc(px, py, 2, 0, 2*Math.PI); ctxP.fill();
            }

            // 3. Tête de piston
            ctxP.fillStyle = "#cbd5e1";
            ctxP.fillRect(pistonX + lengthPixels, pistonY, 15, pistonH);

            // 4. Tige de piston
            ctxP.strokeStyle = "#cbd5e1";
            ctxP.lineWidth = 6;
            ctxP.beginPath();
            ctxP.moveTo(pistonX + lengthPixels + 15, pistonY + pistonH/2);
            ctxP.lineTo(280, pistonY + pistonH/2);
            ctxP.stroke();

            // 5. Source Thermique (Plaque à gauche)
            if (progress < 0.25) {
                // Contact source chaude
                ctxP.fillStyle = "#ff0055";
                ctxP.fillRect(pistonX - 10, pistonY, 10, pistonH);
                document.getElementById('piston-phase').innerText = "PHASE: DÉTENTE ISOTHERME (CHAUD)";
                document.getElementById('piston-phase').style.color = "#ff0055";
            } else if (progress > 0.5 && progress < 0.75) {
                // Contact source froide
                ctxP.fillStyle = "#00e1ff";
                ctxP.fillRect(pistonX - 10, pistonY, 10, pistonH);
                document.getElementById('piston-phase').innerText = "PHASE: COMPRESSION ISOTHERME (FROID)";
                document.getElementById('piston-phase').style.color = "#00e1ff";
            } else {
                // Isolant adiabatique
                ctxP.fillStyle = "#f59e0b";
                ctxP.fillRect(pistonX - 10, pistonY, 10, pistonH);
                if(progress >= 0.25 && progress <= 0.5) document.getElementById('piston-phase').innerText = "PHASE: DÉTENTE ADIABATIQUE";
                else document.getElementById('piston-phase').innerText = "PHASE: COMPRESSION ADIABATIQUE";
                document.getElementById('piston-phase').style.color = "#f59e0b";
            }
        }

        // --- CONTROLS ---
        function toggleSim() {
            isRunning = !isRunning;
            const btn = document.getElementById('btn-play');
            const recLight = document.getElementById('rec-light');
            if (isRunning) {
                btn.innerText = "PAUSE";
                btn.classList.replace('text-[#10b981]', 'text-[#f59e0b]');
                btn.classList.replace('border-[#10b981]', 'border-[#f59e0b]');
                if (recLight) recLight.style.display = "block";
                loop();
            } else {
                btn.innerText = mode==='moteur'?"DÉMARRER CYCLE MOTEUR":"DÉMARRER POMPE À CHALEUR";
                btn.classList.replace('text-[#f59e0b]', 'text-[#10b981]');
                btn.classList.replace('border-[#f59e0b]', 'border-[#10b981]');
                if (recLight) recLight.style.display = "none";
                cancelAnimationFrame(reqAnim);
            }
        }

        function loop() {
            if (isRunning) {
                cycleTime += 0.005; // Vitesse d'animation
                if (cycleTime > 1) cycleTime = 0;
                
                drawPiston(cycleTime);
                reqAnim = requestAnimationFrame(loop);
            }
        }

        function exportCSV() {
            if(pvData.length === 0) return;
            let csv = "data:text/csv;charset=utf-8,";
            csv += "Volume(m3),Pression(kPa),Temperature(K),Entropie(J/K)\n";
            for(let i=0; i<pvData.length; i++) {
                csv += `${pvData[i].x.toFixed(4)},${pvData[i].y.toFixed(2)},${pvData[i].T.toFixed(1)},${tsData[i].x.toFixed(2)}\n`;
            }
            const link = document.createElement("a");
            link.href = encodeURI(csv);
            link.download = `LeWelt_Carnot_Cycle.csv`;
            document.body.appendChild(link); link.click(); document.body.removeChild(link);
        }

        // Init
        window.onload = () => {
            initCharts();
            updateSim();
        };
    </script>
</body>
</html>