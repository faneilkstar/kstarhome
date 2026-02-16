# 🚀 GUIDE COMPLET SUPABASE POUR KSTAR-HOME

## 📖 TABLE DES MATIÈRES
1. [Pourquoi Supabase ?](#pourquoi-supabase)
2. [Configuration Rapide](#configuration-rapide)
3. [Migration des Données](#migration-des-données)
4. [Déploiement sur Render](#déploiement-sur-render)
5. [Dépannage](#dépannage)

---

## ✨ POURQUOI SUPABASE ?

### Avantages
- ✅ **GRATUIT** : 500 MB de base PostgreSQL gratuite
- ✅ **Cloud** : Accessible partout, toujours en ligne
- ✅ **Performant** : PostgreSQL optimisé
- ✅ **Backups** : Sauvegardes automatiques
- ✅ **Dashboard** : Interface web pour gérer vos données
- ✅ **Scalable** : Peut grandir avec votre projet

### vs SQLite Local
| Critère | SQLite | Supabase |
|---------|--------|----------|
| Hébergement | Fichier local | Cloud |
| Multi-utilisateurs | ❌ Limité | ✅ Excellent |
| Backups | ❌ Manuel | ✅ Automatique |
| Production | ❌ Déconseillé | ✅ Recommandé |
| Prix | Gratuit | Gratuit (500MB) |

---

## ⚡ CONFIGURATION RAPIDE

### Étape 1: Créer un Compte Supabase

1. Allez sur https://supabase.com
2. Cliquez sur **Start your project**
3. Connectez-vous avec GitHub (ou email)
4. C'est gratuit, pas de carte bancaire requise !

### Étape 2: Créer un Projet

1. Cliquez sur **New Project**
2. Remplissez :
   - **Name**: `kstar-home` (ou ce que vous voulez)
   - **Database Password**: Choisissez un mot de passe FORT
     - ⚠️ **IMPORTANT**: Notez-le quelque part !
     - Exemple: `MonMotDePasse2024Secure!`
   - **Region**: `Europe (Frankfurt)` ou proche de vous
3. Cliquez sur **Create new project**
4. ⏳ Attendez 2 minutes (création du projet)

### Étape 3: Récupérer l'URL de Connexion

1. Une fois le projet créé, allez dans **Settings** (⚙️ en bas à gauche)
2. Cliquez sur **Database**
3. Descendez jusqu'à **Connection string**
4. Sélectionnez **Connection pooling** onglet
5. Copiez l'URL qui ressemble à :
   ```
   postgresql://postgres.pzzfqduntcmklrakhggy:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```
6. **Remplacez `[YOUR-PASSWORD]`** par le mot de passe que vous avez créé

### Étape 4: Configurer votre Projet Local

1. **Créer le fichier .env** :
   ```bash
   cp .env.example .env
   nano .env
   ```

2. **Remplir SUPABASE_DB_URL** :
   ```bash
   # Remplacez [TON_MOT_DE_PASSE] par votre vrai mot de passe
   SUPABASE_DB_URL=postgresql://postgres.pzzfqduntcmklrakhggy:MonMotDePasse2024Secure!@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```

3. **Sauvegarder** : Ctrl+O, Enter, Ctrl+X

### Étape 5: Configurer le Pool Size sur Supabase

1. Allez sur votre **Supabase Dashboard**
2. Sélectionnez votre projet
3. Allez dans **Settings** → **Database**
4. Trouvez **Connection pooling**
5. Réglez **Pool Size** à **10**
6. Cliquez sur **Save**

> ⚠️ **Important** : Cette configuration évite les erreurs "too many connections"

### Étape 6: Migrer vers Supabase

**Option 1 : Script automatique** (RECOMMANDÉ)
```bash
# Lance tout le processus automatiquement
./setup_supabase.sh
```

Le script va :
- ✅ Nettoyer les anciens fichiers (migrations, SQLite)
- ✅ Initialiser Flask-Migrate
- ✅ Générer la migration
- ✅ Créer les tables sur Supabase
- ✅ Créer le compte admin
- ✅ Vérifier la connexion

**Option 2 : Manuelle**
```bash
# 1. Supprimer les anciens fichiers
rm -rf migrations
rm -f instance/*.db

# 2. Initialiser les migrations
export FLASK_APP=run.py
flask db init

# 3. Générer la migration
flask db migrate -m "Creation tables Supabase"

# 4. Appliquer sur Supabase
flask db upgrade

# 5. Créer le compte admin
python3 create_admin.py
```

---

## 🔄 MIGRATION DES DONNÉES

### Si vous avez déjà des données dans SQLite

**Option 1 : Tout recommencer** (SIMPLE)
```bash
# Juste lancer la migration, les tables seront vides
python3 migrate_to_supabase.py
```

**Option 2 : Exporter/Importer** (AVANCÉ)
```bash
# 1. Exporter depuis SQLite
sqlite3 instance/academique_dev.db .dump > backup.sql

# 2. Nettoyer le fichier SQL (enlever les spécificités SQLite)
# Éditer backup.sql et supprimer les lignes:
# - BEGIN TRANSACTION;
# - COMMIT;
# - CREATE TABLE sqlite_sequence...

# 3. Importer dans Supabase via le Dashboard
# → Supabase Dashboard → SQL Editor → Coller le contenu → Run
```

**Option 3 : Script Python** (pour plus tard)
```python
# TODO: Script d'import automatique SQLite → Supabase
```

---

## 🚀 DÉPLOIEMENT SUR RENDER

### Étape 1: Ajouter la Variable d'Environnement

1. Allez sur https://dashboard.render.com
2. Sélectionnez votre service Web
3. Allez dans **Environment**
4. Cliquez sur **Add Environment Variable**
5. Ajoutez :
   - **Key**: `SUPABASE_DB_URL`
   - **Value**: `postgresql://postgres.pzzfqduntcmklrakhggy:VotreMotDePasse@aws-0-eu-central-1.pooler.supabase.com:6543/postgres`
6. Cliquez sur **Save Changes**

### Étape 2: Redéployer

**Option A : Automatique** (via GitHub)
```bash
./deploy_auto.sh
```

**Option B : Manuel** (sur Render)
1. Cliquez sur **Manual Deploy** → **Deploy latest commit**
2. Attendez 3-5 minutes

### Étape 3: Initialiser la Base en Production

Après le déploiement, les tables seront créées automatiquement grâce à Flask-Migrate.

Si vous voulez initialiser manuellement :
```bash
# Sur votre machine (avec SUPABASE_DB_URL dans .env)
FLASK_ENV=production python3 migrate_to_supabase.py
```

---

## 🎯 VÉRIFICATION

### Test Local

```bash
# 1. Vérifier que .env contient SUPABASE_DB_URL

# 2. Lancer l'application
python3 run.py

# 3. Accéder à http://localhost:5000
# 4. S'inscrire / Se connecter
# 5. Vérifier que tout fonctionne
```

### Test sur Supabase Dashboard

1. Allez sur https://supabase.com/dashboard
2. Sélectionnez votre projet
3. Cliquez sur **Table Editor** (icône table à gauche)
4. Vous devriez voir vos tables :
   - `user`
   - `etudiant`
   - `enseignant`
   - `ue`
   - `tp`
   - `session_tp`
   - etc.

### Requête SQL de Test

Dans **SQL Editor** (Supabase Dashboard) :
```sql
-- Compter les utilisateurs
SELECT COUNT(*) as nb_users FROM "user";

-- Voir tous les utilisateurs
SELECT id, username, email, role FROM "user";

-- Statistiques
SELECT 
    (SELECT COUNT(*) FROM "user") as users,
    (SELECT COUNT(*) FROM etudiant) as etudiants,
    (SELECT COUNT(*) FROM enseignant) as enseignants,
    (SELECT COUNT(*) FROM tp) as tps;
```

---

## 🐛 DÉPANNAGE

### ❌ Erreur "password authentication failed"

**Cause** : Mauvais mot de passe dans l'URL

**Solution** :
1. Vérifiez que vous avez remplacé `[YOUR-PASSWORD]` par le vrai mot de passe
2. Vérifiez qu'il n'y a pas de caractères spéciaux mal encodés
3. Si le mot de passe contient `@` ou `#`, encodez-le :
   - `@` → `%40`
   - `#` → `%23`

### ❌ Erreur "could not connect to server"

**Cause** : URL incorrecte ou firewall

**Solution** :
1. Vérifiez que vous utilisez le bon port : **6543** (pooler) ou **5432** (direct)
2. Testez votre connexion internet
3. Essayez avec la connexion directe (port 5432) :
   ```
   postgresql://postgres.xxx:password@xxx.supabase.com:5432/postgres
   ```

### ❌ Erreur "relation does not exist"

**Cause** : Les tables n'ont pas été créées

**Solution** :
```bash
# Relancer la migration
python3 migrate_to_supabase.py
```

### ❌ Les données ne s'affichent pas

**Cause** : Base de données vide

**Solution** :
1. Vérifiez que les tables existent (Supabase Dashboard)
2. Créez un utilisateur test
3. Vérifiez dans le Dashboard que l'utilisateur apparaît

### ⚠️ "Pool size exceeded"

**Cause** : Trop de connexions simultanées

**Solution** : Le pooler (port 6543) devrait gérer ça automatiquement.
Si le problème persiste :
```python
# Dans config.py, réduire :
SQLALCHEMY_POOL_SIZE = 3  # Au lieu de 10
SQLALCHEMY_MAX_OVERFLOW = 5  # Au lieu de 20
```

---

## 📊 MONITORING

### Dashboard Supabase

1. **Database** → **Database** : Voir la taille utilisée
2. **Database** → **Roles** : Gérer les accès
3. **Table Editor** : Voir et modifier les données
4. **SQL Editor** : Exécuter des requêtes
5. **Logs** : Voir les erreurs et requêtes

### Backups

Supabase fait des backups automatiques dans le plan gratuit :
- **Point-in-time recovery** : 7 jours
- **Daily backups** : Oui

Pour un backup manuel :
```bash
# Via pg_dump (nécessite PostgreSQL installé localement)
PGPASSWORD=VotreMotDePasse pg_dump \
  -h aws-0-eu-central-1.pooler.supabase.com \
  -p 6543 \
  -U postgres.pzzfqduntcmklrakhggy \
  postgres > backup_$(date +%Y%m%d).sql
```

---

## 🎓 RESSOURCES

- [Documentation Supabase](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy avec PostgreSQL](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)

---

## ✅ CHECKLIST FINALE

- [ ] Compte Supabase créé
- [ ] Projet créé (mot de passe noté !)
- [ ] URL de connexion copiée
- [ ] Fichier `.env` créé et rempli
- [ ] `SUPABASE_DB_URL` configuré (sans `[YOUR-PASSWORD]`)
- [ ] Migration exécutée : `python3 migrate_to_supabase.py`
- [ ] Test local réussi : `python3 run.py`
- [ ] Variable ajoutée sur Render
- [ ] Déploiement effectué
- [ ] Test en production réussi

---

## 🎉 FÉLICITATIONS !

Votre application KSTAR-HOME utilise maintenant Supabase !

**Avantages acquis** :
- ✅ Base de données cloud professionnelle
- ✅ Backups automatiques
- ✅ Scalabilité
- ✅ Dashboard de gestion
- ✅ Prêt pour la production

**Prochaines étapes** :
1. Tester toutes les fonctionnalités
2. Créer des utilisateurs de test
3. Configurer les backups réguliers
4. Monitorer l'utilisation

---

**Version** : 1.0  
**Date** : 2026-02-12  
**Support** : Consultez la documentation Supabase ou ouvrez une issue GitHub

