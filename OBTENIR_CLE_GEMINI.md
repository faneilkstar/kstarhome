# 🔑 GUIDE RAPIDE : Obtenir une Clé API Google Gemini

## ⏱️ Temps nécessaire : 2 minutes

---

## 📋 ÉTAPES SIMPLIFIÉES

### ✅ Étape 1 : Accéder à Google AI Studio (30 secondes)

1. Ouvrez votre navigateur
2. Allez sur : **https://makersuite.google.com/app/apikey**
3. Connectez-vous avec votre compte Google

### ✅ Étape 2 : Créer la clé API (30 secondes)

1. Vous arrivez sur la page "API keys"
2. Cliquez sur le bouton bleu **"Create API Key"**
3. Choisissez **"Create API key in new project"**
4. ⏳ Attendez 5 secondes
5. 🎉 Votre clé apparaît !

### ✅ Étape 3 : Copier la clé (10 secondes)

1. Cliquez sur l'icône **📋 Copier** à côté de la clé
2. La clé est copiée dans votre presse-papiers

Format de la clé : `AIzaSy...` (39 caractères)

### ✅ Étape 4 : Configurer dans KstarHome (30 secondes)

1. Ouvrez le fichier `.env` dans votre projet
2. Trouvez la ligne :
   ```
   GEMINI_API_KEY=
   ```
3. Collez votre clé :
   ```
   GEMINI_API_KEY=AIzaSyA...votre_cle_ici
   ```
4. Sauvegardez le fichier

### ✅ Étape 5 : Redémarrer l'application (30 secondes)

```bash
# Arrêter l'application
lsof -ti:5000 | xargs -r kill -9

# Relancer
source venv/bin/activate
python run.py
```

---

## 🎉 C'EST TERMINÉ !

Votre IA avancée est maintenant activée !

Pour vérifier :
1. Allez dans le laboratoire virtuel
2. Démarrez un TP
3. Posez une question à l'IA
4. Vous devriez recevoir une réponse **beaucoup plus intelligente** ! ⚡

---

## 🆘 DÉPANNAGE

### Problème : "Module 'google.generativeai' not found"

**Solution :**
```bash
pip install google-generativeai
```

### Problème : "Invalid API key"

**Solution :**
- Vérifiez que vous avez bien copié toute la clé (39 caractères)
- Pas d'espaces avant/après
- La clé commence par `AIza`

### Problème : L'IA répond toujours comme avant

**Solution :**
- Vérifiez que le fichier `.env` contient bien votre clé
- Redémarrez l'application (tuer le processus puis relancer)
- Regardez les logs au démarrage (devrait afficher "IA Avancée activée")

---

## 📊 VÉRIFIER QUE ÇA FONCTIONNE

Dans les logs au démarrage, vous devriez voir :

```
✅ Configuration chargée depuis .env
✅ IA Avancée (Gemini) disponible
🚀 Laboratoire virtuel avec IA conversationnelle activé
```

Ou si pas de clé :

```
ℹ️ IA Basique activée (pas de clé Gemini)
💡 Pour activer l'IA avancée, ajoutez GEMINI_API_KEY dans .env
```

---

## 💰 COÛT

**GRATUIT** ! 🎉

- Jusqu'à 60 requêtes par minute
- Illimité par jour
- Pas de carte bancaire demandée
- Pas d'abonnement

---

## ⚠️ IMPORTANT

### Pour la production (Render, Heroku, etc.)

1. **Ne PAS** pousser le fichier `.env` sur GitHub (déjà dans .gitignore)
2. Configurer `GEMINI_API_KEY` dans les **variables d'environnement** de votre plateforme
3. Sur Render : Settings → Environment → Add Environment Variable

---

## 🎓 CRÉÉ PAR

**Ing. KOISSI-ZO Tonyi Constantin**  
Spécialiste en Électronique de Puissance  
© 2026 KstarHome

**Date :** 11 Février 2026  
**Durée totale :** ~2 minutes ⏱️

