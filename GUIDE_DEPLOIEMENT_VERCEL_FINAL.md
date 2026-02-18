# 🚀 GUIDE DE DÉPLOIEMENT VERCEL - KSTARHOME

## ✅ CORRECTIONS EFFECTUÉES

### 1. Migration vers la nouvelle API Gemini
- ✅ Remplacement de `google.generativeai` par `google.genai` 
- ✅ Mise à jour de `requirements.txt`
- ✅ Correction de `ai_manager.py`
- ✅ Correction de `validation_ia.py`

### 2. Corrections des erreurs
- ✅ Remplacement de "Matiere" par "UE" dans evaluation.py et evaluation_service.py
- ✅ Correction syntaxe carte_etudiant_service.py
- ✅ Correction template affecter_ues_enseignants.html
- ✅ Suppression classe SignatureDocument dupliquée

### 3. Configuration Vercel
- ✅ Fichier `vercel.json` prêt
- ✅ Fichier `api/index.py` prêt
- ✅ `requirements.txt` optimisé pour Vercel

---

## 📋 ÉTAPES DE DÉPLOIEMENT

### ÉTAPE 1 : Push sur GitHub

```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
git add -A
git commit -m "🚀 Déploiement Vercel - Toutes corrections appliquées"
git push origin main
```

**Identifiants GitHub :**
- Username: `faneilkstar`
- Password: [Votre Personal Access Token GitHub]

> Si vous n'avez pas de token, créez-en un sur : https://github.com/settings/tokens

---

### ÉTAPE 2 : Configurer Vercel

1. **Allez sur** : https://vercel.com
2. **Connectez-vous** avec GitHub
3. **Cliquez sur** : "Add New..." → "Project"
4. **Importez** : `kstarhome` (votre repository)

---

### ÉTAPE 3 : Variables d'environnement Vercel

Dans **Settings** → **Environment Variables**, ajoutez :

#### 🔴 OBLIGATOIRE (Base de données)

| Name | Value |
|------|-------|
| `DATABASE_URL` | `postgresql://postgres.pzzfqduntcmklrakhggy:masque%20de%20mort@aws-0-eu-central-1.pooler.supabase.com:6543/postgres` |

#### 🟡 OPTIONNEL (IA Gemini)

| Name | Value |
|------|-------|
| `GEMINI_API_KEY` | Votre clé API Gemini |
| `FLASK_ENV` | `production` |

> **Note** : Sans `GEMINI_API_KEY`, le site fonctionnera mais l'IA sera désactivée

---

### ÉTAPE 4 : Déploiement

1. Cliquez sur **Deploy**
2. Attendez 3-5 minutes
3. Votre site sera accessible sur : `https://kstarhome.vercel.app`

---

## 🔧 EN CAS D'ERREUR 500

### Vérifier les logs

1. Dans Vercel, allez dans **Deployments**
2. Cliquez sur le déploiement actif
3. Allez dans **Runtime Logs**

### Erreurs fréquentes

| Erreur | Solution |
|--------|----------|
| `ModuleNotFoundError` | Vérifiez `requirements.txt` |
| `DATABASE_URL not found` | Ajoutez la variable d'environnement |
| `Table already exists` | Normal, ignorez (tables déjà sur Supabase) |

---

## 📊 STATUT ACTUEL

✅ Code prêt au déploiement  
✅ API Gemini migrée  
✅ Templates corrigés  
✅ Base de données Supabase configurée  
⏳ En attente : Push GitHub + Configuration Vercel  

---

## 🎯 ACTIONS À FAIRE MAINTENANT

### 1. Push sur GitHub

```bash
# Dans votre terminal
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3

# Si vous n'avez pas de token GitHub, créez-en un d'abord
# Puis:
git push origin main
```

### 2. Sur Vercel

1. Importez le projet
2. Ajoutez `DATABASE_URL` dans les variables d'environnement
3. Déployez

### 3. Test

Visitez votre site sur l'URL fournie par Vercel

---

## 📞 AIDE SUPPLÉMENTAIRE

Si erreur 500 :
1. Consultez les Runtime Logs dans Vercel
2. Vérifiez que DATABASE_URL est bien configuré
3. Redéployez si besoin

---

**Dernière mise à jour** : 18 février 2026  
**Status** : ✅ Prêt pour production

