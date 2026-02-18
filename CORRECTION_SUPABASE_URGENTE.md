# 🔧 CORRECTION URGENTE : ERREUR SUPABASE

## ❌ ERREUR ACTUELLE

```
FATAL: Tenant or user not found
Connection to server at "aws-0-eu-central-1.pooler.supabase.com" failed
```

## 🎯 CAUSE

Le mot de passe dans votre `DATABASE_URL` est **INCORRECT**.

Mot de passe actuel dans .env : `masque%20de%20mort`

Ce mot de passe ne fonctionne pas avec Supabase.

---

## ✅ SOLUTION RAPIDE (2 MINUTES)

### Option 1 : Réinitialiser le Mot de Passe Supabase

**C'est la solution la plus simple et la plus sûre.**

#### Étapes :

1. **Allez sur Supabase**
   - https://supabase.com
   - Connectez-vous
   - Sélectionnez votre projet

2. **Réinitialisez le mot de passe**
   - Cliquez sur **⚙️ Settings** (sidebar gauche)
   - Cliquez sur **🗄️ Database**
   - Descendez et cliquez sur **"Reset Database Password"**
   
3. **Créez un NOUVEAU mot de passe SIMPLE**
   - ⚠️ **IMPORTANT** : Pas d'espaces !
   - Exemples valides :
     - `Admin2024!`
     - `Supabase123`
     - `MyPassword2026`
   - **NOTEZ-LE quelque part** (sur un papier)

4. **Obtenez la nouvelle URL**
   - Toujours dans **Settings → Database**
   - Descendez jusqu'à **"Connection string"**
   - ✅ **COCHEZ** : "Use connection pooling"
   - Sélectionnez : **"Transaction"** (Port 6543)
   - **Copiez** l'URL affichée
   - Elle ressemble à :
     ```
     postgresql://postgres.pzzfqduntcmklrakhggy:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
     ```
   - Remplacez `[YOUR-PASSWORD]` par le mot de passe que vous venez de créer

5. **Mettez à jour le fichier .env**
   ```bash
   cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
   nano .env
   ```
   
   Modifiez la ligne `DATABASE_URL` :
   ```
   DATABASE_URL=postgresql://postgres.pzzfqduntcmklrakhggy:VotreNouveauMotDePasse@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```
   
   **Exemple concret** (si votre mot de passe est `Admin2024!`) :
   ```
   DATABASE_URL=postgresql://postgres.pzzfqduntcmklrakhggy:Admin2024!@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```
   
   Sauvegardez : **CTRL+O** puis **ENTER**
   Quittez : **CTRL+X**

6. **Testez la connexion**
   ```bash
   source venv/bin/activate
   python run.py
   ```

---

### Option 2 : Utiliser SQLite Local (temporaire)

Si vous voulez **tester rapidement** sans Supabase :

```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
nano .env
```

Commentez `DATABASE_URL` :
```
# DATABASE_URL=postgresql://...
GEMINI_API_KEY=AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=ma-cle-secrete-super-securisee-2024
```

Modifiez `config.py` :
```bash
nano config.py
```

Cherchez la section `DevelopmentConfig` et vérifiez que le fallback SQLite est activé.

---

## 📋 CHECKLIST VÉRIFICATION

Après modification du .env :

```bash
# 1. Vérifier que le fichier est bien modifié
cat .env | grep DATABASE_URL

# 2. Tester la connexion
source venv/bin/activate
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('DATABASE_URL:', os.getenv('DATABASE_URL')[:50] + '...')
"

# 3. Lancer l'application
python run.py
```

**Résultat attendu** :
```
✅ [SUPABASE] Connexion configurée depuis DATABASE_URL
🔗 [SUPABASE] Connexion configurée (Port 6543 - Transaction Pooler)
 * Running on http://127.0.0.1:5000
```

**PAS d'erreur** : `Tenant or user not found` ✅

---

## ⚠️ ERREURS COURANTES

### Erreur : "Tenant or user not found"
**Cause** : Mot de passe incorrect
**Solution** : Réinitialisez le mot de passe (Option 1)

### Erreur : "Connection refused"
**Cause** : Port ou URL incorrecte
**Solution** : Vérifiez que c'est bien le port **6543**

### Erreur : "SSL required"
**Cause** : SSL manquant
**Solution** : Ajoutez `?sslmode=require` à la fin de l'URL

---

## 🎯 COMMANDE RAPIDE

Copiez-collez cette commande pour modifier le .env rapidement :

```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3 && nano .env
```

Puis modifiez la ligne `DATABASE_URL` avec votre **VRAI** mot de passe.

---

## 📞 SI VOUS ÊTES BLOQUÉ

1. Vérifiez que vous êtes sur le bon projet Supabase
2. Vérifiez que le projet est actif (pas en pause)
3. Réinitialisez le mot de passe avec un mot simple : `Admin2024!`
4. Copiez l'URL exacte depuis Supabase
5. Collez-la dans le .env

---

**Date** : 18 Février 2026  
**Erreur** : Tenant or user not found  
**Solution** : Réinitialiser le mot de passe Supabase

