# 🎓 KstarHome - Système de Gestion Académique

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

> **Système complet de gestion académique moderne avec IA intégrée**

**Créé par : Ing. KOISSI-ZO Tonyi Constantin**  
Spécialiste en Électronique de Puissance

---

## 📋 Description

**KstarHome** est un système complet de gestion académique pour établissements d'enseignement supérieur. Cette application web permet de gérer les étudiants, enseignants, notes, absences, documents pédagogiques et bien plus encore.

### 🌐 Site web : https://kstarhome.onrender.com
## ✨ Fonctionnalités Principales
### 👨‍🎓 Pour les Étudiants
- ✅ Consultation des notes et bulletins
- ✅ Téléchargement de documents pédagogiques
- ✅ Suivi des absences
- ✅ Génération de lettres administratives
- ✅ Emploi du temps personnalisé
- ✅ Bibliothèque numérique
### 👨‍🏫 Pour les Enseignants
- ✅ Saisie des notes avec pondération flexible
- ✅ Gestion des absences
- ✅ Publication de cours et documents
- ✅ Statistiques de classe
- ✅ Export des données (CSV, Excel)
- ✅ Configuration personnalisée des évaluations
### 👨‍💼 Pour les Directeurs
- ✅ Gestion complète des utilisateurs
- ✅ Création de filières et classes
- ✅ Attribution des UE aux enseignants
- ✅ Statistiques avancées
- ✅ Génération de rapports PDF
- ✅ Programmation des examens
- ✅ Génération de diplômes
## 🚀 Installation Rapide
### Prérequis
- Python 3.12+
- pip
- virtualenv (recommandé)
### Installation
```bash
# Cloner le repository
git clone https://github.com/votre-username/academique-polytech.git
cd academique-polytech
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
# Installer les dépendances
pip install -r requirements.txt
# Initialiser la base de données
python3 init_database.py
# Lancer l'application
python3 run.py
```
L'application sera accessible sur `http://localhost:5000`
## 🔐 Comptes par défaut
Après l'initialisation, vous pouvez vous connecter avec :
- **Directeur** : `directeur` / `directeur123`
- **Enseignant** : `prof` / `prof123`
- **Étudiant** : `etudiant` / `etudiant123`
⚠️ **Important** : Changez ces mots de passe après la première connexion !
## 📦 Structure du Projet
```
academique-polytech/
├── app/
│   ├── __init__.py
│   ├── models.py                 # Modèles de données
│   ├── routes/                   # Routes de l'application
│   │   ├── auth.py
│   │   ├── directeur.py
│   │   ├── enseignant.py
│   │   └── etudiant.py
│   ├── templates/                # Templates HTML
│   ├── static/                   # Fichiers statiques (CSS, JS, images)
│   └── utils/                    # Utilitaires (PDF, Excel, etc.)
├── instance/                     # Base de données SQLite
├── config.py                     # Configuration
├── run.py                        # Point d'entrée
├── requirements.txt              # Dépendances
└── GUIDE_DEPLOIEMENT.md         # Guide de déploiement
```
## 🎨 Technologies Utilisées
- **Backend** : Flask (Python)
- **Base de données** : SQLite (développement) / PostgreSQL (production)
- **Frontend** : Bootstrap 5, HTML5, CSS3, JavaScript
- **PDF** : ReportLab
- **Graphiques** : Matplotlib, Chart.js
- **Excel** : openpyxl
- **Authentification** : Flask-Login
- **ORM** : SQLAlchemy
## 📱 Fonctionnalités Avancées
### Système de Notes Flexible
- Configuration personnalisée des composantes d'évaluation
- Pondération flexible (Examen, Devoir, TP, etc.)
- Calcul automatique de la note finale
- Support multi-sessions (normale/rattrapage)
### Génération de Documents
- Bulletins de notes avec graphiques
- Attestations de scolarité
- Relevés de notes
- Diplômes personnalisés
- Lettres d'admission/refus
### Statistiques & Rapports
- Tableaux de bord interactifs
- Graphiques de performance
- Analyse par filière/classe
- Export des données
## 🌐 Déploiement
Le projet est prêt pour le déploiement sur plusieurs plateformes :
### Option 1 : Render.com (Recommandé - Gratuit)
```bash
# Fichiers déjà configurés : Procfile, runtime.txt
# Suivez les instructions dans GUIDE_DEPLOIEMENT.md
```
### Option 2 : PythonAnywhere (100% Gratuit)
```bash
# Instructions détaillées dans GUIDE_DEPLOIEMENT.md
```
### Option 3 : Docker
```bash
# Construire et lancer
docker-compose up -d
# Arrêter
docker-compose down
```
### Option 4 : VPS Personnel
```bash
# Utiliser le script interactif
./deploy.sh
```
Consultez [GUIDE_DEPLOIEMENT.md](GUIDE_DEPLOIEMENT.md) pour plus de détails.
## 🔧 Configuration
### Variables d'environnement
Créez un fichier `.env` :
```env
FLASK_ENV=production
SECRET_KEY=votre-cle-secrete-tres-longue
DEBUG=False
DATABASE_URL=sqlite:///instance/academique.db
```
### Génération d'une clé secrète
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
## 📖 Documentation
- [Guide d'installation](INSTALLATION.md)
- [Guide de déploiement](GUIDE_DEPLOIEMENT.md)
- [Guide rapide](GUIDE_RAPIDE.md)
- [Documentation API](docs/API.md) _(à venir)_
## 🤝 Contribution
Les contributions sont les bienvenues ! Pour contribuer :
1. Forkez le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request
## 🐛 Signaler un Bug
Si vous trouvez un bug, veuillez ouvrir une [issue](https://github.com/votre-username/academique-polytech/issues) avec :
- Une description claire du problème
- Les étapes pour reproduire
- Les logs d'erreur
- Votre environnement (OS, Python version, etc.)
## 📝 Licence
Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
## 👨‍💻 Auteur
**Prof. Kstar de la KARTZ**
- GitHub: [@votre-username](https://github.com/votre-username)
- Email: contact@polytechnique.edu
## 🙏 Remerciements
- Bootstrap pour le framework CSS
- Flask pour le framework web
- Tous les contributeurs open-source
## 📸 Captures d'écran
### Dashboard Directeur
![Dashboard Directeur](docs/screenshots/dashboard-directeur.png)
### Saisie des Notes (Enseignant)
![Saisie Notes](docs/screenshots/saisie-notes.png)
### Bulletin Étudiant
![Bulletin](docs/screenshots/bulletin.png)
---
⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile !
**Status** : ✅ Production Ready | Dernière mise à jour : Février 2026
