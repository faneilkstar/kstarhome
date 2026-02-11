# 🚀 GUIDE DE DÉPLOIEMENT RAPIDE - KSTARHOME
## ✅ Corrections Appliquées (11 Février 2026)
Tous les bugs ont été corrigés :
- ✅ Laboratoire Virtuel - Hub Directeur fonctionnel
- ✅ Bibliothèque Infinie - Template corrigé
- ✅ Affectation UE - Route corrigée
- ✅ Menus - Liens ajoutés partout
---
## 📋 PRÉREQUIS
### Sur votre machine locale
```bash
✅ Git installé
✅ Python 3.12+ installé
✅ Environnement virtuel activé (venv)
✅ Application testée localement
```
### Comptes nécessaires
- [x] Compte GitHub (gratuit)
- [ ] Compte Render (gratuit) - À créer si nécessaire
---
## 🔄 ÉTAPE 1 : Préparer le Repository GitHub
### 1.1 Vérifier la configuration Git
```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
git config --global user.name "KOISSI-ZO Tonyi Constantin"
git config --global user.email "faneilkstar@gmail.com"
```
### 1.2 Créer le repository sur GitHub
1. Aller sur https://github.com
2. Cliquer sur **"New repository"** (bouton vert en haut à droite)
3. Remplir :
   - **Nom du repo** : `kstarhome`
   - **Description** : `Système de gestion académique avec laboratoire virtuel - Ing. KOISSI-ZO Tonyi Constantin`
   - **Visibilité** : Public
   - ⚠️ **NE PAS** cocher "Add a README file"
4. Cliquer sur **"Create repository"**
### 1.3 Initialiser et pousser le code
```bash
# Initialiser le repository local
git init
# Ajouter tous les fichiers
git add .
# Faire le premier commit
git commit -m "🎓 KstarHome v2.0 - Système de gestion académique complet avec laboratoire virtuel"
# Renommer la branche en main
git branch -M main
# Ajouter le remote (remplacer USERNAME par votre nom d'utilisateur GitHub)
git remote add origin https://github.com/USERNAME/kstarhome.git
# Pousser vers GitHub
git push -u origin main
```
**⚠️ IMPORTANT :** Lors du push, GitHub vous demandera vos identifiants :
- **Username** : Votre nom d'utilisateur GitHub
- **Password** : Utilisez un **Personal Access Token** (pas votre mot de passe)
### 1.4 Créer un Personal Access Token (si nécessaire)
1. GitHub → Cliquer sur votre avatar (en haut à droite)
2. **Settings** → **Developer settings** (en bas à gauche)
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token (classic)**
5. Donner un nom : `KstarHome Deploy`
6. Cocher : **repo** (toutes les cases)
7. Cliquer sur **Generate token**
8. ⚠️ **COPIER LE TOKEN IMMÉDIATEMENT** (vous ne pourrez plus le voir)
9. Utiliser ce token comme mot de passe lors du `git push`
---
## 🌐 ÉTAPE 2 : Déployer sur Render
### 2.1 Créer un compte Render
1. Aller sur https://render.com
2. Cliquer sur **"Get Started for Free"**
3. Se connecter avec GitHub (recommandé)
### 2.2 Créer un nouveau Web Service
1. Dans le Dashboard Render, cliquer sur **"New +"**
2. Sélectionner **"Web Service"**
3. Connecter votre repository GitHub `kstarhome`
4. Autoriser Render à accéder au repository
### 2.3 Configurer le Web Service
Remplir les informations suivantes :
**Name** :
```
kstarhome
```
**Region** :
```
Frankfurt (EU Central)
```
(ou choisir la région la plus proche)
**Branch** :
```
main
```
**Runtime** :
```
Python 3
```
**Build Command** :
```bash
pip install -r requirements.txt
```
**Start Command** :
```bash
gunicorn run:app
```
**Instance Type** :
```
Free
```
### 2.4 Variables d'Environnement
Cliquer sur **"Advanced"** puis ajouter ces variables :
| Key | Value |
|-----|-------|
| `FLASK_APP` | `run.py` |
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `votre-cle-secrete-aleatoire-longue` |
| `DATABASE_URL` | (laisser vide, Render le gérera) |
**⚠️ Générer une clé secrète** :
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
### 2.5 Déployer
1. Cliquer sur **"Create Web Service"**
2. Render va :
   - Cloner votre repository
   - Installer les dépendances
   - Lancer l'application
3. ⏳ Attendre 5-10 minutes pour le premier déploiement
### 2.6 Initialiser la Base de Données
Une fois déployé :
1. Dans le Dashboard Render, aller dans votre service `kstarhome`
2. Cliquer sur **"Shell"** (en haut à droite)
3. Exécuter :
```bash
python init_database.py
```
---
## ✅ ÉTAPE 3 : Vérifier le Déploiement
### 3.1 Accéder à l'application
Render vous donnera une URL du type :
```
https://kstarhome.onrender.com
```
### 3.2 Se connecter
```
Username: admin
Password: admin123
```
### 3.3 Tester les fonctionnalités
- [ ] Connexion directeur OK
- [ ] Dashboard affiche les stats
- [ ] Créer une filière
- [ ] Créer une classe
- [ ] Créer un enseignant
- [ ] Créer un étudiant
- [ ] Accéder au Laboratoire Virtuel
- [ ] Accéder à la Bibliothèque Infinie
- [ ] Mode sombre fonctionne
---
## 🔧 DÉPANNAGE
### Problème : Le build échoue
**Solution :**
1. Vérifier que `requirements.txt` est à jour
2. Vérifier que `runtime.txt` existe avec `python-3.12.0`
3. Regarder les logs de build dans Render
### Problème : L'application ne démarre pas
**Solution :**
1. Vérifier les logs dans Render
2. S'assurer que `Procfile` existe avec :
   ```
   web: gunicorn run:app
   ```
3. Vérifier que les variables d'environnement sont bien définies
### Problème : Erreur de base de données
**Solution :**
1. Aller dans Shell Render
2. Supprimer la DB :
   ```bash
   rm -rf instance/*.db
   ```
3. Réinitialiser :
   ```bash
   python init_database.py
   ```
### Problème : "Application Error" après déploiement
**Solution :**
1. Vérifier les logs Render
2. Redémarrer le service
3. Vérifier que toutes les dépendances sont dans `requirements.txt`
---
## 🔄 MISES À JOUR FUTURES
Quand vous modifiez le code :
```bash
# 1. Tester localement
python run.py
# 2. Commiter les changements
git add .
git commit -m "✨ Ajout de nouvelle fonctionnalité"
# 3. Pousser vers GitHub
git push origin main
# 4. Render redéploie automatiquement ! ✅
```
---
## 📊 PERFORMANCES
### Instance Free Render
- ✅ Suffisant pour tests et démonstration
- ✅ 512 MB RAM
- ⚠️ Se met en veille après 15 minutes d'inactivité
- ⚠️ Premier accès peut prendre 30-60 secondes (réveil)
### Pour améliorer les performances
1. Passer à une instance payante ($7/mois)
2. Utiliser une vraie base de données PostgreSQL
3. Ajouter un CDN pour les assets statiques
---
## 🎓 CONFIGURATION PERSONNALISÉE
### Changer le nom de l'école
Dans `app/templates/base.html` :
```html
<div class="brand-logo">
    <i class="fas fa-graduation-cap me-3"></i>VOTRE ÉCOLE
</div>
```
### Changer les couleurs
Dans `app/templates/base.html`, section `:root` :
```css
:root {
    --primary: #6366f1;  /* Votre couleur principale */
    --accent: #06b6d4;   /* Votre couleur d'accent */
}
```
---
## 📞 SUPPORT
### Documentation
- `CORRECTIONS_COMPLETES.md` - Tous les bugs corrigés
- `NOUVELLES_FONCTIONNALITES.md` - Guide du laboratoire virtuel
- `GUIDE_UTILISATEUR_FR.md` - Guide pour les utilisateurs
### En cas de problème
1. Vérifier les logs Render
2. Tester localement avec `python run.py`
3. Vérifier la console du navigateur (F12)
---
## ✅ CHECKLIST FINALE
Avant de déployer, vérifier :
- [ ] `requirements.txt` complet
- [ ] `Procfile` présent
- [ ] `runtime.txt` présent
- [ ] `.gitignore` configuré
- [ ] Variables d'environnement définies
- [ ] Base de données initialisée
- [ ] Application testée localement
- [ ] Repository GitHub créé
- [ ] Code poussé vers GitHub
- [ ] Service Render créé
- [ ] Déploiement réussi
- [ ] Tests de connexion OK
---
## 🎉 FÉLICITATIONS !
Votre application **KstarHome** est maintenant déployée et accessible publiquement !
**URL de votre site** : `https://kstarhome.onrender.com`
---
**Créé par : Ing. KOISSI-ZO Tonyi Constantin**
**Spécialiste en Électronique de Puissance**
**Date : 11 Février 2026**
© 2026 KstarHome - Tous droits réservés
