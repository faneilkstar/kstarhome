# 🚀 DÉPLOIEMENT AUTOMATIQUE - GUIDE COMPLET

## ✅ ÉTAPE 1: Configuration GitHub Actions (FAIT ✓)

Le fichier `.github/workflows/auto-deploy.yml` a été créé.

## 🔑 ÉTAPE 2: Configurer le Deploy Hook Render

### 2.1 Obtenir le Deploy Hook
1. Allez sur https://dashboard.render.com
2. Sélectionnez votre service Web
3. Allez dans **Settings** → **Deploy Hook**
4. Cliquez sur **Create Deploy Hook**
5. Copiez l'URL générée (format: `https://api.render.com/deploy/srv-xxxxx?key=xxxxx`)

### 2.2 Ajouter le Secret sur GitHub
1. Allez sur votre dépôt GitHub
2. Cliquez sur **Settings** → **Secrets and variables** → **Actions**
3. Cliquez sur **New repository secret**
4. Nom: `RENDER_DEPLOY_HOOK`
5. Valeur: Collez l'URL du Deploy Hook
6. Cliquez sur **Add secret**

## 🎯 ÉTAPE 3: Utilisation

### Déploiement automatique
```bash
# Modifier votre code localement
nano app/routes/laboratoire.py

# Committer et pousser
git add .
git commit -m "✨ Amélioration du laboratoire IA V3"
git push origin main

# ⏳ Attendez 3-5 minutes
# GitHub Actions va:
# 1. Vérifier le code
# 2. Tester la compilation
# 3. Déclencher Render
# 4. Render va redéployer automatiquement
```

### Voir le statut du déploiement
- **GitHub**: Onglet "Actions" de votre dépôt
- **Render**: Onglet "Events" de votre service

## 🔄 WORKFLOW COMPLET

```
┌─────────────────┐
│  Modification   │
│   de code       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   git push      │
│   origin main   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
│  • Compile      │
│  • Teste        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Trigger Render  │
│  Deploy Hook    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Render Deploy   │
│  • Build        │
│  • Deploy       │
│  • Live 🎉      │
└─────────────────┘
```

## 🛠️ COMMANDES UTILES

### Déployer manuellement depuis GitHub
```bash
# Aller dans l'onglet Actions → Auto Deploy to Render
# Cliquer sur "Run workflow" → "Run workflow"
```

### Déployer depuis votre terminal local
```bash
# Ajouter votre Deploy Hook dans .env (NE PAS COMMITER)
echo "RENDER_DEPLOY_HOOK=https://api.render.com/deploy/srv-xxxxx?key=xxxxx" >> .env

# Puis utiliser curl
source .env
curl -X POST "$RENDER_DEPLOY_HOOK"
```

### Script de déploiement rapide
```bash
#!/bin/bash
# deploy_auto.sh

echo "🚀 Déploiement automatique..."

# Vérifier les modifications
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Modifications détectées"
    
    # Demander message de commit
    read -p "Message du commit: " MESSAGE
    
    # Commit et push
    git add .
    git commit -m "$MESSAGE"
    git push origin main
    
    echo "✅ Code poussé sur GitHub"
    echo "⏳ GitHub Actions va déclencher le déploiement dans quelques secondes..."
    echo "📊 Suivez le déploiement sur:"
    echo "   - GitHub: https://github.com/VOTRE-USERNAME/VOTRE-REPO/actions"
    echo "   - Render: https://dashboard.render.com"
else
    echo "ℹ️  Aucune modification à déployer"
fi
```

## 🎨 AMÉLIORATIONS IA V3

### Nouvelles fonctionnalités ajoutées

1. **Gemini Pro Integration**
   - Réponses naturelles et pédagogiques
   - Compréhension contextuelle avancée
   - Fallback intelligent si Gemini est indisponible

2. **Analyse Multi-Dimensionnelle**
   - Qualité des mesures (40%)
   - Progression de l'étudiant (20%)
   - Engagement (15%)
   - Compréhension (15%)
   - Autonomie (10%)

3. **Feedback Personnalisé**
   - Points forts identifiés
   - Axes d'amélioration ciblés
   - Recommandations pédagogiques

4. **Base de Connaissances Étendue**
   - Convertisseur Buck
   - Traitement du signal (Fourier)
   - Thermodynamique
   - Mécanique (chute libre)
   - Et plus...

## 📊 VARIABLES D'ENVIRONNEMENT

### Sur Render (Settings → Environment)
```bash
# Base de données
DATABASE_URL=postgresql://...

# Flask
SECRET_KEY=votre-clé-secrète
FLASK_ENV=production

# IA Gemini (optionnel)
GEMINI_API_KEY=votre-clé-gemini

# Email (optionnel)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-app
```

## 🐛 DÉPANNAGE

### Le déploiement échoue sur Render
1. Vérifiez les logs sur Render (onglet "Logs")
2. Erreur fréquente: dépendances manquantes
   ```bash
   # Localement, testez:
   pip install -r requirements.txt
   python run.py
   ```

### GitHub Actions échoue
1. Vérifiez l'onglet "Actions" sur GitHub
2. Regardez les logs de l'étape qui échoue
3. Souvent: erreur de syntaxe Python

### Le site ne se met pas à jour
1. Vérifiez que le push a réussi sur GitHub
2. Attendez 5 minutes (Render peut être lent)
3. Videz le cache de votre navigateur (Ctrl+F5)
4. Sur Render, cliquez sur "Manual Deploy" → "Clear build cache & deploy"

## 📚 RESSOURCES

- [Documentation Render](https://render.com/docs)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gemini API](https://ai.google.dev/docs)

## 🎯 PROCHAINES ÉTAPES

1. ✅ Push ce code sur GitHub
2. ✅ Configurer le Deploy Hook sur GitHub Secrets
3. ✅ Tester le déploiement automatique
4. 🎉 Profiter du déploiement sans effort !

---

**Dernière mise à jour**: 2026-02-12
**Version IA**: V3 (Gemini Pro + Fallback Intelligent)

