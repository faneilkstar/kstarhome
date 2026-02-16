# 🎓 KstarHome - Guide de Démarrage Rapide

## 🚀 Lancement de l'Application

### Méthode 1 : Script Automatique (Recommandé)
```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
./START_APP.sh
```

### Méthode 2 : Commandes Manuelles
```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
source venv/bin/activate
python run.py
```

## 🔑 Connexion

- **URL** : http://127.0.0.1:5000
- **Identifiant** : `admin`
- **Mot de passe** : `admin123`
- **Rôle** : DIRECTEUR

## ✨ Nouvelles Fonctionnalités

### 1. Création d'Enseignant (Champs Complets)
Quand vous créez un enseignant, remplissez maintenant :
- ✅ Nom et Prénom
- ✅ Email professionnel
- ✅ **Date de naissance** 📅
- ✅ **Sexe** 🚻
- ✅ **Téléphone** 📞
- ✅ **Adresse** 🏠
- ✅ Grade académique
- ✅ Domaine d'expertise

**Chemin** : Directeur → Enseignants → Nouvel Enseignant

### 2. Validation Automatique IA des Inscriptions

#### Comment ça marche ?
1. **Étudiant s'inscrit** → Statut "En attente"
2. **Directeur a 48h** pour valider ou refuser
3. **Après 48h sans action** → L'IA valide automatiquement :
   - ✅ Moyenne ≥ 12/20 → **ACCEPTÉ**
   - ❌ Moyenne < 12/20 → **REFUSÉ**

#### Validation Manuelle (Directeur)
**Option 1 : En masse**
- Directeur → Étudiants → Bouton "Validation IA Auto" 🤖
- Tous les étudiants en attente sont traités d'un coup

**Option 2 : Individuel**
- Directeur → Étudiants → Cliquer sur un étudiant
- Bouton "Valider" ou "Refuser"

#### Script de Validation Automatique
```bash
# Lancer manuellement
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
source venv/bin/activate
python validation_auto_inscriptions.py
```

**Pour automatiser (Cron) :**
```bash
crontab -e
# Ajouter :
0 2 * * * cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3 && venv/bin/python validation_auto_inscriptions.py >> /tmp/validation_auto.log 2>&1
```
*(S'exécute tous les jours à 2h du matin)*

## 💾 Base de Données

- **Type** : PostgreSQL (Supabase Cloud)
- **Région** : Irlande (aws-1-eu-west-1)
- **Tables** : 48 tables
- **Sauvegarde** : Automatique sur Supabase

## 📊 Tableaux de Bord

### Directeur
- Gestion des étudiants (validation, refus)
- Gestion des enseignants (création, affectation)
- Gestion des UE (création, attribution)
- Gestion des classes et filières
- Statistiques globales

### Enseignant
- Liste de ses UE
- Saisie des notes
- Gestion des documents de cours
- Création de TPs (Laboratoire virtuel)

### Étudiant
- Inscription en ligne
- Suivi du statut d'inscription
- Consultation des notes
- Accès aux cours et documents
- Laboratoire virtuel (TPs interactifs)

## 🛠️ Commandes Utiles

### Créer un nouvel admin
```bash
python creer_admin_auto.py
```

### Tester la connexion Supabase
```bash
python test_connexion_finale.py
```

### Arrêter l'application
```bash
pkill -9 -f "python.*run.py"
fuser -k 5000/tcp
```

### Voir les logs de validation auto
```bash
tail -f /tmp/validation_auto.log
```

## 🔧 Configuration Avancée

### Modifier le délai de validation auto (48h par défaut)
Éditez `validation_auto_inscriptions.py` ligne 24 :
```python
delai_validation = datetime.utcnow() - timedelta(hours=48)  # Modifier ici
```

### Activer l'IA Gemini
Ajoutez votre clé API dans `.env` :
```bash
GEMINI_API_KEY=votre_cle_api_ici
```

## 📚 Documentation Complète

- `AMELIORATIONS_FINALES_COMPLETE.md` - Toutes les modifications
- `VALIDATION_AUTO_IA.md` - Guide validation automatique
- `GUIDE_UTILISATEUR_FR.md` - Guide utilisateur complet

## 🆘 Problèmes Courants

### Port 5000 occupé
```bash
fuser -k 5000/tcp
```

### Erreur de connexion Supabase
Vérifiez dans `app/__init__.py` que l'URL est :
```python
DB_URL = "postgresql://postgres.pzzfqduntcmklrakhggy:masqquedemort@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
```

### IA ne fonctionne pas
Vérifiez la clé API Gemini dans `.env` ou utilisez le mode fallback (validation par moyenne uniquement)

## ✅ Checklist Post-Installation

- [x] Application démarre correctement
- [x] Connexion avec admin/admin123 fonctionne
- [x] Base Supabase connectée (48 tables)
- [x] Création d'enseignant avec tous les champs
- [x] Script de validation auto testé
- [x] Documentation complète disponible

## 🎉 Tout est Prêt !

Votre plateforme KstarHome est maintenant **100% opérationnelle** avec :
- ✅ Formulaire enseignant complet
- ✅ Validation automatique IA après 48h
- ✅ Base de données cloud Supabase
- ✅ Scripts de démarrage simplifiés

**Bon développement ! 🚀**

