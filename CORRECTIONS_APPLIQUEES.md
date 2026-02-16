# ✅ CORRECTIONS APPLIQUÉES - Session du 12 Février 2026

## 🔧 Problèmes Résolus

### 1. **Modules Python Manquants**
- ✅ Installé `flask-jwt-extended` 
- ✅ Installé `google-genai` (nouveau package Gemini)
- ✅ Mis à jour tous les imports de `google.generativeai` vers `google.genai`

### 2. **Modèles de Base de Données**
- ✅ Ajouté la relation `sessions_tp` manquante dans le modèle `Etudiant`
- ✅ Supprimé toutes les références au modèle `Directeur` qui n'existe pas
- ✅ Nettoyé toutes les références à "Matiere" (on utilise des UE)

### 3. **Templates Laboratoire**
- ✅ Corrigé `hub_enseignant.html` : utilisation des variables passées depuis la route
- ✅ Corrigé `hub_etudiant.html` : gestion des UE sans enseignants
- ✅ Corrigé les boucles de filtrage des sessions

### 4. **Routes et Contrôleurs**
- ✅ Mis à jour `hub_etudiant()` pour passer `ues_avec_tps`
- ✅ Corrigé les statistiques du hub enseignant

### 5. **Configuration Supabase**
- ✅ Ajouté support Supabase dans `config.py` avec pool de connexions
- ✅ Configuration automatique du port 6543 (pooler mode)
- ✅ Fallback sur SQLite si Supabase non configuré

### 6. **Scripts Utilitaires**
- ✅ Corrigé `create_admin.py` pour créer un admin DIRECTEUR
- ✅ Créé `start.sh` pour démarrage automatique
- ✅ Créé `SETUP_RAPIDE.md` avec guide complet

---

## 📋 Configuration Requise

### Fichier `.env`
```bash
# SUPABASE (Remplacez [TON_MOT_DE_PASSE] par votre vrai mot de passe)
SUPABASE_DB_URL=postgresql://postgres.pzzfqduntcmklrakhggy:[VOTRE_MOT_DE_PASSE]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# FLASK
SECRET_KEY=ma-cle-secrete-super-securisee
FLASK_APP=run.py
FLASK_ENV=development

# GEMINI (Optionnel - pour l'IA)
GEMINI_API_KEY=votre_cle_gemini
```

---

## 🚀 Commandes de Démarrage

### Option 1: Script Automatique
```bash
./start.sh
```

### Option 2: Commandes Manuelles
```bash
# Nettoyer le port
pkill -f "python.*run.py"
lsof -ti:5000 | xargs kill -9

# Activer venv
source venv/bin/activate

# Lancer
python run.py
```

---

## 📦 Migration Supabase (Première fois)

```bash
# 1. Configurer .env avec votre mot de passe Supabase

# 2. Nettoyer
rm -rf migrations/

# 3. Initialiser
flask db init

# 4. Créer migration
flask db migrate -m "Migration Supabase Université"

# 5. Appliquer
flask db upgrade

# 6. Créer admin
python create_admin.py
# (Utilisez les valeurs par défaut: admin/admin123)

# 7. Lancer
python run.py
```

---

## 🎯 Architecture Corrigée

### Modèles Principaux
- ✅ `User` (DIRECTEUR, ENSEIGNANT, ETUDIANT)
- ✅ `Etudiant` (avec relation `sessions_tp`)
- ✅ `Enseignant` (avec propriété `sessions_tp_supervisees`)
- ✅ `UE` (Unités d'Enseignement - pas de matières)
- ✅ `TP` (Travaux Pratiques du laboratoire)
- ✅ `SessionTP` (Sessions de TP des étudiants)

### Relations Importantes
```python
Etudiant.sessions_tp → SessionTP (toutes les sessions de l'étudiant)
Enseignant.tps_crees → TP (TPs créés par l'enseignant)
Enseignant.sessions_tp_supervisees → SessionTP (via TPs créés)
UE.enseignants → many-to-many
```

---

## 🌐 Déploiement Automatique

### GitHub → Render
```bash
git add .
git commit -m "Configuration complète Supabase + Corrections"
git push origin main
```

Render redéploie automatiquement en 3-5 minutes.

---

## ✅ Points Clés à Retenir

1. **Base de données**: Supabase (PostgreSQL cloud) avec port 6543
2. **Environnement**: Python 3.12 avec venv
3. **Modules IA**: google-genai (nouveau package)
4. **Structure**: Université (Licence/Master) avec UE, pas de matières
5. **Rôles**: DIRECTEUR, ENSEIGNANT, ETUDIANT
6. **Laboratoire**: TPs avec IA (ETA, ALPHA, KAYT)

---

## 🔍 Vérifications

### Test de connexion Supabase
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.session.execute(db.text('SELECT 1')); print('✅ Supabase OK')"
```

### Test de création app
```bash
python -c "from app import create_app; app = create_app(); print('✅ App OK')"
```

### Test du port
```bash
python -c "import socket; s = socket.socket(); s.bind(('', 5000)); print('✅ Port 5000 libre'); s.close()"
```

---

## 📞 Support

En cas de problème:
1. Vérifier le fichier `.env` (mot de passe sans crochets)
2. Vérifier que le port 5000 est libre
3. Vérifier les logs: `python run.py 2>&1 | head -50`
4. Consulter `SETUP_RAPIDE.md`

---

**Auteur**: Ing. KOISSI-ZO Tonyi Constantin  
**Date**: 12 Février 2026  
**Version**: Harmony School v3.0 - Université

