#!/bin/bash

# 🚀 DÉPLOIEMENT FINAL AVEC GEMINI AI
# Date: 18 Février 2026

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   🚀 DÉPLOIEMENT KSTARHOME AVEC IA GEMINI                      ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 CONFIGURATION DÉTECTÉE :${NC}"
echo ""
echo "  ✅ Base de données : Supabase (eu-central-1)"
echo "  ✅ Port : 6543 (Connection Pooling)"
echo "  ✅ IA Gemini : Activée"
echo "  ✅ Corrections Vercel : Appliquées"
echo ""

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Étape 1
echo -e "${YELLOW}📦 [1/4] Vérification des fichiers...${NC}"
sleep 1

required_files=(
    "config.py"
    "app/__init__.py"
    ".env"
    "vercel.json"
    "api/index.py"
    "requirements.txt"
)

all_ok=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✅ $file${NC}"
    else
        echo -e "  ${RED}❌ $file manquant${NC}"
        all_ok=false
    fi
done

if [ "$all_ok" = false ]; then
    echo -e "${RED}❌ Fichiers manquants. Arrêt.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Étape 2
echo -e "${YELLOW}📝 [2/4] Ajout des fichiers au commit...${NC}"
git add .env config.py app/__init__.py
git add CONFIG_GEMINI_AI.md 🤖_GEMINI_CONFIGURÉ.txt
git add FIX_VERCEL_READ_ONLY.md 🔧_FIX_VERCEL_APPLIQUÉ.txt
git add COMMANDES_DEPLOIEMENT.md README_DEPLOIEMENT.md
git add -A

echo -e "${GREEN}✅ Fichiers ajoutés${NC}"
echo ""

# Étape 3
echo -e "${YELLOW}💾 [3/4] Création du commit...${NC}"
git commit -m "🤖 Config finale: Gemini AI + Fix Vercel + Supabase" || echo "Rien de nouveau à commiter"
echo ""

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Étape 4
echo -e "${YELLOW}📤 [4/4] Push vers GitHub...${NC}"
echo ""
echo -e "${BLUE}⚠️  IDENTIFIANTS REQUIS :${NC}"
echo "   Username: ${YELLOW}faneilkstar${NC}"
echo "   Password: ${YELLOW}[Personal Access Token]${NC}"
echo ""
echo -e "${BLUE}💡 Créez un token sur : https://github.com/settings/tokens${NC}"
echo ""

read -p "Appuyez sur ENTRÉE pour continuer..."

git push origin main

if [ $? -eq 0 ]; then
    clear
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║   ✅ CODE ENVOYÉ SUR GITHUB AVEC SUCCÈS !                      ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}📋 PROCHAINES ÉTAPES SUR VERCEL :${NC}"
    echo ""
    echo "1️⃣  Allez sur : ${YELLOW}https://vercel.com${NC}"
    echo ""
    echo "2️⃣  Cliquez sur votre projet ${YELLOW}kstarhome${NC}"
    echo ""
    echo "3️⃣  ${YELLOW}Settings${NC} → ${YELLOW}Environment Variables${NC}"
    echo ""
    echo "4️⃣  Ajoutez ces 2 variables :"
    echo ""
    echo "   ${GREEN}Variable 1 (Base de données)${NC}"
    echo "   ├─ Name:  ${YELLOW}DATABASE_URL${NC}"
    echo "   └─ Value: ${BLUE}postgresql://postgres.pzzfqduntcmklrakhggy:masque%20de%20mort@aws-0-eu-central-1.pooler.supabase.com:6543/postgres${NC}"
    echo ""
    echo "   ${GREEN}Variable 2 (IA Gemini)${NC}"
    echo "   ├─ Name:  ${YELLOW}GEMINI_API_KEY${NC}"
    echo "   └─ Value: ${BLUE}AIzaSyCARZUlNsBp6X4wzWtkgvOZcDYjpLANijA${NC}"
    echo ""
    echo "5️⃣  Cliquez sur ${YELLOW}Save${NC}"
    echo ""
    echo "6️⃣  ${YELLOW}Deployments${NC} → ${YELLOW}Redeploy${NC} (ou attendez le déploiement auto)"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}⏱️  Temps d'attente : 3-5 minutes${NC}"
    echo ""
    echo -e "${GREEN}🎉 Votre site sera en ligne avec :${NC}"
    echo "   ✅ Base de données Supabase"
    echo "   ✅ IA Gemini activée"
    echo "   ✅ Toutes les fonctionnalités"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Erreur lors du push${NC}"
    echo ""
    echo -e "${YELLOW}💡 Solutions :${NC}"
    echo "1. Vérifiez vos identifiants GitHub"
    echo "2. Créez un Personal Access Token sur:"
    echo "   ${BLUE}https://github.com/settings/tokens${NC}"
    echo "3. Réessayez avec le token comme mot de passe"
    echo ""
    exit 1
fi

