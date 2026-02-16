# 🤖 GUIDE GEMINI AI - DÉPLOIEMENT VERCEL

## ✅ CE QUI A ÉTÉ FAIT

### Fichiers créés :
1. ✅ **`app/ai_manager.py`** - Gestionnaire IA Gemini
2. ✅ **`app/routes/api_ia.py`** - Routes API pour l'IA
3. ✅ **`app/templates/test_ia.html`** - Page de test
4. ✅ **Blueprint enregistré** dans `app/__init__.py`
5. ✅ **requirements.txt** mis à jour avec `google-generativeai`

### Fonctionnalités :
- ✅ Chat avec l'IA (POST /api/ia/chat)
- ✅ Validation de réponses (POST /api/ia/valider)
- ✅ Génération d'exercices (POST /api/ia/generer-exercice)
- ✅ Vérification du statut (GET /api/ia/status)
- ✅ Page de test (GET /api/ia/test)

---

## 🔑 TA CLÉ API GEMINI

```
AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA
```

**Projet** : projects/535983796765  
**Nom** : Gemini API Key

---

## 🚀 DÉPLOIEMENT SUR VERCEL

### ÉTAPE 1 : Pousser le code sur GitHub

```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3

# Ajouter tous les fichiers
git add .

# Commit avec message clair
git commit -m "Ajout IA Gemini : chat, validation, génération d'exercices"

# Pousser sur GitHub
git push origin main
```

### ÉTAPE 2 : Configurer la clé API sur Vercel

1. Va sur **https://vercel.com/dashboard**
2. Clique sur ton projet **"kstarhome"**
3. Va dans **"Settings"** (en haut)
4. Dans le menu de gauche, clique sur **"Environment Variables"**
5. Clique sur **"Add New"**

#### Ajouter la variable :

**Name** :
```
GEMINI_API_KEY
```

**Value** :
```
AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA
```

**Environments** : Coche les 3 cases
- ✅ Production
- ✅ Preview
- ✅ Development

6. Clique sur **"Save"**

### ÉTAPE 3 : Redéployer

Vercel va automatiquement redéployer après ton push sur GitHub.

Sinon, force le redéploiement :
1. Va dans **"Deployments"**
2. Clique sur les 3 points `...` du dernier déploiement
3. Clique sur **"Redeploy"**

---

## 🧪 TESTER L'IA

### Sur Vercel (une fois déployé) :

1. Connecte-toi à ton site : `https://kstarhome.vercel.app`
2. Va sur : `https://kstarhome.vercel.app/api/ia/test`
3. Pose une question à l'IA
4. Vérifie que ça fonctionne !

### En local :

```bash
# Définir la clé API en local
export GEMINI_API_KEY="AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA"

# Lancer l'application
python run.py
```

Puis va sur : `http://127.0.0.1:5000/api/ia/test`

---

## 📡 API ENDPOINTS

### 1. Chat avec l'IA

**POST** `/api/ia/chat`

```json
{
  "question": "Explique-moi la photosynthèse",
  "role": "Tu es un professeur de biologie"
}
```

**Réponse** :
```json
{
  "reponse": "La photosynthèse est...",
  "succes": true
}
```

### 2. Valider une réponse

**POST** `/api/ia/valider`

```json
{
  "question": "Qu'est-ce que la photosynthèse ?",
  "reponse_etudiant": "C'est le processus par lequel...",
  "reponse_attendue": "La photosynthèse est..."
}
```

**Réponse** :
```json
{
  "valide": true,
  "note": 16.5,
  "commentaire": "Excellente réponse !",
  "suggestions": "Tu pourrais ajouter...",
  "succes": true
}
```

### 3. Générer un exercice

**POST** `/api/ia/generer-exercice` (Enseignants seulement)

```json
{
  "matiere": "Mathématiques",
  "niveau": "L1",
  "type": "QCM"
}
```

**Réponse** :
```json
{
  "enonce": "Résoudre l'équation...",
  "questions": ["Question 1", "Question 2"],
  "reponses": ["Réponse 1", "Réponse 2"],
  "correction": "Explication détaillée...",
  "succes": true
}
```

### 4. Vérifier le statut

**GET** `/api/ia/status`

**Réponse** :
```json
{
  "disponible": true,
  "modele": "gemini-pro",
  "message": "IA Gemini opérationnelle"
}
```

---

## 🔧 UTILISER L'IA DANS TON CODE

### Exemple 1 : Chat simple

```python
from app.ai_manager import interroger_ia

# Poser une question
reponse = interroger_ia(
    "Qu'est-ce que le théorème de Pythagore ?",
    contexte="Tu es un professeur de mathématiques"
)

print(reponse)
```

### Exemple 2 : Validation automatique

```python
from app.ai_manager import valider_reponse_etudiant

resultat = valider_reponse_etudiant(
    question="Qu'est-ce que la photosynthèse ?",
    reponse_etudiant="C'est le processus par lequel les plantes produisent leur nourriture",
    reponse_attendue="La photosynthèse est le processus de conversion de l'énergie lumineuse..."
)

print(f"Note : {resultat['note']}/20")
print(f"Commentaire : {resultat['commentaire']}")
```

### Exemple 3 : Générer un exercice

```python
from app.ai_manager import generer_exercice

exercice = generer_exercice(
    matiere="Physique",
    niveau="L2",
    type_exercice="Problème"
)

print(f"Énoncé : {exercice['enonce']}")
```

---

## 🎯 INTÉGRATION DANS LE LABORATOIRE

Tu peux maintenant intégrer Gemini dans ton laboratoire existant !

### Dans `app/routes/laboratoire.py` :

```python
from app.ai_manager import interroger_ia, valider_reponse_etudiant

@laboratoire_bp.route('/tp/<int:tp_id>/aide', methods=['POST'])
@login_required
def aide_ia(tp_id):
    """Aide IA pour un TP"""
    question = request.json.get('question')
    
    reponse = interroger_ia(
        question,
        contexte="Tu es un assistant de laboratoire qui aide les étudiants"
    )
    
    return jsonify({'aide': reponse})

@laboratoire_bp.route('/tp/<int:tp_id>/valider', methods=['POST'])
@login_required
def valider_tp(tp_id):
    """Validation automatique par l'IA"""
    data = request.json
    
    resultat = valider_reponse_etudiant(
        question=data['question'],
        reponse_etudiant=data['reponse'],
        reponse_attendue=data.get('correction')
    )
    
    return jsonify(resultat)
```

---

## 📊 LIMITES ET QUOTAS GEMINI

### Gratuit (Gemini Pro) :
- ✅ 60 requêtes par minute
- ✅ 1500 requêtes par jour
- ✅ Parfait pour ton usage universitaire !

### Si tu dépasses :
- Attendre 1 minute
- Ou passer à l'abonnement payant (peu probable pour ton cas)

---

## 🐛 DÉPANNAGE

### Erreur "IA non disponible"

**Cause** : `GEMINI_API_KEY` non définie

**Solution** :
1. Vérifie dans Vercel : Settings > Environment Variables
2. La clé doit être : `AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA`
3. Redéploie après avoir ajouté la variable

### Erreur "API key not valid"

**Cause** : Clé expirée ou incorrecte

**Solution** :
1. Génère une nouvelle clé sur https://makersuite.google.com/app/apikey
2. Remplace dans Vercel
3. Redéploie

### Erreur "Rate limit exceeded"

**Cause** : Trop de requêtes (60/min)

**Solution** :
- Attends 1 minute
- Implémente un cache pour les réponses fréquentes

---

## ✅ CHECKLIST FINALE

Avant de déployer :

- [x] `app/ai_manager.py` créé
- [x] `app/routes/api_ia.py` créé
- [x] Blueprint enregistré dans `__init__.py`
- [x] `requirements.txt` mis à jour
- [x] Page de test créée
- [ ] Code poussé sur GitHub ← **À FAIRE**
- [ ] `GEMINI_API_KEY` ajoutée sur Vercel ← **À FAIRE**
- [ ] Application redéployée ← **À FAIRE**
- [ ] Test sur `/api/ia/test` ← **À FAIRE**

---

## 🎉 RÉSULTAT ATTENDU

Après déploiement, tu auras :

```
✅ Chat IA fonctionnel
✅ Validation automatique de réponses
✅ Génération d'exercices
✅ API REST complète
✅ Interface de test élégante
✅ Intégration possible dans le laboratoire
```

---

## 🔗 LIENS UTILES

- **Console Gemini** : https://makersuite.google.com/app/apikey
- **Documentation Gemini** : https://ai.google.dev/docs
- **Vercel Dashboard** : https://vercel.com/dashboard
- **GitHub** : https://github.com/faneilkstar/kstarhome

---

**Version** : 11.2.0 - Gemini AI Intégré  
**Date** : 16 février 2026  
**Clé API** : AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA

🤖 **IA GEMINI COMPLÈTEMENT INTÉGRÉE !**  
🚀 **PRÊT POUR LE DÉPLOIEMENT !**  
✨ **TON APPLICATION A MAINTENANT UN CERVEAU !**

