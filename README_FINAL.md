# 🎓 Harmony School - Système de Gestion Universitaire

## ⚡ Démarrage Rapide (3 commandes)

```bash
# 1. Configurer Supabase dans .env (remplacer [TON_MOT_DE_PASSE])
nano .env

# 2. Créer les tables et l'admin
flask db init && flask db migrate -m "Init" && flask db upgrade && python create_admin.py

# 3. Lancer
./start.sh
```

Connectez-vous sur **http://localhost:5000** avec `admin` / `admin123`

---

## 📋 Prérequis

- Python 3.12+
- PostgreSQL (Supabase)
- Git

---

## 🚀 Installation Complète

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd PythonProject3
```

### 2. Créer l'environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurer Supabase
Éditez `.env`:
```bash
SUPABASE_DB_URL=postgresql://postgres.pzzfqduntcmklrakhggy:VOTRE_VRAI_MOT_DE_PASSE@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

### 4. Initialiser la base de données
```bash
flask db init
flask db migrate -m "Migration initiale"
flask db upgrade
python create_admin.py
```

### 5. Lancer
```bash
python run.py
# ou
./start.sh
```

---

## 🌐 Déploiement sur Render

### Configuration Render
1. Connectez votre repo GitHub
2. Variables d'environnement:
   - `SUPABASE_DB_URL`: Votre URL Supabase
   - `SECRET_KEY`: Clé secrète Flask
   - `GEMINI_API_KEY`: (Optionnel) Clé API Gemini
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn run:app`

### Déploiement Automatique
```bash
git add .
git commit -m "Mise à jour"
git push origin main
```
Render redéploie automatiquement!

---

## 📚 Fonctionnalités

### Pour le Directeur
- ✅ Gestion des filières et classes
- ✅ Gestion des enseignants et étudiants
- ✅ Validation des inscriptions avec IA
- ✅ Génération de documents PDF
- ✅ Statistiques et rapports

### Pour les Enseignants
- ✅ Gestion des notes et absences
- ✅ Création de TPs avec IA
- ✅ Évaluation automatique
- ✅ Bibliothèque de cours
- ✅ Rapports personnalisés

### Pour les Étudiants
- ✅ Consultation des notes
- ✅ Laboratoire virtuel avec IA
- ✅ Simulations interactives
- ✅ Bibliothèque de ressources
- ✅ Profil et statistiques

---

## 🤖 Intelligence Artificielle

3 IA spécialisées:
- **ETA** 🔴 - Électronique/Électrotechnique
- **ALPHA** 🟢 - Physique/Mécanique  
- **KAYT** 🟡 - Chimie

Powered by Google Gemini Pro

---

## 🛠️ Structure du Projet

```
PythonProject3/
├── app/
│   ├── models.py          # Modèles BDD
│   ├── routes/            # Contrôleurs
│   ├── services/          # Services IA
│   ├── templates/         # Templates HTML
│   └── static/            # CSS, JS, images
├── migrations/            # Migrations BDD
├── config.py              # Configuration
├── run.py                 # Point d'entrée
├── start.sh               # Script de démarrage
└── requirements.txt       # Dépendances
```

---

## 🔧 Commandes Utiles

### Base de données
```bash
flask db init              # Initialiser migrations
flask db migrate -m "msg"  # Créer migration
flask db upgrade           # Appliquer migration
flask db downgrade         # Annuler migration
```

### Développement
```bash
python run.py              # Lancer en mode dev
./start.sh                 # Lancer avec nettoyage auto
python create_admin.py     # Créer admin
```

### Nettoyage
```bash
rm -rf migrations/         # Supprimer migrations
pkill -f "python.*run.py"  # Tuer processus
lsof -ti:5000 | xargs kill -9  # Libérer port
```

---

## 📖 Documentation

- `SETUP_RAPIDE.md` - Guide de configuration
- `CORRECTIONS_APPLIQUEES.md` - Journal des corrections
- `GUIDE_DEPLOIEMENT_RAPIDE.md` - Déploiement Render

---

## 🐛 Dépannage

### Port 5000 occupé
```bash
./start.sh
# ou
lsof -ti:5000 | xargs kill -9
```

### Erreur Supabase
Vérifiez:
1. Mot de passe dans `.env` (sans crochets `[]`)
2. Port `:6543` (mode pooler)
3. Connexion internet

### Erreur migration
```bash
rm -rf migrations/
flask db init
flask db migrate -m "Reset"
flask db upgrade
```

---

## 👥 Crédits

**Développeur**: Ing. KOISSI-ZO Tonyi Constantin  
**Date**: Février 2026  
**Version**: 3.0  

---

## 📄 Licence

Propriétaire - Harmony University

---

## 🌟 Support

Pour toute question, consultez la documentation ou contactez l'équipe technique.

