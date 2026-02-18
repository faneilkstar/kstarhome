#!/bin/bash

# 🚀 Script de déploiement automatique pour Vercel
# Author: K-Star
# Date: 18 Février 2026

echo "🚀 DÉPLOIEMENT KSTARHOME SUR VERCEL"
echo "===================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Vérifier qu'on est dans le bon dossier
if [ ! -f "run.py" ]; then
    echo -e "${RED}❌ Erreur: Lancez ce script depuis le dossier du projet${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Étape 1/4 : Vérification des fichiers...${NC}"
sleep 1

# Vérifier que les fichiers essentiels existent
files_to_check=("api/index.py" "vercel.json" "requirements.txt" "app/__init__.py")
all_files_ok=true

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file manquant${NC}"
        all_files_ok=false
    fi
done

if [ "$all_files_ok" = false ]; then
    echo -e "${RED}❌ Fichiers manquants. Déploiement annulé.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📝 Étape 2/4 : Ajout des fichiers à Git...${NC}"
git add -A
echo -e "${GREEN}✅ Fichiers ajoutés${NC}"

echo ""
echo -e "${YELLOW}💾 Étape 3/4 : Commit...${NC}"
git commit -m "🚀 Déploiement Vercel $(date '+%Y-%m-%d %H:%M:%S')" || echo "Rien à commiter"

echo ""
echo -e "${YELLOW}📤 Étape 4/4 : Push vers GitHub...${NC}"
echo ""
echo -e "${YELLOW}⚠️  Vous allez être invité à entrer vos identifiants GitHub${NC}"
echo -e "${YELLOW}Username: faneilkstar${NC}"
echo -e "${YELLOW}Password: [Votre Personal Access Token]${NC}"
echo ""

git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ ========================================${NC}"
    echo -e "${GREEN}✅ CODE ENVOYÉ SUR GITHUB AVEC SUCCÈS !${NC}"
    echo -e "${GREEN}✅ ========================================${NC}"
    echo ""
    echo -e "${YELLOW}📋 PROCHAINES ÉTAPES :${NC}"
    echo ""
    echo "1. Allez sur https://vercel.com"
    echo "2. Cliquez sur 'Add New' → 'Project'"
    echo "3. Importez 'kstarhome' depuis GitHub"
    echo "4. Dans Settings → Environment Variables, ajoutez :"
    echo ""
    echo "   DATABASE_URL = postgresql://postgres.pzzfqduntcmklrakhggy:masqquedemort@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
    echo ""
    echo "5. Cliquez sur Deploy"
    echo ""
    echo -e "${GREEN}🎉 Votre site sera en ligne dans 3-5 minutes !${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Erreur lors du push${NC}"
    echo ""
    echo -e "${YELLOW}💡 Solutions possibles :${NC}"
    echo "1. Vérifiez vos identifiants GitHub"
    echo "2. Utilisez un Personal Access Token au lieu du mot de passe"
    echo "3. Créez un token sur : https://github.com/settings/tokens"
    echo ""
    exit 1
fi

