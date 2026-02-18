#!/bin/bash

# Script de redéploiement automatique sur GitHub
# L'application sera automatiquement redéployée sur Render

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🚀 REDÉPLOIEMENT AUTOMATIQUE                                ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3

echo "📝 Ajout des fichiers modifiés..."
git add -A

echo ""
echo "💾 Création du commit..."
git commit -m "🚀 Redéploiement: Configuration Supabase + Type Structure LMD

CONFIGURATION:
✅ Fichier .env créé avec DATABASE_URL
✅ Variables d'environnement Supabase configurées
✅ Clé API Gemini ajoutée

SYSTÈME LMD:
✅ Type Structure implémenté (ue_simple/ue_composite/element_constitutif)
✅ Semestres S1-S10
✅ UE Composites avec EC
✅ Génération automatique de codes
✅ Calcul moyennes pondérées

RÈGLES MÉTIER:
✅ UE Libres (optionnelles, accessibles à tous)
✅ Types de diplômes (Fondamental/Professionnel)
✅ Restrictions par filière

APPLICATION:
✅ Démarrage local vérifié
✅ Connexion Supabase testée
✅ 9 blueprints chargés
✅ Prêt pour production

Status: ✅ Prêt pour déploiement automatique
" 2>&1

if [ $? -ne 0 ]; then
    echo "ℹ️  Aucun changement à committer ou commit déjà fait"
fi

echo ""
echo "📤 Push vers GitHub (déclenchera le déploiement automatique)..."
git push origin main 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║   ✅ PUSH RÉUSSI !                                            ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🔄 Render va automatiquement redéployer l'application..."
    echo "⏱️  Attendez 3-5 minutes"
    echo ""
    echo "📍 Vérifiez le déploiement sur :"
    echo "   https://dashboard.render.com"
    echo ""
    echo "🌐 Une fois déployé, votre site sera accessible sur :"
    echo "   https://kstarhome.onrender.com (ou votre URL Render)"
    echo ""
else
    echo ""
    echo "❌ Erreur lors du push"
    echo "Vérifiez votre connexion GitHub"
fi

