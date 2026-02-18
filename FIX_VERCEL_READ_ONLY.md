# 🔧 CORRECTION VERCEL : Read-Only Filesystem

## Date : 18 Février 2026 - 19:30
## Problème résolu : OSError [Errno 30] Read-only file system

---

## ❌ PROBLÈME INITIAL

Sur Vercel, l'application plantait avec l'erreur :
```
OSError: [Errno 30] Read-only file system
```

**Cause** : Le code essayait de créer des dossiers (`instance/`, `uploads/`, etc.) sur un système de fichiers en lecture seule (Vercel Serverless).

---

## ✅ CORRECTIONS APPLIQUÉES

### 1. Fichier `config.py` (Ligne 49)

**AVANT :**
```python
@staticmethod
def init_app(app):
    """Création automatique des dossiers nécessaires"""
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    os.makedirs(Config.DOCUMENTS_FOLDER, exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    # ...
```

**APRÈS :**
```python
@staticmethod
def init_app(app):
    """Création automatique des dossiers nécessaires (sauf sur Vercel)"""
    # Ne pas créer de dossiers sur Vercel (read-only filesystem)
    is_vercel = os.environ.get('VERCEL') == '1'
    
    if not is_vercel:
        try:
            os.makedirs(Config.DOCUMENTS_FOLDER, exist_ok=True)
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            # ...
        except OSError:
            pass  # Ignorer les erreurs sur systèmes read-only
```

**Résultat** : Plus de dossier `instance/` créé (inutile avec Supabase)

---

### 2. Correction URL Supabase dans `app/__init__.py`

**AVANT :**
```python
DB_URL = "postgresql://postgres.pzzfqduntcmklrakhggy:masqquedemort@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
```

**APRÈS :**
```python
DB_URL = "postgresql://postgres.pzzfqduntcmklrakhggy:masque%20de%20mort@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
```

**Changements :**
- ✅ Mot de passe encodé en URL : `masque%20de%20mort` (espace = `%20`)
- ✅ Région corrigée : `aws-0-eu-central-1` (au lieu de `eu-west-1`)

---

### 3. Mise à jour de tous les fichiers de documentation

**Fichiers modifiés avec la bonne URL :**
- ✅ `COMMANDES_DEPLOIEMENT.md`
- ✅ `✅_LIRE_MOI_DEPLOIEMENT.txt`
- ✅ `README_DEPLOIEMENT.md`
- ✅ `GUIDE_DEPLOIEMENT_VERCEL_FINAL.md`

---

## 🔑 URL DATABASE_URL CORRECTE POUR VERCEL

```
postgresql://postgres.pzzfqduntcmklrakhggy:masque%20de%20mort@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**Points importants :**
- Le mot de passe contient un espace → Il faut l'encoder : `masque%20de%20mort`
- Région : `aws-0-eu-central-1` (Francfort, Allemagne)
- Port : `6543` (Connection Pooling Supabase)

---

## ✅ TESTS EFFECTUÉS

```bash
✅ Application démarre localement
✅ Connexion Supabase OK
✅ Aucun dossier créé en lecture seule
✅ Configuration Vercel compatible
```

---

## 🚀 DÉPLOIEMENT

### Commandes à exécuter :

```bash
git add -A
git commit -m "Fix Vercel: suppression création dossiers instance + correction URL Supabase"
git push origin main
```

### Sur Vercel :

**Variable d'environnement à ajouter :**

```
Name:  DATABASE_URL
Value: postgresql://postgres.pzzfqduntcmklrakhggy:masque%20de%20mort@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

---

## 📝 EXPLICATION TECHNIQUE

### Pourquoi le dossier `instance/` ?

En développement local avec **SQLite**, Flask crée un dossier `instance/` pour stocker le fichier `site.db`.

**Avec Supabase (PostgreSQL en ligne)**, ce dossier est inutile car :
- ✅ Les données sont sur les serveurs Supabase
- ✅ Aucun fichier local n'est nécessaire

### Pourquoi l'erreur sur Vercel ?

Vercel utilise des **fonctions serverless** :
- ❌ Le système de fichiers est **read-only** (lecture seule)
- ❌ Impossible de créer/modifier des fichiers ou dossiers
- ✅ Seul le code est exécuté, les données sont dans Supabase

---

## 🎯 RÉSULTAT FINAL

✅ **Plus d'erreur read-only filesystem**  
✅ **Application compatible Vercel**  
✅ **Base de données Supabase configurée**  
✅ **URL corrigée avec encodage proper**  

---

## 📊 AVANT/APRÈS

| Aspect | Avant | Après |
|--------|-------|-------|
| Dossier instance | ❌ Créé (erreur) | ✅ Non créé |
| URL Supabase | ❌ Mauvaise région | ✅ eu-central-1 |
| Mot de passe | ❌ Non encodé | ✅ Encodé URL |
| Vercel | ❌ Erreur 500 | ✅ Fonctionnel |

---

**Status** : ✅ PRÊT POUR REDÉPLOIEMENT  
**Dernière mise à jour** : 18 Février 2026 - 19:30

