# 🔴 PROBLÈME IDENTIFIÉ : Identifiants Supabase Incorrects

## ❌ Erreur Actuelle
```
FATAL: Tenant or user not found
```

Cela signifie que :
- Le mot de passe est incorrect, OU
- L'ID du projet est incorrect, OU
- La base de données n'existe pas

---

## ✅ SOLUTION : Récupérer les Bons Identifiants

### Étape 1 : Aller sur Supabase
Ouvrez votre navigateur et allez sur :
**https://supabase.com/dashboard/project/pzzfqduntcmklrakhggy/settings/database**

### Étape 2 : Trouver la Connection String
1. Dans la section **"Connection string"**
2. Sélectionnez le mode **"Transaction"** (pas Session)
3. Vous verrez quelque chose comme :
```
postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

### Étape 3 : Copier l'URL Complète
1. Cliquez sur **"Copy"** pour copier l'URL
2. L'URL ressemble à :
```
postgresql://postgres.XXXXXX:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

### Étape 4 : Remplacer [YOUR-PASSWORD]
Dans l'URL copiée, **remplacez `[YOUR-PASSWORD]`** par votre vrai mot de passe Supabase.

**Si votre mot de passe contient des espaces ou caractères spéciaux**, encodez-les :
- Espace → `%20`
- @ → `%40`
- # → `%23`
- etc.

Exemple avec "masque de mort" :
```
postgresql://postgres.xxxxx:masque%20de%20mort@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

### Étape 5 : Mettre à Jour le .env
Ouvrez le fichier `.env` et remplacez la ligne `SUPABASE_DB_URL` :

```bash
nano .env
```

Collez l'URL complète avec le vrai mot de passe :
```
SUPABASE_DB_URL=postgresql://postgres.VOTRE_ID:VOTRE_MOT_DE_PASSE@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

Sauvegardez : `Ctrl+O` puis `Entrée`, puis quittez : `Ctrl+X`

### Étape 6 : Tester
```bash
python test_supabase.py
```

Si ça affiche `✅ CONNEXION RÉUSSIE!`, alors vous pouvez continuer avec :
```bash
flask db upgrade
python create_admin.py
python run.py
```

---

## 🔍 Vérifications Importantes

### Le mot de passe est-il correct ?
- Allez dans Supabase → Settings → Database
- Cliquez sur "Reset database password" si vous ne vous en souvenez plus
- Notez le nouveau mot de passe

### L'ID du projet est-il correct ?
Dans votre URL actuelle : `postgres.pzzfqduntcmklrakhggy`
- Vérifiez que c'est bien le même ID dans votre dashboard Supabase
- L'URL de votre dashboard devrait contenir ce même ID

---

## 🆘 Si Rien Ne Fonctionne

### Option 1 : Réinitialiser le mot de passe
1. Dashboard Supabase → Settings → Database
2. Cliquez "Reset database password"
3. Choisissez un nouveau mot de passe SIMPLE (sans espaces)
4. Exemple : `MonMotDePasse2026!`
5. Mettez à jour `.env` avec ce nouveau mot de passe

### Option 2 : Utiliser le mode Session (port 5432)
Si le mode Transaction ne fonctionne pas, essayez le mode Session :
```
SUPABASE_DB_URL=postgresql://postgres.pzzfqduntcmklrakhggy:VOTRE_MOT_DE_PASSE@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
```

### Option 3 : Vérifier le projet
- Assurez-vous que le projet existe toujours
- Vérifiez que vous êtes connecté au bon compte Supabase
- Le projet n'est pas en pause ou supprimé

---

## 📞 Ce Qu'il Faut Me Donner

Pour que je puisse vous aider, donnez-moi :

1. **L'URL de connexion** (copiée depuis Supabase, avec [YOUR-PASSWORD] non remplacé)
   - Exemple : `postgresql://postgres.xxxxx:[YOUR-PASSWORD]@...`

2. **Confirmation du mot de passe** (je l'encoderai correctement)

3. **Screenshot** de la page Settings → Database de Supabase (optionnel)

Dès que vous me donnez ces infos, je configure tout automatiquement ! 🚀

