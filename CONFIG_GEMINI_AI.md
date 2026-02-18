# 🤖 CONFIGURATION GEMINI AI - VERCEL

## Date : 18 Février 2026 - 20:00

---

## ✅ CLÉ API GEMINI DISPONIBLE

Vous avez une clé API Gemini fonctionnelle :
```
AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA
```

---

## 🚀 CONFIGURATION VERCEL

### Variables d'environnement à ajouter sur Vercel

Allez sur : **Settings → Environment Variables**

#### 1. Base de données (OBLIGATOIRE)

```
Name:  DATABASE_URL
Value: postgresql://postgres.pzzfqduntcmklrakhggy:masque%20de%20mort@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

#### 2. IA Gemini (RECOMMANDÉ)

```
Name:  GEMINI_API_KEY
Value: AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA
```

#### 3. Flask (OPTIONNEL)

```
Name:  FLASK_ENV
Value: production
```

```
Name:  SECRET_KEY
Value: ma-cle-secrete-super-securisee-2024
```

---

## 🎯 FONCTIONNALITÉS ACTIVÉES AVEC GEMINI

Avec la clé API configurée, votre site aura :

✅ **Validation automatique des inscriptions**
- L'IA évalue les dossiers d'étudiants
- Recommandations intelligentes
- Scoring automatique

✅ **Chatbot pédagogique**
- Assistance aux étudiants 24/7
- Réponses contextuelles
- Support multilingue

✅ **Correction automatique**
- Évaluation des réponses d'étudiants
- Feedback constructif
- Notation intelligente

✅ **Génération d'exercices**
- Création automatique de QCM
- Problèmes adaptés au niveau
- Corrections détaillées

✅ **Analyse de laboratoire**
- Validation des résultats de TP
- Suggestions d'amélioration
- Détection d'erreurs

---

## 🔒 SÉCURITÉ

⚠️ **IMPORTANT** :
- Ne partagez JAMAIS votre clé API publiquement
- Ne la commitez pas sur GitHub
- Elle est déjà dans `.env` (qui est dans `.gitignore`)

---

## 📋 DÉPLOIEMENT COMPLET

### Étape 1 : Push sur GitHub

```bash
git add -A
git commit -m "🤖 Ajout clé Gemini AI + corrections Vercel"
git push origin main
```

### Étape 2 : Configuration Vercel

1. Allez sur https://vercel.com
2. Cliquez sur votre projet `kstarhome`
3. **Settings** → **Environment Variables**
4. Ajoutez les 2 variables ci-dessus :
   - `DATABASE_URL`
   - `GEMINI_API_KEY`
5. Cliquez sur **Save**

### Étape 3 : Redéploiement

1. Allez dans **Deployments**
2. Cliquez sur **Redeploy** (ou attendez le déploiement automatique)
3. Attendez 3-5 minutes

### Étape 4 : Test

Visitez votre site et testez :
- Connexion avec `admin` / `admin123`
- Chat IA (si disponible dans l'interface)
- Validation d'inscription

---

## 🧪 TEST LOCAL

Pour tester l'IA localement :

```bash
# La clé est déjà dans .env
python run.py
```

Puis testez les fonctionnalités IA depuis l'interface.

---

## ⚡ QUOTA GRATUIT GEMINI

La clé API Gemini (gratuite) a des limites :

- **60 requêtes par minute**
- **1500 requêtes par jour**
- **1 million de tokens par mois**

Pour une utilisation universitaire normale, c'est largement suffisant !

---

## 📊 COMPARAISON AVEC/SANS IA

| Fonctionnalité | Sans Gemini | Avec Gemini |
|----------------|-------------|-------------|
| Validation inscriptions | ⚠️ Manuelle | ✅ Automatique |
| Support étudiants | ❌ Limité | ✅ 24/7 |
| Correction devoirs | ⚠️ Manuelle | ✅ Semi-auto |
| Génération exercices | ❌ Non | ✅ Oui |
| Analyse TP | ⚠️ Basique | ✅ Intelligente |

---

## 🎉 RÉCAPITULATIF

✅ Clé API ajoutée au fichier `.env`  
✅ Configuration locale fonctionnelle  
✅ Prêt pour Vercel  
✅ Documentation complète  

**Il ne reste qu'à configurer les variables sur Vercel !**

---

## 📞 EN CAS DE PROBLÈME

### L'IA ne répond pas ?

1. Vérifiez que `GEMINI_API_KEY` est bien dans Vercel
2. Attendez le redéploiement complet
3. Vérifiez les logs : **Deployments → Runtime Logs**

### Quota dépassé ?

Si vous voyez `429 Too Many Requests` :
- Attendez 1 minute (quota par minute)
- Ou 24h (quota journalier)

---

**Date** : 18 Février 2026 - 20:00  
**Status** : ✅ CLÉ GEMINI CONFIGURÉE  
**Prêt pour** : DÉPLOIEMENT VERCEL AVEC IA

