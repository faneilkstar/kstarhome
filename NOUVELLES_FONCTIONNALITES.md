# 🔬 LABORATOIRE VIRTUEL - NOUVELLES FONCTIONNALITÉS

## 📋 Vue d'ensemble

Le module **Laboratoire Virtuel** ajoute des capacités de simulation interactive et d'assistance par IA à KstarHome.

### ✨ Fonctionnalités ajoutées

- 🧪 **TPs Virtuels** : Travaux pratiques avec simulations interactives
- 📊 **6 Types de simulations** :
  - Convertisseur Buck (Électronique de puissance)
  - Traitement du Signal
  - Thermodynamique
  - Mécanique
  - Résistance des Matériaux (RDM)
  - Gestion de Stock
- 🤖 **3 Assistants IA** :
  - **ETA** : Assistant pédagogique général
  - **ALPHA** : Expert en électronique de puissance
  - **KAYT** : Spécialiste des simulations
- 📈 **Suivi des performances** : Notes automatiques et statistiques
- 💬 **Historique des interactions** avec l'IA

---

## 🗃️ Nouveaux Modèles de Base de Données

### 1. **TP** (Travaux Pratiques)
```python
- id, titre, description
- type_simulation (buck, signal, thermo, mecanique, rdm, stock)
- niveau_difficulte (facile, moyen, difficile)
- duree_estimee (minutes)
- objectifs_pedagogiques
- consignes
- parametres_initiaux (JSON)
- criteres_evaluation (JSON)
- createur_id (enseignant)
- ue_id (optionnel)
- statut (actif, archive)
```

### 2. **SessionTP** (Session d'étudiant)
```python
- id, tp_id, etudiant_id
- date_debut, date_fin
- statut (en_cours, termine, abandonne)
- note_finale
- nombre_tentatives
```

### 3. **ResultatSimulation** (Résultats)
```python
- id, session_id
- parametres_entree (JSON)
- resultats_obtenus (JSON)
- graphiques_data (base64)
- note_automatique
- timestamp
```

### 4. **InteractionIA** (Historique IA)
```python
- id, session_id
- question_etudiant
- reponse_ia
- contexte_simulation (JSON)
- timestamp
- ia_nom (ETA, ALPHA, KAYT)
- pertinence_question (1-5)
```

---

## 🚀 Routes Ajoutées

### Pour tous les rôles
- `GET /laboratoire/` - Hub principal (redirige selon le rôle)

### Pour les Directeurs
- `GET /laboratoire/directeur` - Hub directeur avec statistiques globales

### Pour les Enseignants
- `GET /laboratoire/enseignant` - Hub enseignant
- `GET /laboratoire/creer-tp` - Formulaire de création de TP
- `POST /laboratoire/creer-tp` - Créer un TP
- `GET /laboratoire/editer-tp/<id>` - Éditer un TP
- `POST /laboratoire/editer-tp/<id>` - Sauvegarder modifications
- `POST /laboratoire/supprimer-tp/<id>` - Supprimer un TP
- `GET /laboratoire/tp/<id>` - Détails d'un TP

### Pour les Étudiants
- `GET /laboratoire/etudiant` - Hub étudiant
- `POST /laboratoire/demarrer-tp/<id>` - Démarrer une session
- `GET /laboratoire/salle/<session_id>` - Salle de TP virtuelle
- `POST /laboratoire/terminer-session/<id>` - Terminer une session
- `GET /laboratoire/resultat/<session_id>` - Voir les résultats

### API (AJAX)
- `POST /laboratoire/api/sauvegarder-resultat` - Sauvegarder un résultat de simulation
- `POST /laboratoire/api/poser-question-ia` - Poser une question à l'IA

---

## 📁 Fichiers Créés/Modifiés

### Nouveaux fichiers
```
app/routes/laboratoire.py              # Routes du laboratoire
migration_laboratoire.py                # Script de migration DB
NOUVELLES_FONCTIONNALITES.md           # Cette documentation
```

### Fichiers modifiés
```
app/__init__.py                        # Enregistrement du blueprint
app/models.py                          # Modèles déjà présents
app/templates/enseignant/base.html     # Lien laboratoire
app/templates/etudiant/dashboard_admis.html  # Lien laboratoire
```

### Templates déjà présents
```
app/templates/laboratoire/hub_directeur.html
app/templates/laboratoire/hub_enseignant.html
app/templates/laboratoire/hub_etudiant.html
app/templates/laboratoire/creer_tp.html
app/templates/laboratoire/editer_tp.html
app/templates/laboratoire/detail_tp.html
app/templates/laboratoire/salle_tp.html
app/templates/laboratoire/resultat_tp.html
```

### Scripts JavaScript de simulation déjà présents
```
app/static/js/simulation_buck.js
app/static/js/simulation_signal.js
app/static/js/simulation_thermo.js
app/static/js/simulation_mecanique.js
app/static/js/simulation_rdm.js
app/static/js/simulation_stock.js
```

---

## 🔧 Installation et Migration

### 1. Mettre à jour la base de données

```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3

# Exécuter le script de migration
python migration_laboratoire.py
```

### 2. Vérifier l'installation

```bash
# Lancer l'application
python run.py

# Accéder au laboratoire :
# - Enseignant : http://localhost:5000/laboratoire/enseignant
# - Étudiant : http://localhost:5000/laboratoire/etudiant
# - Directeur : http://localhost:5000/laboratoire/directeur
```

---

## 📖 Guide d'utilisation

### Pour les Enseignants

#### Créer un TP
1. Accéder au **Hub Laboratoire** via la sidebar
2. Cliquer sur **"Créer un TP"**
3. Remplir le formulaire :
   - Titre et description
   - Type de simulation
   - Niveau de difficulté
   - Durée estimée
   - Objectifs pédagogiques
   - Consignes
   - Paramètres initiaux (JSON optionnel)
   - Critères d'évaluation (JSON optionnel)
4. Associer à une UE (optionnel)
5. Valider

#### Gérer les TPs
- **Éditer** : Modifier titre, description, paramètres
- **Désactiver** : Changer le statut en "archivé"
- **Supprimer** : Impossible si des sessions sont en cours
- **Voir les stats** : Nombre de sessions, notes moyennes

### Pour les Étudiants

#### Réaliser un TP
1. Accéder au **Hub Laboratoire**
2. Voir la liste des TPs disponibles
3. Cliquer sur **"Démarrer"**
4. Dans la salle de TP :
   - Lire les consignes
   - Ajuster les paramètres de simulation
   - Lancer la simulation
   - Observer les résultats (graphiques, valeurs)
   - Poser des questions à l'IA si besoin
   - Sauvegarder les résultats
5. Terminer la session
6. Voir la note et les feedbacks

#### Interagir avec l'IA
- **ETA** : Questions pédagogiques générales
- **ALPHA** : Questions techniques (électronique de puissance)
- **KAYT** : Questions sur les simulations

---

## 🎨 Types de Simulations

### 1. Convertisseur Buck
- **Type** : `buck`
- **Domaine** : Électronique de puissance
- **Paramètres** : Tension entrée, tension sortie, fréquence, inductance, capacité
- **Résultats** : Formes d'onde, rendement, ondulation

### 2. Traitement du Signal
- **Type** : `signal`
- **Domaine** : Traitement numérique du signal
- **Paramètres** : Signal d'entrée, filtres, fréquence d'échantillonnage
- **Résultats** : Spectres, signaux filtrés, FFT

### 3. Thermodynamique
- **Type** : `thermo`
- **Domaine** : Transferts thermiques
- **Paramètres** : Températures, matériaux, géométrie
- **Résultats** : Profils de température, flux thermiques

### 4. Mécanique
- **Type** : `mecanique`
- **Domaine** : Mécanique générale
- **Paramètres** : Forces, masses, vitesses
- **Résultats** : Trajectoires, énergies

### 5. RDM
- **Type** : `rdm`
- **Domaine** : Résistance des matériaux
- **Paramètres** : Charges, géométrie, matériau
- **Résultats** : Contraintes, déformations, diagrammes

### 6. Gestion de Stock
- **Type** : `stock`
- **Domaine** : Logistique
- **Paramètres** : Demande, coûts, délais
- **Résultats** : Niveau de stock optimal, coûts

---

## 🤖 Système d'IA

### Assistants disponibles

#### ETA (Assistant Pédagogique)
- Aide à comprendre les consignes
- Explique les concepts
- Guide l'étudiant pas à pas

#### ALPHA (Expert Électronique)
- Spécialiste en électronique de puissance
- Aide sur les convertisseurs
- Explique les phénomènes physiques

#### KAYT (Expert Simulation)
- Aide à interpréter les résultats
- Explique les graphiques
- Suggestions d'optimisation

### Fonctionnement
1. L'étudiant pose une question
2. Le système envoie : question + contexte (paramètres, résultats)
3. L'IA génère une réponse adaptée
4. L'interaction est sauvegardée
5. L'enseignant peut voir l'historique

---

## 📊 Évaluation Automatique

### Critères d'évaluation (JSON)

Exemple de critères pour un TP Buck :

```json
{
  "tension_sortie": {
    "cible": 12.0,
    "tolerance": 0.5,
    "points": 5
  },
  "ondulation": {
    "max": 0.1,
    "points": 3
  },
  "rendement": {
    "min": 0.85,
    "points": 2
  }
}
```

### Calcul de la note
- Comparaison automatique résultats/critères
- Attribution des points
- Note sur 20
- Feedback automatique

---

## 🔄 Déploiement

### Sur le serveur local
```bash
# 1. Migrer la base de données
python migration_laboratoire.py

# 2. Redémarrer l'application
./liberer_port5000.sh
python run.py
```

### Sur Render.com
```bash
# 1. Commit et push
git add .
git commit -m "✨ Ajout du laboratoire virtuel avec simulations et IA"
git push

# 2. Render redéploiera automatiquement

# 3. Dans Shell Render, migrer la DB
python migration_laboratoire.py
```

---

## 🆘 Dépannage

### Les tables ne sont pas créées
```bash
python migration_laboratoire.py
```

### Erreur "laboratoire_bp not found"
Vérifier que le blueprint est bien enregistré dans `app/__init__.py`

### Les simulations ne fonctionnent pas
Vérifier que les fichiers JS sont présents dans `app/static/js/`

### L'IA ne répond pas
Vérifier la route `/laboratoire/api/poser-question-ia` et les logs

---

## 📈 Statistiques et Métriques

### Pour les Enseignants
- Nombre de sessions par TP
- Taux de complétion
- Note moyenne
- Temps moyen de réalisation
- Questions fréquentes posées à l'IA

### Pour les Directeurs
- Total de TPs créés
- TPs par type de simulation
- Activité globale
- Performance moyenne par filière

---

## 🎯 Prochaines Améliorations

- [ ] Export des résultats en PDF
- [ ] Comparaison de résultats entre étudiants
- [ ] Mode collaboratif (TPs en groupe)
- [ ] Plus de types de simulations
- [ ] IA plus avancée avec modèles de langage
- [ ] Certification des compétences acquises
- [ ] Leaderboard et gamification

---

## 📞 Support

Pour toute question sur le laboratoire virtuel :
- Consulter cette documentation
- Vérifier les logs dans `logs/`
- Contacter l'administrateur

---

**© 2026 KstarHome - Laboratoire Virtuel**  
**Créé par : Ing. KOISSI-ZO Tonyi Constantin**  
**Spécialiste en Électronique de Puissance**

