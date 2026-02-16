#!/bin/bash

# 🚀 Script de Déploiement Automatique Rapide

echo "════════════════════════════════════════════════════════"
echo "🚀 DÉPLOIEMENT AUTOMATIQUE KSTAR-HOME"
echo "════════════════════════════════════════════════════════"
echo ""

# Vérifier si on est dans un dépôt git
if [ ! -d ".git" ]; then
    echo "❌ Erreur: Pas dans un dépôt Git"
    echo "   Initialisez d'abord: git init"
    exit 1
fi

# Vérifier les modifications
if [ -z "$(git status --porcelain)" ]; then
    echo "ℹ️  Aucune modification détectée"
    read -p "Voulez-vous forcer le déploiement? (y/N): " FORCE
    if [ "$FORCE" != "y" ] && [ "$FORCE" != "Y" ]; then
        echo "Annulé."
        exit 0
    fi
fi

# Afficher les modifications
echo "📝 Modifications détectées:"
echo "─────────────────────────────────────────────────────"
git status --short
echo "─────────────────────────────────────────────────────"
echo ""

# Demander le message de commit
read -p "💬 Message du commit (ou Enter pour auto): " MESSAGE

if [ -z "$MESSAGE" ]; then
    MESSAGE="🚀 Auto-deploy $(date '+%Y-%m-%d %H:%M:%S')"
fi

echo ""
echo "📦 Préparation du déploiement..."

# Ajouter tous les fichiers
git add .

# Commit
git commit -m "$MESSAGE"

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du commit"
    exit 1
fi

echo "✅ Commit créé"
echo ""

# Pousser sur GitHub
echo "📤 Push vers GitHub..."
git push origin main

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du push"
    echo "   Essayez: git push -u origin main"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ CODE POUSSÉ SUR GITHUB !"
echo "════════════════════════════════════════════════════════"
echo ""
echo "🔄 Déploiement en cours..."
echo ""
echo "📊 Suivez le déploiement sur:"
echo "   • GitHub Actions: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
echo "   • Render Dashboard: https://dashboard.render.com"
echo ""
echo "⏳ Le déploiement prend environ 3-5 minutes"
echo ""
echo "Statut estimé:"
echo "   [0-1 min] GitHub Actions démarre"
echo "   [1-2 min] Tests et vérifications"
echo "   [2-5 min] Render build et deploy"
echo ""
echo "🎉 Votre site sera mis à jour automatiquement !"
echo ""

# Optionnel: Trigger Render manuellement si RENDER_DEPLOY_HOOK est défini
if [ -f ".env" ]; then
    source .env
    if [ -n "$RENDER_DEPLOY_HOOK" ]; then
        echo "🔧 Déclenchement manuel de Render..."
        curl -X POST "$RENDER_DEPLOY_HOOK" -s > /dev/null
        echo "✅ Render déployment déclenché manuellement"
        echo ""
    fi
fi

echo "════════════════════════════════════════════════════════"
echo "📝 NOTES:"
echo "  • Ne fermez pas votre terminal pendant le déploiement"
echo "  • Vérifiez les logs sur Render si problème"
echo "  • Rafraîchissez le site (Ctrl+F5) après déploiement"
echo "════════════════════════════════════════════════════════"

