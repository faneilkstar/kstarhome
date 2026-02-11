# 🔄 MIGRATION VERS POSTGRESQL (Données permanentes)

## ❌ PROBLÈME ACTUEL

Avec SQLite sur Render :
- ✅ Les données existent localement sur votre PC
- ❌ Les données sont **PERDUES à chaque redéploiement** sur Render
- ❌ SQLite n'est pas fait pour la production web

## ✅ SOLUTION : PostgreSQL

PostgreSQL est une base de données **permanente** et **professionnelle**.

---

## 📋 ÉTAPE 1 : Créer la base PostgreSQL sur Render

1. **Allez sur** : https://dashboard.render.com
2. **Cliquez sur** : "New +" → "PostgreSQL"
3. **Configurez** :
   - **Name** : `kstarhome-db`
   - **Database** : `kstarhome`
   - **User** : `kstarhome_user`
   - **Region** : `Frankfurt (EU Central)` (le plus proche)
   - **Plan** : **Free** (0$/mois)
4. **Cliquez sur** : "Create Database"
5. **Attendez 2-3 minutes** que Render crée la base

---

## 📋 ÉTAPE 2 : Récupérer l'URL de connexion

1. Sur la page de votre base PostgreSQL
2. **Cherchez** : "Internal Database URL"
3. **Copiez** l'URL (elle ressemble à) :
   ```
   postgresql://kstarhome_user:mot_de_passe@...
   ```
4. **GARDEZ cette URL secrète** (ne la partagez jamais)

---

## 📋 ÉTAPE 3 : Configurer votre application Render

1. **Allez sur** : https://dashboard.render.com
2. **Cliquez sur** : Votre service `kstarhome`
3. **Allez dans** : "Environment" (menu de gauche)
4. **Ajoutez une variable** :
   - **Key** : `DATABASE_URL`
   - **Value** : L'URL PostgreSQL que vous avez copiée
5. **Cliquez sur** : "Save Changes"

---

## 📋 ÉTAPE 4 : Initialiser la base PostgreSQL

### Méthode 1 : Via le Shell Render (Recommandé)

1. Sur Render, allez dans votre service `kstarhome`
2. Cliquez sur "Shell" (menu de gauche)
3. **Tapez** :
   ```bash
   python init_database.py
   ```
4. Attendez le message "✅ Base de données initialisée"

### Méthode 2 : Script automatique

Le fichier `init_database.py` détecte automatiquement PostgreSQL et crée :
- ✅ Les tables
- ✅ Le compte admin
- ✅ Les comptes de test

---

## 📋 ÉTAPE 5 : Redéployer l'application

1. **Faites un push** :
   ```bash
   git add .
   git commit -m "🔄 Migration PostgreSQL"
   git push origin main
   ```
2. **Render redéploie automatiquement** (3-5 min)
3. **Vérifiez** que le site fonctionne

---

## ✅ VÉRIFICATION

### Comment savoir si PostgreSQL est utilisé ?

1. **Regardez les logs** sur Render
2. Vous devriez voir :
   ```
   [CONFIG] Base de données : PostgreSQL
   ```
3. **Testez** : Créez un étudiant → Redéployez → L'étudiant est toujours là !

---

## 🆘 EN CAS DE PROBLÈME

### Problème : "Could not connect to database"

**Solution** :
1. Vérifiez que `DATABASE_URL` est bien configurée
2. Vérifiez que la base PostgreSQL est "Available"
3. Redémarrez le service Render

### Problème : "relation does not exist"

**Solution** :
```bash
# Dans le Shell Render
python init_database.py
```

### Problème : "password authentication failed"

**Solution** :
1. Régénérez l'URL depuis Render (Database → Connection String)
2. Remettez à jour `DATABASE_URL` dans Environment

---

## 💾 BACKUP DES DONNÉES

### Sauvegarder la base PostgreSQL

Render fait des **backups automatiques** (plan Free : 7 jours de rétention)

### Sauvegarder manuellement

```bash
# Sur Render Shell
pg_dump $DATABASE_URL > backup.sql
```

### Restaurer depuis un backup

```bash
psql $DATABASE_URL < backup.sql
```

---

## 📊 AVANTAGES DE POSTGRESQL

| Critère | SQLite | PostgreSQL |
|---------|--------|------------|
| **Données permanentes** | ❌ (effacées au redéploiement) | ✅ |
| **Multi-utilisateurs** | ❌ (1 seul à la fois) | ✅ |
| **Performances** | 🟡 (limité) | ✅ (excellent) |
| **Backups auto** | ❌ | ✅ |
| **Production-ready** | ❌ | ✅ |

---

## 🎯 RÉSUMÉ RAPIDE

```bash
# 1. Créer PostgreSQL sur Render (5 min)
# 2. Copier l'URL interne
# 3. Ajouter DATABASE_URL dans Environment
# 4. Lancer init_database.py dans Shell
# 5. Push → Redéploiement automatique
# 6. ✅ VOS DONNÉES SONT PERMANENTES !
```

---

## 🔐 SÉCURITÉ

⚠️ **NE JAMAIS** :
- Partager l'URL PostgreSQL publiquement
- Commiter DATABASE_URL dans Git
- Utiliser le même mot de passe partout

✅ **TOUJOURS** :
- Utiliser des variables d'environnement
- Changer les mots de passe par défaut
- Faire des backups réguliers

---

**© 2026 KstarHome - Migration PostgreSQL**  
*Plus de perte de données !*

