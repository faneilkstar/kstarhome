// ============================================================
// SIMULATION STRUCTURES DE LEWIS
// Représentation 2D des molécules, électrons de valence
// ============================================================

const canvas = document.getElementById('scopeCanvas');
const ctx = canvas.getContext('2d');
canvas.width = 800;
canvas.height = 600;

let simState = {
    molecule: 'H2O',
    atomes: [],
    liaisons: [],
    doublets_libres: []
};

// Données atomiques
const atomes_data = {
    'H': { nom: 'Hydrogène', valence: 1, couleur: '#FFFFFF', rayon: 20 },
    'C': { nom: 'Carbone', valence: 4, couleur: '#909090', rayon: 30 },
    'N': { nom: 'Azote', valence: 5, couleur: '#3050F8', rayon: 28 },
    'O': { nom: 'Oxygène', valence: 6, couleur: '#FF0D0D', rayon: 28 },
    'F': { nom: 'Fluor', valence: 7, couleur: '#90E050', rayon: 25 },
    'Cl': { nom: 'Chlore', valence: 7, couleur: '#1FF01F', rayon: 32 },
    'S': { nom: 'Soufre', valence: 6, couleur: '#FFFF30', rayon: 32 }
};

// Bibliothèque de molécules
const molecules = {
    'H2O': {
        nom: 'Eau',
        formule: 'H₂O',
        atomes: [
            { element: 'O', x: 400, y: 300, id: 0 },
            { element: 'H', x: 350, y: 250, id: 1 },
            { element: 'H', x: 450, y: 250, id: 2 }
        ],
        liaisons: [
            { from: 0, to: 1, ordre: 1 },
            { from: 0, to: 2, ordre: 1 }
        ],
        doublets_libres: [
            { atome: 0, angle: 90 },
            { atome: 0, angle: 270 }
        ]
    },
    'CO2': {
        nom: 'Dioxyde de carbone',
        formule: 'CO₂',
        atomes: [
            { element: 'C', x: 400, y: 300, id: 0 },
            { element: 'O', x: 300, y: 300, id: 1 },
            { element: 'O', x: 500, y: 300, id: 2 }
        ],
        liaisons: [
            { from: 0, to: 1, ordre: 2 },
            { from: 0, to: 2, ordre: 2 }
        ],
        doublets_libres: [
            { atome: 1, angle: 45 },
            { atome: 1, angle: 315 },
            { atome: 2, angle: 135 },
            { atome: 2, angle: 225 }
        ]
    },
    'NH3': {
        nom: 'Ammoniac',
        formule: 'NH₃',
        atomes: [
            { element: 'N', x: 400, y: 300, id: 0 },
            { element: 'H', x: 350, y: 250, id: 1 },
            { element: 'H', x: 450, y: 250, id: 2 },
            { element: 'H', x: 400, y: 350, id: 3 }
        ],
        liaisons: [
            { from: 0, to: 1, ordre: 1 },
            { from: 0, to: 2, ordre: 1 },
            { from: 0, to: 3, ordre: 1 }
        ],
        doublets_libres: [
            { atome: 0, angle: 180 }
        ]
    },
    'CH4': {
        nom: 'Méthane',
        formule: 'CH₄',
        atomes: [
            { element: 'C', x: 400, y: 300, id: 0 },
            { element: 'H', x: 350, y: 250, id: 1 },
            { element: 'H', x: 450, y: 250, id: 2 },
            { element: 'H', x: 350, y: 350, id: 3 },
            { element: 'H', x: 450, y: 350, id: 4 }
        ],
        liaisons: [
            { from: 0, to: 1, ordre: 1 },
            { from: 0, to: 2, ordre: 1 },
            { from: 0, to: 3, ordre: 1 },
            { from: 0, to: 4, ordre: 1 }
        ],
        doublets_libres: []
    },
    'C2H4': {
        nom: 'Éthylène',
        formule: 'C₂H₄',
        atomes: [
            { element: 'C', x: 350, y: 300, id: 0 },
            { element: 'C', x: 450, y: 300, id: 1 },
            { element: 'H', x: 300, y: 250, id: 2 },
            { element: 'H', x: 300, y: 350, id: 3 },
            { element: 'H', x: 500, y: 250, id: 4 },
            { element: 'H', x: 500, y: 350, id: 5 }
        ],
        liaisons: [
            { from: 0, to: 1, ordre: 2 },
            { from: 0, to: 2, ordre: 1 },
            { from: 0, to: 3, ordre: 1 },
            { from: 1, to: 4, ordre: 1 },
            { from: 1, to: 5, ordre: 1 }
        ],
        doublets_libres: []
    }
};

function generateControls() {
    const container = document.getElementById('controls-container');
    container.innerHTML = `
        <div class="col-md-6">
            <label class="form-label"><strong>Choisir une molécule</strong></label>
            <select id="molecule_select" class="form-select" onchange="changerMolecule()">
                <option value="H2O">Eau (H₂O)</option>
                <option value="CO2">Dioxyde de carbone (CO₂)</option>
                <option value="NH3">Ammoniac (NH₃)</option>
                <option value="CH4">Méthane (CH₄)</option>
                <option value="C2H4">Éthylène (C₂H₄)</option>
            </select>
        </div>
        <div class="col-md-6">
            <label class="form-label"><strong>Informations</strong></label>
            <div id="molecule-info" class="alert alert-info mb-0">
                <strong>Nom :</strong> <span id="nom-molecule">Eau</span><br>
                <strong>Formule :</strong> <span id="formule-molecule">H₂O</span><br>
                <strong>Électrons de valence :</strong> <span id="electrons-valence">8</span>
            </div>
        </div>
        <div class="col-12 mt-2">
            <div class="alert alert-success">
                <strong>🎯 Règle de l'octet :</strong> Chaque atome cherche à avoir 8 électrons de valence (sauf H qui en veut 2).
            </div>
        </div>
    `;
}

function changerMolecule() {
    const select = document.getElementById('molecule_select').value;
    simState.molecule = select;
    chargerMolecule(select);
    dessinerMolecule();
}

function chargerMolecule(nom) {
    const mol = molecules[nom];

    simState.atomes = mol.atomes;
    simState.liaisons = mol.liaisons;
    simState.doublets_libres = mol.doublets_libres;

    // Mettre à jour les infos
    document.getElementById('nom-molecule').innerText = mol.nom;
    document.getElementById('formule-molecule').innerText = mol.formule;

    // Calculer électrons de valence
    let total_electrons = 0;
    mol.atomes.forEach(a => {
        total_electrons += atomes_data[a.element].valence;
    });
    document.getElementById('electrons-valence').innerText = total_electrons;
}

function dessinerMolecule() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Dessiner les liaisons
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#000';

    simState.liaisons.forEach(liaison => {
        const atome1 = simState.atomes[liaison.from];
        const atome2 = simState.atomes[liaison.to];

        const dx = atome2.x - atome1.x;
        const dy = atome2.y - atome1.y;
        const dist = Math.sqrt(dx*dx + dy*dy);

        // Vecteur perpendiculaire pour liaisons multiples
        const perpX = -dy / dist;
        const perpY = dx / dist;

        if (liaison.ordre === 1) {
            // Liaison simple
            ctx.beginPath();
            ctx.moveTo(atome1.x, atome1.y);
            ctx.lineTo(atome2.x, atome2.y);
            ctx.stroke();
        } else if (liaison.ordre === 2) {
            // Liaison double
            const offset = 5;
            ctx.beginPath();
            ctx.moveTo(atome1.x + perpX * offset, atome1.y + perpY * offset);
            ctx.lineTo(atome2.x + perpX * offset, atome2.y + perpY * offset);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(atome1.x - perpX * offset, atome1.y - perpY * offset);
            ctx.lineTo(atome2.x - perpX * offset, atome2.y - perpY * offset);
            ctx.stroke();
        }
    });

    // Dessiner les doublets non liants
    simState.doublets_libres.forEach(doublet => {
        const atome = simState.atomes[doublet.atome];
        const data = atomes_data[atome.element];
        const rayon = data.rayon + 10;

        const angle_rad = doublet.angle * Math.PI / 180;
        const x = atome.x + Math.cos(angle_rad) * rayon;
        const y = atome.y + Math.sin(angle_rad) * rayon;

        // Dessiner deux points (doublet)
        ctx.fillStyle = '#FF0000';
        ctx.beginPath();
        ctx.arc(x - 3, y, 3, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.arc(x + 3, y, 3, 0, Math.PI * 2);
        ctx.fill();
    });

    // Dessiner les atomes
    simState.atomes.forEach(atome => {
        const data = atomes_data[atome.element];

        // Cercle
        ctx.fillStyle = data.couleur;
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(atome.x, atome.y, data.rayon, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Symbole
        ctx.fillStyle = '#000';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(atome.element, atome.x, atome.y);
    });
}

function getParametresActuels() {
    return {
        molecule: simState.molecule,
        formule: molecules[simState.molecule].formule,
        nom: molecules[simState.molecule].nom
    };
}

function getResultatsActuels() {
    const mol = molecules[simState.molecule];

    let total_electrons = 0;
    mol.atomes.forEach(a => {
        total_electrons += atomes_data[a.element].valence;
    });

    const nb_liaisons = mol.liaisons.reduce((sum, l) => sum + l.ordre, 0);
    const nb_doublets_libres = mol.doublets_libres.length;

    return {
        Electrons_valence_total: total_electrons,
        Nombre_liaisons: nb_liaisons,
        Doublets_non_liants: nb_doublets_libres,
        Electrons_liants: nb_liaisons * 2,
        Electrons_non_liants: nb_doublets_libres * 2
    };
}

generateControls();
chargerMolecule('H2O');
dessinerMolecule();

// Redessiner en boucle pour animations futures
setInterval(dessinerMolecule, 100);