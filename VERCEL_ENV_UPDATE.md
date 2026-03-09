# ✅ MISE À JOUR VERCEL - NOUVEAU MOT DE PASSE SUPABASE

## 🔒 Nouveau mot de passe configuré : `masquedemort`

## 📝 Actions à effectuer sur Vercel :

1. **Aller sur Vercel.com**
   - Connectez-vous à votre compte
   - Sélectionnez le projet `kstarhome`

2. **Mettre à jour les variables d'environnement**
   - Allez dans **Settings** → **Environment Variables**
   - Trouvez `DATABASE_URL`
   - Cliquez sur **Edit**
   - Remplacez par :
   ```
   postgresql://postgres.pzzfqduntcmklrakhggy:masquedemort@aws-1-eu-west-1.pooler.supabase.com:6543/postgres?sslmode=require
   ```

3. **Redéployer**
   - Allez dans **Deployments**
   - Cliquez sur les 3 points ⋮ du dernier déploiement
   - Sélectionnez **Redeploy**

## ✅ Connexion locale testée avec succès

Le serveur démarre correctement en local avec le nouveau mot de passe.

## 🔑 Variables d'environnement actuelles :

```env
DATABASE_URL=postgresql://postgres.pzzfqduntcmklrakhggy:masquedemort@aws-1-eu-west-1.pooler.supabase.com:6543/postgres?sslmode=require
GEMINI_API_KEY=AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=ma-cle-secrete-super-securisee-2024
```

## 🚀 Après le redéploiement

Votre site sera accessible sur :
- https://kstarhome.vercel.app

Avec connexion complète à Supabase (PostgreSQL).

