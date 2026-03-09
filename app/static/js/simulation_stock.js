<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Le Welt - Optimisation Logistique & Flux</title>
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
            --neon-red: #ff0055;
            --neon-orange: #f59e0b;
        }

        body {
            background-color: var(--tech-dark);
            color: #e2e8f0;
            font-family: 'Rajdhani', sans-serif;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(0, 225, 255, 0.05) 0%, transparent 60%),
                linear-gradient(to right, rgba(0, 225, 255, 0.02) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(0, 225, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 40px 40px, 40px 40px;
        }

        .orbitron { font-family: 'Orbitron', sans-serif; }

        .panel {
            background: var(--tech-panel);
            border: 1px solid rgba(0, 225, 255, 0.2);
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(0, 225, 255, 0.05);
            backdrop-filter: blur(12px);
        }

        input[type="range"] {
            -webkit-appearance: none; width: 100%; height: 4px;
            background: rgba(255, 255, 255, 0.1); border-radius: 5px; outline: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none; appearance: none; width: 14px; height: 14px;
            border-radius: 50%; background: var(--neon-cyan); cursor: pointer;
            box-shadow: 0 0 10px var(--neon-cyan); transition: transform 0.2s;
        }
        input[type="range"]::-webkit-slider-thumb:hover { transform: scale(1.3); }

        .digital-screen {
            background: #000; border: 1px solid #1e293b; border-radius: 6px;
            font-family: 'Orbitron', monospace; box-shadow: inset 0 0 15px rgba(0,0,0,0.8);
        }

        .btn-glow:hover { box-shadow: 0 0 15px currentColor; }
        
        .equadif-box {
            font-family: 'Courier New', Courier, monospace;
            background: rgba(0, 0, 0, 0.6);
            border-left: 3px solid var(--neon-purple);
        }
    </style>
</head>
<body class="min-h-screen p-4 flex flex-col items-center">

    <div class="w-full max-w-[1400px] mb-4 text-center">
        <h1 class="text-3xl md:text-4xl font-black orbitron text-transparent bg-clip-text bg-gradient-to-r from-[#00e1ff] via-[#b026ff] to-[#ff0055] tracking-widest uppercase">
            LABORATOIRE LE WELT : OPTIMISATION & FLUX STOCHASTIQUES
        </h1>
        <p class="text-slate-400 font-bold tracking-widest mt-1 uppercase text-xs md:text-sm">
            Modèle de Wilson (EOQ), Bruit Aléatoire & Minimisation des Coûts
        </p>
    </div>

    <div class="w-full max-w-[1400px] grid grid-cols-1 lg:grid-cols-12 gap-4 h-full">
        
        <!-- PANNEAU DE CONTRÔLE (Gauche) -->
        <div class="lg:col-span-3 panel rounded-2xl p-4 flex flex-col gap-4">
            <h2 class="orbitron text-md font-bold text-[#00e1ff] border-b border-[#00e1ff]/30 pb-2 flex justify-between items-center">
                <span>VARIABLES D'ÉTAT</span>
                <span class="text-[9px] bg-[#00e1ff]/20 px-2 py-1 rounded text-white">SUPPLY CHAIN</span>
            </h2>

            <div class="space-y-4">
                <!-- Demande Annuelle -->
                <div>
                    <label class="flex justify-between text-[10px] font-bold text-slate-300 uppercase mb-1">
                        <span>Demande Annuelle ($D$)</span>
                        <span id="val-d" class="text-[#00e1ff]">12000 u/an</span>
                    </label>
                    <input type="range" id="in-d" min="1000" max="50000" step="1000" value="12000" oninput="updateSim()">
                </div>

                <!-- Coût Commande -->
                <div>
                    <label class="flex justify-between text-[10px] font-bold text-[#f59e0b] uppercase mb-1">
                        <span>Coût de Commande ($C_c$)</span>
                        <span id="val-cc" class="text-[#f59e0b]">50 €</span>
                    </label>
                    <input type="range" id="in-cc" min="10" max="500" step="10" value="50" style="accent-color: #f59e0b;" oninput="updateSim()">
                    <p class="text-[8px] text-slate-500 mt-1">Coût fixe d'affrètement par transport.</p>
                </div>

                <!-- Coût Stockage -->
                <div>
                    <label class="flex justify-between text-[10px] font-bold text-[#b026ff] uppercase mb-1">
                        <span>Coût Possession ($C_p$)</span>
                        <span id="val-cp" class="text-[#b026ff]">2.0 €/u/an</span>
                    </label>
                    <input type="range" id="in-cp" min="0.1" max="20" step="0.1" value="2.0" style="accent-color: #b026ff;" oninput="updateSim()">
                    <p class="text-[8px] text-slate-500 mt-1">Coût d'immobilisation en entrepôt.</p>
                </div>

                <!-- Logistique -->
                <div class="pt-3 border-t border-slate-700">
                    <h3 class="text-[10px] font-bold text-[#10b981] uppercase mb-2">Paramètres Logistiques</h3>
                    <div class="mb-3">
                        <label class="flex justify-between text-[9px] font-bold text-slate-400 uppercase mb-1">
                            <span>Délai de Livraison ($L$)</span>
                            <span id="val-lead">5 jours</span>
                        </label>
                        <input type="range" id="in-lead" min="1" max="30" step="1" value="5" style="accent-color: #10b981;" oninput="updateSim()">
                    </div>
                    <div class="mb-3">
                        <label class="flex justify-between text-[9px] font-bold text-slate-400 uppercase mb-1">
                            <span>Stock de Sécurité ($SS$)</span>
                            <span id="val-ss">50 u</span>
                        </label>
                        <input type="range" id="in-ss" min="0" max="500" step="10" value="50" style="accent-color: #10b981;" oninput="updateSim()">
                    </div>
                    <div>
                        <label class="flex justify-between text-[9px] font-bold text-[#ff0055] uppercase mb-1">
                            <span>Bruit Aléatoire (Stochastique)</span>
                            <span id="val-noise">0%</span>
                        </label>
                        <input type="range" id="in-noise" min="0" max="100" step="5" value="0" style="accent-color: #ff0055;" oninput="updateSim()">
                        <p class="text-[8px] text-slate-500 mt-1">Simule des pics de demande imprévus.</p>
                    </div>
                </div>
            </div>
            
            <div class="mt-auto pt-2">
                <button onclick="exportCSV()" class="w-full bg-[#00e1ff]/20 text-[#00e1ff] border border-[#00e1ff] p-2 rounded font-bold orbitron text-xs hover:bg-[#00e1ff]/40 transition-colors btn-glow">
                    EXPORTER TÉLÉMÉTRIE (CSV)
                </button>
            </div>
        </div>

        <!-- ZONE D'ANALYSE TEMPORELLE (Centre) -->
        <div class="lg:col-span-6 panel rounded-2xl p-4 flex flex-col relative min-h-[450px]">
            <div class="flex justify-between items-center mb-2 border-b border-slate-700 pb-2">
                <h2 class="orbitron text-md font-bold text-white uppercase tracking-widest">Évolution des Stocks</h2>
                <span class="text-[9px] text-[#10b981] bg-[#10b981]/10 px-2 py-1 rounded font-mono">Horizon: 365 Jours</span>
            </div>

            <!-- Conteneur WebGL -->
            <div class="w-full flex-1 bg-[#010205] rounded border border-slate-700 p-2 relative min-h-[300px]">
                <canvas id="timeChart"></canvas>
            </div>
            
            <!-- Équations d'Optimisation -->
            <div class="w-full equadif-box p-3 rounded-lg mt-3 text-[11px] text-slate-300">
                <div class="text-[#b026ff] font-bold mb-2 uppercase border-b border-slate-700 pb-1">Modèle d'Optimisation d'Harris-Wilson (EOQ)</div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <div class="text-slate-400">Quantité Économique de Commande</div>
                        <div class="font-bold text-white text-lg mt-1">$Q^* = \sqrt{\frac{2 \cdot D \cdot C_c}{C_p}}$</div>
                    </div>
                    <div class="text-right">
                        <div class="text-[#00e1ff] mb-1">Point de Commande ($R_{op}$)</div>
                        <div class="font-bold">$= (\text{Demande moy.} \times L) + SS$</div>
                        <div class="font-bold text-lg text-[#00e1ff] mt-1"><span id="eq-rop">0</span> unités</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- APPAREIL D'ANALYSE DES COÛTS (Droite) -->
        <div class="lg:col-span-3 panel rounded-2xl p-4 flex flex-col gap-3">
            <h2 class="orbitron text-md font-bold text-white uppercase tracking-widest border-b border-slate-700 pb-2 text-center">
                Analyse des Coûts
            </h2>
            
            <!-- Graphe Chart.js Coûts -->
            <div class="w-full bg-[#010205] rounded border border-slate-700 p-1 relative h-[200px]">
                <canvas id="costChart"></canvas>
            </div>

            <!-- Télémétrie Dynamique -->
            <div class="mt-2 space-y-2">
                <div class="digital-screen p-2 flex justify-between items-center border-l-4 border-[#00e1ff]">
                    <span class="text-[9px] text-slate-400 uppercase">Qte Opti (EOQ)</span>
                    <span class="text-sm font-bold text-[#00e1ff]" id="out-eoq">0 u</span>
                </div>
                <div class="digital-screen p-2 flex justify-between items-center border-l-4 border-[#f59e0b]">
                    <span class="text-[9px] text-slate-400 uppercase">Nbre Commandes</span>
                    <span class="text-sm font-bold text-[#f59e0b]" id="out-ncmd">0 /an</span>
                </div>
                <div class="digital-screen p-2 flex justify-between items-center border-l-4 border-[#10b981]">
                    <span class="text-[9px] text-slate-400 uppercase">Coût Total Annuel</span>
                    <span class="text-sm font-bold text-[#10b981]" id="out-cost">0 €</span>
                </div>
                
                <!-- Alerte Rupture -->
                <div id="alert-rupture" class="digital-screen p-2 flex flex-col items-center border-t-2 border-[#ff0055] mt-4 opacity-50">
                    <span class="text-[9px] text-[#ff0055] uppercase font-bold animate-pulse">Ruptures de Stock (Pénurie)</span>
                    <span class="text-xl font-bold text-white mt-1" id="out-rupture">0 Jours</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        // --- CHART.JS GLOBALS ---
        let timeChart, costChart;
        let histDays = [], histStock = [], histRop = [], histSS = [];

        function initCharts() {
            Chart.defaults.color = '#64748b';
            Chart.defaults.font.family = 'Rajdhani';

            // 1. Graphe Temporel (Dents de scie)
            const ctxTime = document.getElementById('timeChart').getContext('2d');
            timeChart = new Chart(ctxTime, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Niveau Stock', data: [], borderColor: '#00e1ff', borderWidth: 2, fill: true, backgroundColor: 'rgba(0, 225, 255, 0.1)', pointRadius: 0, stepper: true },
                        { label: 'Point Commande', data: [], borderColor: '#f59e0b', borderWidth: 1, borderDash: [5, 5], pointRadius: 0 },
                        { label: 'Stock Sécurité', data: [], borderColor: '#ff0055', borderWidth: 1, borderDash: [2, 2], pointRadius: 0 }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false, animation: false,
                    scales: { 
                        x: { title: {display: true, text: 'Jours de l\'année'} }, 
                        y: { title: {display: true, text: 'Unités'}, suggestedMin: 0 } 
                    },
                    plugins: { legend: { position: 'top', labels: {boxWidth:10} } }
                }
            });

            // 2. Graphe Optimisation des Coûts
            const ctxCost = document.getElementById('costChart').getContext('2d');
            costChart = new Chart(ctxCost, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Coût Total', data: [], borderColor: '#10b981', borderWidth: 3, pointRadius: 0, tension: 0.4 },
                        { label: 'Coût Possession', data: [], borderColor: '#b026ff', borderWidth: 1, pointRadius: 0 },
                        { label: 'Coût Commande', data: [], borderColor: '#f59e0b', borderWidth: 1, pointRadius: 0 }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false, animation: false,
                    scales: { 
                        x: { display: false }, 
                        y: { display: false, suggestedMin: 0 } 
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }

        // --- MOTEUR DE SIMULATION LOGISTIQUE ---
        function updateSim() {
            // 1. Récupération des Inputs
            const D = parseFloat(document.getElementById('in-d').value);
            const Cc = parseFloat(document.getElementById('in-cc').value);
            const Cp = parseFloat(document.getElementById('in-cp').value);
            const L = parseFloat(document.getElementById('in-lead').value); // Délai livraison
            const SS = parseFloat(document.getElementById('in-ss').value); // Stock Sécurité
            const noisePercent = parseFloat(document.getElementById('in-noise').value) / 100;

            // Mise à jour UI Labels
            document.getElementById('val-d').innerText = D.toFixed(0) + " u/an";
            document.getElementById('val-cc').innerText = Cc.toFixed(0) + " €";
            document.getElementById('val-cp').innerText = Cp.toFixed(1) + " €/u/an";
            document.getElementById('val-lead').innerText = L.toFixed(0) + " jours";
            document.getElementById('val-ss').innerText = SS.toFixed(0) + " u";
            document.getElementById('val-noise').innerText = (noisePercent*100).toFixed(0) + "%";

            // 2. Calculs Analytiques (Modèle de Wilson)
            const Q_opt = Math.sqrt((2 * D * Cc) / Cp);
            const demande_jour_moyenne = D / 365;
            const ROP = (demande_jour_moyenne * L) + SS; // Reorder Point (Point de Commande)

            document.getElementById('eq-rop').innerText = ROP.toFixed(0);
            document.getElementById('out-eoq').innerText = Q_opt.toFixed(0) + " u";
            document.getElementById('out-ncmd').innerText = (D / Q_opt).toFixed(1) + " /an";
            
            const total_cost = (D / Q_opt) * Cc + (Q_opt / 2) * Cp;
            document.getElementById('out-cost').innerText = total_cost.toFixed(0) + " €";

            // 3. Simulation Temporelle (365 jours)
            histDays = []; histStock = []; histRop = []; histSS = [];
            let currentStock = Q_opt + SS;
            let pendingOrderDays = -1;
            let ruptureCount = 0;

            for (let jour = 1; jour <= 365; jour++) {
                // Application de la demande (avec ou sans bruit stochastique)
                // Bruit gaussien simplifié
                let noise = 1.0;
                if (noisePercent > 0) {
                    noise = 1.0 + (Math.random() * 2 - 1) * noisePercent; // +/- noisePercent
                }
                let daily_demand = demande_jour_moyenne * noise;

                currentStock -= daily_demand;

                // Vérification Rupture
                if (currentStock < 0) {
                    ruptureCount++;
                    currentStock = 0; // On ne gère pas le reliquat dans ce modèle simple
                }

                // Livraison d'une commande en attente
                if (pendingOrderDays === 0) {
                    currentStock += Q_opt;
                    pendingOrderDays = -1;
                } else if (pendingOrderDays > 0) {
                    pendingOrderDays--;
                }

                // Déclenchement d'une nouvelle commande si sous le seuil et aucune en cours
                if (currentStock <= ROP && pendingOrderDays < 0) {
                    pendingOrderDays = L;
                }

                histDays.push(jour);
                histStock.push(currentStock);
                histRop.push(ROP);
                histSS.push(SS);
            }

            // Mise à jour de l'Alerte Rupture
            const alertBox = document.getElementById('alert-rupture');
            document.getElementById('out-rupture').innerText = ruptureCount + " Jours";
            if (ruptureCount > 0) {
                alertBox.style.opacity = "1";
                alertBox.style.boxShadow = "inset 0 0 15px rgba(255,0,85,0.5)";
            } else {
                alertBox.style.opacity = "0.5";
                alertBox.style.boxShadow = "none";
            }

            // 4. Génération de la courbe des Coûts
            let costQ = [], costTot = [], costPos = [], costCmd = [];
            // On étudie de Q = 10% de EOQ à 300% de EOQ
            for (let q = Q_opt * 0.2; q <= Q_opt * 3; q += Q_opt * 0.1) {
                costQ.push(q.toFixed(0));
                let cp_val = (q / 2) * Cp;
                let cc_val = (D / q) * Cc;
                costPos.push(cp_val);
                costCmd.push(cc_val);
                costTot.push(cp_val + cc_val);
            }

            // 5. Update Charts
            timeChart.data.labels = histDays;
            timeChart.data.datasets[0].data = histStock;
            timeChart.data.datasets[1].data = histRop;
            timeChart.data.datasets[2].data = histSS;
            timeChart.update();

            costChart.data.labels = costQ;
            costChart.data.datasets[0].data = costTot;
            costChart.data.datasets[1].data = costPos;
            costChart.data.datasets[2].data = costCmd;
            costChart.update();
        }

        // --- EXPORT CSV ---
        function exportCSV() {
            let csv = "data:text/csv;charset=utf-8,";
            csv += "Jour,Niveau_Stock,Seuil_Commande,Stock_Securite\n";
            for(let i=0; i<histDays.length; i++) {
                csv += `${histDays[i]},${histStock[i].toFixed(2)},${histRop[i].toFixed(2)},${histSS[i].toFixed(2)}\n`;
            }
            const link = document.createElement("a");
            link.href = encodeURI(csv);
            link.download = `LeWelt_SupplyChain_Sim.csv`;
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