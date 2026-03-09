<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Le Welt - Électronique de Puissance (Convertisseur Buck)</title>
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
            --neon-yellow: #eab308;
        }

        body {
            background-color: var(--tech-dark);
            color: #e2e8f0;
            font-family: 'Rajdhani', sans-serif;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(16, 185, 129, 0.05) 0%, transparent 60%),
                linear-gradient(to right, rgba(0, 225, 255, 0.02) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(0, 225, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 40px 40px, 40px 40px;
        }

        .orbitron { font-family: 'Orbitron', sans-serif; }

        .panel {
            background: var(--tech-panel);
            border: 1px solid rgba(16, 185, 129, 0.2);
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(16, 185, 129, 0.05);
            backdrop-filter: blur(12px);
        }

        input[type="range"] {
            -webkit-appearance: none; width: 100%; height: 4px;
            background: rgba(255, 255, 255, 0.1); border-radius: 5px; outline: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none; appearance: none; width: 14px; height: 14px;
            border-radius: 50%; background: var(--neon-green); cursor: pointer;
            box-shadow: 0 0 10px var(--neon-green); transition: transform 0.2s;
        }
        input[type="range"]::-webkit-slider-thumb:hover { transform: scale(1.3); }

        select, button { outline: none; transition: all 0.3s ease; }
        
        .digital-screen {
            background: #000; border: 1px solid #1e293b; border-radius: 6px;
            font-family: 'Orbitron', monospace; box-shadow: inset 0 0 15px rgba(0,0,0,0.8);
        }

        .equadif-box {
            font-family: 'Courier New', Courier, monospace;
            background: rgba(0, 0, 0, 0.6);
            border-left: 3px solid var(--neon-green);
        }

        .btn-glow:hover { box-shadow: 0 0 15px currentColor; }
        .chart-tab.active { background: rgba(16, 185, 129, 0.2); border-color: var(--neon-green); color: var(--neon-green); }
        .chart-tab { background: transparent; border-color: #334155; color: #94a3b8; transition: all 0.3s; }
    </style>
</head>
<body class="min-h-screen p-4 flex flex-col items-center">

    <div class="w-full max-w-[1400px] mb-4 text-center">
        <h1 class="text-3xl md:text-4xl font-black orbitron text-transparent bg-clip-text bg-gradient-to-r from-[#10b981] via-[#00e1ff] to-[#b026ff] tracking-widest uppercase">
            LE WELT : ÉLECTRONIQUE DE PUISSANCE
        </h1>
        <p class="text-slate-400 font-bold tracking-widest mt-1 uppercase text-xs md:text-sm">
            Hacheur Série (Buck Converter), PWM & Filtrage RLC
        </p>
    </div>

    <div class="w-full max-w-[1400px] grid grid-cols-1 lg:grid-cols-12 gap-4 h-full">
        
        <!-- PANNEAU DE CONTRÔLE (Gauche) -->
        <div class="lg:col-span-3 panel rounded-2xl p-4 flex flex-col gap-4">
            <h2 class="orbitron text-md font-bold text-[#10b981] border-b border-[#10b981]/30 pb-2 flex justify-between items-center">
                <span>CONTRÔLEUR PWM</span>
                <span class="text-[9px] bg-[#10b981]/20 px-2 py-1 rounded text-white">GATE DRIVE</span>
            </h2>

            <div class="space-y-4">
                <!-- Tension d'entrée -->
                <div>
                    <label class="flex justify-between text-[10px] font-bold text-slate-300 uppercase mb-1">
                        <span>Tension Entrée ($V_{in}$)</span>
                        <span id="val-vin" class="text-[#00e1ff]">24.0 V</span>
                    </label>
                    <input type="range" id="in-vin" min="5" max="100" step="1" value="24" style="accent-color: #00e1ff;" oninput="updateParams()">
                </div>

                <!-- Rapport Cyclique -->
                <div>
                    <label class="flex justify-between text-[10px] font-bold text-[#ff0055] uppercase mb-1">
                        <span>Rapport Cyclique ($\alpha$)</span>
                        <span id="val-alpha" class="text-[#ff0055]">0.50 (50%)</span>
                    </label>
                    <input type="range" id="in-alpha" min="0.05" max="0.95" step="0.01" value="0.5" style="accent-color: #ff0055;" oninput="updateParams()">
                </div>

                <!-- Filtre LC -->
                <div class="pt-2 border-t border-slate-700">
                    <h3 class="text-[10px] font-bold text-[#b026ff] uppercase mb-2">Filtre de Lissage (LC)</h3>
                    <div class="mb-3">
                        <label class="flex justify-between text-[9px] font-bold text-slate-400 uppercase mb-1">
                            <span>Inductance ($L$)</span>
                            <span id="val-l">1.0 mH</span>
                        </label>
                        <input type="range" id="in-l" min="0.1" max="10" step="0.1" value="1.0" style="accent-color: #b026ff;" oninput="updateParams()">
                    </div>
                    <div>
                        <label class="flex justify-between text-[9px] font-bold text-slate-400 uppercase mb-1">
                            <span>Condensateur ($C$)</span>
                            <span id="val-c">100 µF</span>
                        </label>
                        <input type="range" id="in-c" min="10" max="1000" step="10" value="100" style="accent-color: #b026ff;" oninput="updateParams()">
                    </div>
                </div>

                <!-- Charge -->
                <div class="pt-2 border-t border-slate-700">
                    <label class="flex justify-between text-[10px] font-bold text-[#f59e0b] uppercase mb-1">
                        <span>Charge Résistive ($R$)</span>
                        <span id="val-r" class="text-[#f59e0b]">10.0 Ω</span>
                    </label>
                    <input type="range" id="in-r" min="1" max="100" step="1" value="10" style="accent-color: #f59e0b;" oninput="updateParams()">
                </div>
            </div>
            
            <div class="mt-auto pt-2 flex flex-col gap-2">
                <button id="btn-play" onclick="toggleSim()" class="w-full bg-[#10b981]/20 text-[#10b981] border border-[#10b981] p-2 rounded font-bold orbitron text-xs hover:bg-[#10b981]/40 transition-colors btn-glow">
                    DÉMARRER LE HACHEUR
                </button>
                <button onclick="exportCSV()" class="w-full bg-transparent text-[#94a3b8] border border-slate-600 p-2 rounded font-bold orbitron text-[10px] uppercase tracking-widest hover:bg-slate-800 transition-colors">
                    EXPORTER TÉLÉMÉTRIE (CSV)
                </button>
            </div>
        </div>

        <!-- ZONE DE SCHÉMATIQUE (Centre) -->
        <div class="lg:col-span-4 panel rounded-2xl p-3 flex flex-col relative min-h-[450px]">
            <div class="absolute top-2 left-2 z-10 digital-screen px-2 py-1 text-[9px] text-slate-400 uppercase tracking-widest bg-black/60 flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-red-500 animate-pulse" id="rec-light" style="display:none;"></div>
                Circuit Électrique <span class="text-[#10b981]" id="out-fsw">fsw: 20 kHz</span>
            </div>

            <!-- Conteneur Canvas Synoptique -->
            <div class="w-full bg-[#02040a] rounded border border-slate-700 relative h-[220px] mt-8 flex justify-center items-center">
                <canvas id="circuitCanvas" width="380" height="200"></canvas>
            </div>
            
            <!-- Équations Différentielles Live -->
            <div class="w-full equadif-box p-3 rounded-lg mt-3 text-[10px] text-slate-300">
                <div class="text-[#10b981] font-bold mb-2 uppercase border-b border-slate-700 pb-1">Variables d'État (Espace d'État)</div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <div class="text-[#b026ff] font-bold">Courant Bobine ($\frac{di_L}{dt}$)</div>
                        <div class="font-mono text-[9px] mt-1">Si ON: $(V_{in} - V_{out}) / L$</div>
                        <div class="font-mono text-[9px]">Si OFF: $(-V_{out}) / L$</div>
                        <div class="font-bold text-white mt-1">$\Delta i_L = $ <span id="eq-il">0.00</span> A</div>
                    </div>
                    <div>
                        <div class="text-[#00e1ff] font-bold">Tension Condensateur ($\frac{dv_C}{dt}$)</div>
                        <div class="font-mono text-[9px] mt-1">$(i_L - i_R) / C$</div>
                        <div class="font-mono text-[9px]">$i_R = V_{out} / R$</div>
                        <div class="font-bold text-white mt-1">$\Delta V_{out} = $ <span id="eq-vout">0.00</span> V</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- APPAREIL D'OSCILLOSCOPE (Droite) -->
        <div class="lg:col-span-5 panel rounded-2xl p-4 flex flex-col gap-2">
            <h2 class="orbitron text-md font-bold text-white uppercase tracking-widest border-b border-slate-700 pb-2">
                Oscilloscope Numérique
            </h2>
            
            <!-- Graphes Chart.js -->
            <div class="flex-1 w-full bg-[#010205] rounded border border-slate-700 p-1 relative flex flex-col gap-1 h-[300px]">
                <div class="h-1/3 relative"><canvas id="pwmChart"></canvas></div>
                <div class="h-1/3 relative"><canvas id="ilChart"></canvas></div>
                <div class="h-1/3 relative"><canvas id="voutChart"></canvas></div>
            </div>

            <!-- Télémétrie Dynamique -->
            <div class="grid grid-cols-3 gap-2 mt-2">
                <div class="digital-screen p-2 flex flex-col items-center border-t-2 border-[#00e1ff]">
                    <span class="text-[8px] text-slate-500 uppercase text-center">$V_{out}$ Moyen</span>
                    <span class="text-sm font-bold text-[#00e1ff]" id="out-vavg">0.00 V</span>
                    <span class="text-[8px] text-slate-600 font-mono mt-1">Réf: <span id="out-vref">0.00</span> V</span>
                </div>
                <div class="digital-screen p-2 flex flex-col items-center border-t-2 border-[#b026ff]">
                    <span class="text-[8px] text-slate-500 uppercase text-center">Courant $I_L$ Moyen</span>
                    <span class="text-sm font-bold text-[#b026ff]" id="out-iavg">0.00 A</span>
                    <span class="text-[8px] text-slate-600 font-mono mt-1">Charge: <span id="out-ir">0.00</span> A</span>
                </div>
                <div class="digital-screen p-2 flex flex-col items-center border-t-2 border-[#ff0055]">
                    <span class="text-[8px] text-slate-500 uppercase text-center">Ondulation $\Delta V$</span>
                    <span class="text-sm font-bold text-[#ff0055]" id="out-ripple">0.00 V</span>
                    <span class="text-[8px] text-white font-bold mt-1 py-0.5 px-1 rounded" id="out-mode" style="background:#10b981">Mode CCM</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        // --- ÉTATS GLOBAUX & PHYSIQUE ---
        let simState = {
            vin: 24, alpha: 0.5, L: 0.001, C: 0.0001, R: 10,
            vout: 0, il: 0, t: 0, fsw: 20000 // 20 kHz
        };

        const dt = 1e-7; // Pas d'intégration ultra fin (100 ns) pour la précision
        let isRunning = false;
        let animationFrame;
        let switchState = 0; // 1 = ON, 0 = OFF

        // Historique Oscilloscope
        const MAX_POINTS = 150; 
        let histT = [], histVout = [], histIl = [], histPWM = [];

        // --- CHART.JS SETUP ---
        let pwmChart, ilChart, voutChart;

        function initCharts() {
            Chart.defaults.color = '#64748b';
            Chart.defaults.font.family = 'Rajdhani';
            const commonOptions = {
                responsive: true, maintainAspectRatio: false, animation: false,
                scales: { x: { display: false } },
                plugins: { legend: { display: false }, tooltip: {enabled: false} },
                elements: { point: { radius: 0 } }
            };

            // 1. PWM (Gate)
            pwmChart = new Chart(document.getElementById('pwmChart'), {
                type: 'line',
                data: { labels: histT, datasets: [{ data: histPWM, borderColor: '#f59e0b', borderWidth: 1.5, stepper: true }] },
                options: { ...commonOptions, scales: { x:{display:false}, y: { min: -0.5, max: 1.5, ticks: {display:false} } } }
            });

            // 2. Courant IL
            ilChart = new Chart(document.getElementById('ilChart'), {
                type: 'line',
                data: { labels: histT, datasets: [{ data: histIl, borderColor: '#b026ff', borderWidth: 2, fill: true, backgroundColor: 'rgba(176, 38, 255, 0.1)' }] },
                options: { ...commonOptions, scales: { x:{display:false}, y: { position: 'right', suggestedMin: 0 } } }
            });

            // 3. Tension Vout
            voutChart = new Chart(document.getElementById('voutChart'), {
                type: 'line',
                data: { 
                    labels: histT, 
                    datasets: [
                        { data: histVout, borderColor: '#00e1ff', borderWidth: 2 },
                        { data: [], borderColor: '#ff0055', borderDash: [5,5], borderWidth: 1 } // Ligne de référence
                    ] 
                },
                options: { ...commonOptions, scales: { x:{display:false}, y: { position: 'right', suggestedMin: 0 } } }
            });
        }

        // --- MOTEUR PHYSIQUE (Euler Integration) ---
        function updateParams() {
            simState.vin = parseFloat(document.getElementById('in-vin').value);
            simState.alpha = parseFloat(document.getElementById('in-alpha').value);
            simState.L = parseFloat(document.getElementById('in-l').value) * 1e-3;
            simState.C = parseFloat(document.getElementById('in-c').value) * 1e-6;
            simState.R = parseFloat(document.getElementById('in-r').value);

            document.getElementById('val-vin').innerText = simState.vin.toFixed(1) + " V";
            document.getElementById('val-alpha').innerText = simState.alpha.toFixed(2);
            document.getElementById('val-l').innerText = (simState.L * 1000).toFixed(1) + " mH";
            document.getElementById('val-c').innerText = (simState.C * 1e6).toFixed(0) + " µF";
            document.getElementById('val-r').innerText = simState.R.toFixed(1) + " Ω";
            
            document.getElementById('out-vref').innerText = (simState.vin * simState.alpha).toFixed(2);
        }

        function runPhysics() {
            const T = 1 / simState.fsw; 
            
            // Pour que l'animation soit fluide mais qu'on couvre assez de temps,
            // on calcule N sous-étapes d'Euler par frame d'animation (ex: 200)
            const stepsPerFrame = 200; 

            let vout_min = 9999, vout_max = -9999;
            let il_min = 9999;

            for (let i = 0; i < stepsPerFrame; i++) {
                simState.t += dt;
                const cycleTime = simState.t % T;

                let di_dt = 0;
                // Gestion du rapport cyclique
                if (cycleTime < simState.alpha * T) {
                    switchState = 1; // Interrupteur fermé (Transistor passant)
                    di_dt = (simState.vin - simState.vout) / simState.L;
                } else {
                    switchState = 0; // Interrupteur ouvert (Diode passante)
                    di_dt = -simState.vout / simState.L;
                }

                // La diode empêche le courant IL de devenir négatif dans un hacheur asynchrone (Mode DCM)
                if (switchState === 0 && simState.il <= 0 && di_dt < 0) {
                    simState.il = 0;
                    di_dt = 0;
                }

                const ir = simState.vout / simState.R;
                const dv_dt = (simState.il - ir) / simState.C;

                simState.il += di_dt * dt;
                simState.vout += dv_dt * dt;

                if (simState.vout < 0) simState.vout = 0;

                // Stats pour ripple
                if(simState.vout < vout_min) vout_min = simState.vout;
                if(simState.vout > vout_max) vout_max = simState.vout;
                if(simState.il < il_min) il_min = simState.il;
            }

            // On sauvegarde 1 point par frame pour le Chart.js
            histT.push((simState.t * 1000).toFixed(2)); // ms
            histPWM.push(switchState);
            histIl.push(simState.il);
            histVout.push(simState.vout);

            if (histT.length > MAX_POINTS) {
                histT.shift(); histPWM.shift(); histIl.shift(); histVout.shift();
            }

            // Update UI Equadif
            document.getElementById('eq-il').innerText = (vout_max - vout_min).toFixed(3); // Approximation visuelle UI
            document.getElementById('eq-vout').innerText = (vout_max - vout_min).toFixed(3);
            
            document.getElementById('out-vavg').innerText = simState.vout.toFixed(2) + " V";
            document.getElementById('out-iavg').innerText = simState.il.toFixed(2) + " A";
            document.getElementById('out-ir').innerText = (simState.vout / simState.R).toFixed(2);
            document.getElementById('out-ripple').innerText = (vout_max - vout_min).toFixed(3) + " V";

            const modeBadge = document.getElementById('out-mode');
            if (il_min <= 0.01) {
                modeBadge.innerText = "Mode DCM";
                modeBadge.style.background = "#ff0055"; // Rouge
            } else {
                modeBadge.innerText = "Mode CCM";
                modeBadge.style.background = "#10b981"; // Vert
            }

            // Rafraîchir les graphiques
            pwmChart.update();
            ilChart.update();
            
            // Ligne de référence dynamique Vout théorique = alpha * Vin
            const vRefArray = Array(histVout.length).fill(simState.vin * simState.alpha);
            voutChart.data.datasets[1].data = vRefArray;
            voutChart.update();

            // Dessiner le schéma
            drawSchematic();

            if (isRunning) {
                animationFrame = requestAnimationFrame(runPhysics);
            }
        }

        // --- SCHÉMA ÉLECTRIQUE ANIMÉ (CANVAS) ---
        function drawSchematic() {
            const canvas = document.getElementById('circuitCanvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const w = canvas.width, h = canvas.height;
            ctx.lineWidth = 3;
            ctx.strokeStyle = "#64748b";

            // Points du circuit
            const pVin_top = {x: 40, y: 50};
            const pVin_bot = {x: 40, y: 150};
            const pSwitch_in = {x: 100, y: 50};
            const pSwitch_out = {x: 160, y: 50};
            const pDiode_top = {x: 160, y: 50};
            const pDiode_bot = {x: 160, y: 150};
            const pL_in = {x: 160, y: 50};
            const pL_out = {x: 240, y: 50};
            const pC_top = {x: 240, y: 50};
            const pC_bot = {x: 240, y: 150};
            const pR_top = {x: 320, y: 50};
            const pR_bot = {x: 320, y: 150};

            // Lignes de base (GND)
            ctx.beginPath(); ctx.moveTo(pVin_bot.x, pVin_bot.y); ctx.lineTo(pR_bot.x, pR_bot.y); ctx.stroke();
            // Lignes Hautes
            ctx.beginPath(); ctx.moveTo(pVin_top.x, pVin_top.y); ctx.lineTo(pSwitch_in.x, pSwitch_in.y); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(pSwitch_out.x, pSwitch_out.y); ctx.lineTo(pL_in.x, pL_in.y); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(pL_out.x, pL_out.y); ctx.lineTo(pR_top.x, pR_top.y); ctx.stroke();

            // 1. Source de Tension (Vin)
            ctx.beginPath(); ctx.arc(pVin_top.x, (pVin_top.y + pVin_bot.y)/2, 15, 0, 2*Math.PI); 
            ctx.fillStyle = "#010205"; ctx.fill(); ctx.stroke();
            ctx.fillStyle = "#00e1ff"; ctx.font = "12px Orbitron"; ctx.fillText("Vin", pVin_top.x - 10, (pVin_top.y + pVin_bot.y)/2 + 4);

            // 2. Transistor (Interrupteur)
            ctx.strokeStyle = switchState ? "#10b981" : "#ff0055"; // Vert si fermé, Rouge si ouvert
            ctx.beginPath();
            ctx.moveTo(pSwitch_in.x, pSwitch_in.y);
            if (switchState) {
                ctx.lineTo(pSwitch_out.x, pSwitch_out.y); // Ligne fermée
            } else {
                ctx.lineTo(pSwitch_out.x, pSwitch_out.y - 20); // Ligne levée
            }
            ctx.stroke();

            // 3. Diode
            ctx.strokeStyle = (!switchState && simState.il > 0) ? "#10b981" : "#64748b"; // S'allume si Switch OFF et I_L > 0
            ctx.beginPath(); ctx.moveTo(pDiode_top.x, pDiode_top.y); ctx.lineTo(pDiode_bot.x, pDiode_bot.y); ctx.stroke();
            // Triangle Diode
            ctx.beginPath(); ctx.moveTo(pDiode_top.x - 10, pDiode_top.y + 40); ctx.lineTo(pDiode_top.x + 10, pDiode_top.y + 40); ctx.lineTo(pDiode_top.x, pDiode_top.y + 60); ctx.closePath();
            ctx.fillStyle = ctx.strokeStyle; ctx.fill();
            ctx.beginPath(); ctx.moveTo(pDiode_top.x - 10, pDiode_top.y + 60); ctx.lineTo(pDiode_top.x + 10, pDiode_top.y + 60); ctx.stroke();

            // 4. Inductance (L)
            ctx.strokeStyle = "#b026ff";
            ctx.beginPath();
            for(let i=0; i<4; i++) {
                ctx.arc(pL_in.x + 10 + i*20, pL_in.y, 10, Math.PI, 0);
            }
            ctx.stroke();
            ctx.fillStyle = "#b026ff"; ctx.fillText("L", pL_in.x + 35, pL_in.y - 15);

            // 5. Condensateur (C)
            ctx.strokeStyle = "#64748b";
            ctx.beginPath(); ctx.moveTo(pC_top.x, pC_top.y); ctx.lineTo(pC_top.x, pC_top.y + 45); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(pC_bot.x, pC_bot.y); ctx.lineTo(pC_bot.x, pC_bot.y - 45); ctx.stroke();
            ctx.lineWidth = 5;
            ctx.beginPath(); ctx.moveTo(pC_top.x - 15, pC_top.y + 45); ctx.lineTo(pC_top.x + 15, pC_top.y + 45); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(pC_bot.x - 15, pC_bot.y - 45); ctx.lineTo(pC_bot.x + 15, pC_bot.y - 45); ctx.stroke();
            ctx.fillStyle = "#00e1ff"; ctx.fillText("C", pC_top.x + 20, (pC_top.y + pC_bot.y)/2);

            // 6. Résistance (R)
            ctx.lineWidth = 3;
            ctx.beginPath(); ctx.moveTo(pR_top.x, pR_top.y); ctx.lineTo(pR_top.x, pR_top.y + 30);
            let yy = pR_top.y + 30;
            for(let i=0; i<5; i++) {
                ctx.lineTo(pR_top.x + (i%2===0?10:-10), yy + 8);
                yy += 8;
            }
            ctx.lineTo(pR_bot.x, pR_bot.y); ctx.stroke();
            ctx.fillStyle = "#f59e0b"; ctx.fillText("R", pR_top.x + 20, (pR_top.y + pR_bot.y)/2);
        }

        // --- CONTROLES ---
        function toggleSim() {
            isRunning = !isRunning;
            const btn = document.getElementById('btn-play');
            const recLight = document.getElementById('rec-light');
            if (isRunning) {
                btn.innerText = "PAUSE (HACHAGE)";
                btn.classList.replace('text-[#10b981]', 'text-[#f59e0b]');
                btn.classList.replace('border-[#10b981]', 'border-[#f59e0b]');
                if (recLight) recLight.style.display = "block";
                runPhysics();
            } else {
                btn.innerText = "DÉMARRER LE HACHEUR";
                btn.classList.replace('text-[#f59e0b]', 'text-[#10b981]');
                btn.classList.replace('border-[#f59e0b]', 'border-[#10b981]');
                if (recLight) recLight.style.display = "none";
                cancelAnimationFrame(animationFrame);
            }
        }

        function exportCSV() {
            if(histT.length === 0) return;
            let csv = "data:text/csv;charset=utf-8,";
            csv += "Temps(ms),PWM_State,Courant_L(A),Tension_Vout(V)\n";
            for(let i=0; i<histT.length; i++) {
                csv += `${histT[i]},${histPWM[i]},${histIl[i].toFixed(4)},${histVout[i].toFixed(4)}\n`;
            }
            const link = document.createElement("a");
            link.href = encodeURI(csv);
            link.download = `LeWelt_Buck_Converter.csv`;
            document.body.appendChild(link); link.click(); document.body.removeChild(link);
        }

        // Init
        window.onload = () => {
            initCharts();
            updateParams();
            drawSchematic();
        };
    </script>
</body>
</html>