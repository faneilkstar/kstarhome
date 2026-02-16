# 🚀 GUIDE RAPIDE - Configuration Supabase

## ⚡ Configuration en 3 étapes

### 1️⃣ Configurer le mot de passe Supabase

Ouvrez le fichier `.env` et remplacez `[TON_MOT_DE_PASSE]` par votre vrai mot de passe Supabase:

```bash
nano .env
```

Modifiez cette ligne:
```
SUPABASE_DB_URL=postgresql://postgres.pzzfqduntcmklrakhggy:[TON_MOT_DE_PASSE]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

Exemple (avec un vrai mot de passe):
```
SUPABASE_DB_URL=postgresql://postgres.pzzfqduntcmklrakhggy:MonMotDePasse123!@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

Sauvegardez: `Ctrl+O` puis `Entrée`, puis quittez: `Ctrl+X`

---

### 2️⃣ Créer les tables dans Supabase

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Nettoyer les anciennes migrations
rm -rf migrations/

# Initialiser les migrations
flask db init

# Créer la migration
flask db migrate -m "Migration Supabase"

# Appliquer sur Supabase
flask db upgrade
```

---

### 3️⃣ Créer le compte administrateur

```bash
python create_admin.py
```

Appuyez sur `Entrée` pour utiliser les valeurs par défaut:
- Username: `admin`
- Password: `admin123`
- Email: `admin@kstarhome.com`

---

## 🌐 Lancer l'application

```bash
python run.py
```

Ouvrez votre navigateur: **http://localhost:5000**

Connectez-vous avec:
- **Username**: `admin`
- **Password**: `admin123`

---

## 🔄 Déploiement automatique sur Render

Une fois que tout fonctionne localement:

```bash
git add .
git commit -m "Configuration Supabase complète"
git push origin main
```

Render redéploiera automatiquement votre site en 3-5 minutes! 🎉

---

## ❓ Problèmes courants

### Port 5000 déjà utilisé
```bash
lsof -ti:5000 | xargs kill -9
```

### Erreur de connexion Supabase
Vérifiez que:
1. Le mot de passe dans `.env` est correct (sans crochets)
2. Le port est bien `:6543` (mode pooler)
3. Vous avez bien fait `flask db upgrade`

### Aucune table créée
```bash
# Vérifier la connexion
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print(db.engine.url)"
```

---

## 📝 Notes importantes

- ✅ Tous les étudiants commencent en **1ère année**
- ✅ On utilise des **UE** (Unités d'Enseignement), pas des matières
- ✅ C'est un site **universitaire** (Licence/Master)
- ✅ Les données sont sur **Supabase** (cloud)
- ✅ Le déploiement est **automatique** via GitHub → Render

---

Créé par: **Ing. KOISSI-ZO Tonyi Constantin**
Date: 12 Février 2026

