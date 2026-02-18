#!/bin/bash

# 🚀 SCRIPT DE DÉPLOIEMENT RAPIDE POST-CORRECTION
# Fix: Read-only filesystem + URL Supabase corrigée

echo "🔧 DÉPLOIEMENT DES CORRECTIONS VERCEL"
echo "======================================="
echo ""

# Ajout des fichiers
echo "📦 Ajout des fichiers modifiés..."
git add config.py app/__init__.py
git add COMMANDES_DEPLOIEMENT.md ✅_LIRE_MOI_DEPLOIEMENT.txt
git add README_DEPLOIEMENT.md GUIDE_DEPLOIEMENT_VERCEL_FINAL.md
git add FIX_VERCEL_READ_ONLY.md

echo "✅ Fichiers ajoutés"
echo ""

# Commit
echo "💾 Création du commit..."
git commit -m "🔧 Fix Vercel: suppression dossier instance + correction URL Supabase (masque%20de%20mort, eu-central-1)"

echo ""
echo "📤 Push vers GitHub..."
echo ""
echo "⚠️  IDENTIFIANTS REQUIS :"
echo "   Username: faneilkstar"
echo "   Password: [Personal Access Token]"
echo ""

# Push
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ =========================================="
    echo "✅ CORRECTIONS ENVOYÉES SUR GITHUB !"
    echo "✅ =========================================="
    echo ""
    echo "📋 PROCHAINES ÉTAPES SUR VERCEL :"
    echo ""
    echo "1. Allez sur votre projet Vercel"
    echo "2. Settings → Environment Variables"
    echo "3. Ajoutez (ou modifiez) DATABASE_URL :"
    echo ""
    echo "   postgresql://postgres.pzzfqduntcmklrakhggy:masque%20de%20mort@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
    echo ""
    echo "4. Deployments → Redeploy"
    echo ""
    echo "✅ Plus d'erreur 'Read-only filesystem' !"
    echo ""
else
    echo ""
    echo "❌ Erreur lors du push"
    echo ""
    echo "💡 Assurez-vous d'avoir un Personal Access Token"
    echo "   Créez-en un sur : https://github.com/settings/tokens"
    echo ""
fi

