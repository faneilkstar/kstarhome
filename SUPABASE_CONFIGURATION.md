# 🔐 CONFIGURATION SUPABASE - GUIDE COMPLET

## ⚠️ PROBLÈME ACTUEL

L'URL Supabase actuelle dans `.env` est **INCORRECTE** :
```
postgresql://postgres.pzzfqduntcmklrakhggy:masque%20de%20mort@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**Erreur obtenue :** `FATAL: Tenant or user not found`

Cela signifie que soit :
- Le mot de passe est incorrect
- L'ID du projet est incorrect  
- La région est incorrecte

---

## ✅ COMMENT OBTENIR LA BONNE URL

### Étape 1 : Aller sur Supabase

1. Allez sur https://supabase.com
2. Connectez-vous à votre compte
3. Sélectionnez votre projet

### Étape 2 : Obtenir l'URL de connexion

1. Cliquez sur **⚙️ Settings** (dans la sidebar gauche)
2. Cliquez sur **Database** 
3. Descendez jusqu'à **Connection string**
4. **COCHEZ** la case **"Use connection pooling"** ✅
5. Sélectionnez le mode **"Transaction"** (Port 6543)
6. Copiez l'URL qui s'affiche

### Étape 3 : Remplacer `[YOUR-PASSWORD]`

L'URL copiée ressemble à ceci :
```
postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-X-xxx.pooler.supabase.com:6543/postgres
```

**IMPORTANT :** Remplacez `[YOUR-PASSWORD]` par votre VRAI mot de passe de base de données.

⚠️ **C'est PAS le mot de passe de votre compte Supabase !**

C'est le mot de passe que vous avez créé lors de la création du projet.

### Étape 4 : Si vous avez oublié le mot de passe

1. Dans **Settings > Database**
2. Cliquez sur **"Reset Database Password"**
3. Créez un nouveau mot de passe (ex: `MonMotDePasse2026!`)
4. **NOTEZ-LE QUELQUE PART** ⚠️
5. Utilisez ce nouveau mot de passe dans l'URL

---

## 📝 MISE À JOUR DU FICHIER .env

Une fois que vous avez l'URL correcte, modifiez le fichier `.env` :

```bash
# SUPABASE - CONFIGURATION CORRECTE
DATABASE_URL=postgresql://postgres.xxxxxxxxx:VOTRE_VRAI_MOT_DE_PASSE@aws-X-xxx.pooler.supabase.com:6543/postgres

# GEMINI API (IA)
GEMINI_API_KEY=AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA

# FLASK
SECRET_KEY=ma-cle-secrete-super-securisee
FLASK_APP=run.py
FLASK_ENV=development
```

---

## ✅ VÉRIFICATION

Pour tester que ça fonctionne :

```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
source venv/bin/activate
python -c "from app import create_app; create_app()"
```

**Vous devriez voir :**
```
✅ [SUPABASE] Connexion configurée depuis DATABASE_URL
🔗 [SUPABASE] Connexion configurée (Port 6543 - Transaction Pooler)
```

**PAS d'erreur `Tenant or user not found`** ✅

---

## 🔄 MIGRATION DE LA BASE DE DONNÉES

Une fois la connexion Supabase fonctionnelle :

```bash
# Supprimer les anciennes migrations SQLite
rm -rf migrations

# Initialiser avec Supabase
flask db init

# Créer la migration Architecture V2
flask db migrate -m "Architecture V2: Départements + Catégories UE"

# Appliquer sur Supabase
flask db upgrade
```

---

## ❓ EN CAS DE PROBLÈME

### Erreur : "Tenant or user not found"
→ Mot de passe ou URL incorrecte. Refaites les étapes 1-4.

### Erreur : "Connection refused"
→ Vérifiez que le port est bien **6543** (Transaction Pooler)

### Erreur : "SSL required"
→ Ajoutez `?sslmode=require` à la fin de l'URL :
```
postgresql://...postgres?sslmode=require
```

---

## 📞 EXEMPLE COMPLET D'URL CORRECTE

```
DATABASE_URL=postgresql://postgres.pzzfqduntcmklrakhggy:VotreMdp2026!@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

Remplacez :
- `VotreMdp2026!` par votre vrai mot de passe
- `aws-0-eu-central-1` par votre vraie région (visible sur Supabase)

---

**Date :** 18 Février 2026  
**Status :** Configuration Supabase obligatoire (SQLite désactivé)

