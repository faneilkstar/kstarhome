# 🚀 Déploiement sur Render.com
Guide complet pour héberger votre application gratuitement sur Render.com
## ✨ Pourquoi Render.com ?
- ✅ **100% Gratuit** avec limite généreuse
- ✅ **SSL automatique** (HTTPS)
- ✅ **Base de données PostgreSQL gratuite**
- ✅ **Déploiement automatique** via Git
- ✅ **Environnement moderne** et facile à utiliser
## 📋 Prérequis
1. Un compte GitHub
2. Votre code sur GitHub
3. Un compte Render.com (gratuit)
## 🔧 Étape 1 : Préparer votre code pour GitHub
### 1.1 Initialiser Git (si pas déjà fait)
```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
git init
```
### 1.2 Ajouter tous les fichiers
```bash
git add .
git commit -m "Initial commit - Ready for deployment"
```
### 1.3 Créer un repository sur GitHub
1. Allez sur https://github.com
2. Cliquez sur "New repository"
3. Nom : `academique-polytech` (ou autre)
4. Cochez "Private" si vous voulez garder le code privé
5. Cliquez sur "Create repository"
### 1.4 Pousser votre code
```bash
# Remplacez 'votre-username' par votre nom d'utilisateur GitHub
git remote add origin https://github.com/votre-username/academique-polytech.git
git branch -M main
git push -u origin main
```
## 🌐 Étape 2 : Créer un compte Render.com
1. Allez sur https://render.com
2. Cliquez sur "Get Started"
3. Connectez-vous avec votre compte GitHub
4. Autorisez Render à accéder à vos repositories
## 🗄️ Étape 3 : Créer la base de données PostgreSQL
### 3.1 Créer la base de données
1. Dans Render Dashboard, cliquez sur "New +"
2. Sélectionnez "PostgreSQL"
3. Remplissez :
   - **Name** : `academique-db`
   - **Database** : `academique`
   - **User** : `academique_user`
   - **Region** : Choisissez le plus proche (ex: Frankfurt)
   - **PostgreSQL Version** : 15
   - **Plan** : **Free** (0$/mois)
4. Cliquez sur "Create Database"
### 3.2 Noter les informations de connexion
Une fois la base créée, copiez :
- ✅ **Internal Database URL** (commence par postgresql://)
- ✅ **External Database URL** (pour se connecter depuis l'extérieur)
💡 **Important** : Gardez ces informations secrètes !
## 🚀 Étape 4 : Déployer l'application Web
### 4.1 Créer le Web Service
1. Dans Render Dashboard, cliquez sur "New +"
2. Sélectionnez "Web Service"
3. Cliquez sur "Connect" à côté de votre repository GitHub
### 4.2 Configuration du service
Remplissez le formulaire :
```
Name: academique-polytech
Region: Frankfurt (ou le même que la DB)
Branch: main
Root Directory: (laisser vide)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn run:app
```
### 4.3 Plan gratuit
- Sélectionnez **Free** (0$/mois)
- Limites: 750 heures/mois (suffisant pour tester)
- L'app s'endort après 15 min d'inactivité
### 4.4 Variables d'environnement
Cliquez sur "Advanced" puis "Add Environment Variable" pour ajouter :
```
FLASK_ENV=production
DEBUG=False
SECRET_KEY=votre-cle-secrete-generee
DATABASE_URL=postgresql://...
```
**Pour générer SECRET_KEY** :
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Copiez le résultat et utilisez-le comme SECRET_KEY.
**Pour DATABASE_URL** :
Collez l'Internal Database URL de l'étape 3.2.
### 4.5 Déployer !
1. Cliquez sur "Create Web Service"
2. Attendez 3-5 minutes pendant le build
3. Votre app sera accessible sur : `https://academique-polytech.onrender.com`
## 🗃️ Étape 5 : Initialiser la base de données
### 5.1 Via Shell Render
1. Allez sur votre Web Service dans Render
2. Cliquez sur "Shell" dans le menu de gauche
3. Exécutez :
```bash
python3 init_database.py
```
Cela créera toutes les tables et les données de test.
## ✅ Étape 6 : Tester l'application
1. Ouvrez `https://votre-app.onrender.com`
2. Connectez-vous avec les comptes par défaut :
   - Directeur : `directeur` / `directeur123`
   - Enseignant : `prof` / `prof123`
   - Étudiant : `etudiant` / `etudiant123`
## 🔄 Déploiement automatique
Chaque fois que vous poussez du code sur GitHub :
```bash
git add .
git commit -m "Nouvelle fonctionnalité"
git push
```
Render redéploiera automatiquement votre app ! 🎉
## 🔧 Configuration avancée
### Domaine personnalisé (optionnel)
1. Allez dans Settings → Custom Domains
2. Ajoutez votre domaine
3. Configurez le DNS selon les instructions
### Logs et monitoring
- **Logs** : Onglet "Logs" pour voir ce qui se passe
- **Metrics** : Onglet "Metrics" pour voir l'utilisation
## ⚠️ Limitations du plan gratuit
- **750 heures/mois** (suffisant pour 1 projet)
- **L'app s'endort** après 15 min sans visite
- **Premier chargement lent** (réveil)
- **512 MB RAM** (suffisant pour cette app)
## 🎯 Pour aller plus loin
### Passer à un plan payant (7$/mois)
Avantages :
- ✅ Pas de sommeil
- ✅ Plus de RAM (1GB+)
- ✅ Scaling automatique
### Backup de la base de données
```bash
# Télécharger la DB
pg_dump DATABASE_URL > backup.sql
# Restaurer
psql DATABASE_URL < backup.sql
```
## 🆘 Dépannage
### L'app ne démarre pas
1. Vérifiez les logs dans Render
2. Vérifiez que `requirements.txt` est complet
3. Vérifiez que `Procfile` est présent
4. Vérifiez les variables d'environnement
### Erreur de base de données
1. Vérifiez que DATABASE_URL est correct
2. Essayez de réinitialiser la DB via Shell
3. Vérifiez que la DB est dans la même région
### L'app est lente
- C'est normal avec le plan gratuit (réveil après 15 min)
- Utilisez un service comme UptimeRobot pour pinger l'app
- Ou passez au plan payant
## 📞 Support
- Documentation Render : https://render.com/docs
- Community Forum : https://community.render.com
---
🎉 **Félicitations !** Votre application est maintenant en ligne et accessible depuis n'importe où dans le monde !
**URL de votre app** : `https://votre-app.onrender.com`
**Prochaines étapes** :
- ✅ Changez tous les mots de passe par défaut
- ✅ Ajoutez vos vraies données
- ✅ Configurez un domaine personnalisé (optionnel)
- ✅ Mettez en place des sauvegardes régulières
