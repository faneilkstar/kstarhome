#!/bin/bash

# ========================================
# Script de Déploiement Rapide
# Par : Ing. KOISSI-ZO Tonyi Constantin
# Date : 12 Février 2026
# ========================================

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🚀 DÉPLOIEMENT AUTOMATIQUE          ║${NC}"
echo -e "${BLUE}║   K-Star Home Academic System         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Message de commit (par défaut ou fourni en argument)
MESSAGE="${1:-🔧 Mise à jour automatique}"

echo -e "${YELLOW}📝 Message du commit :${NC} $MESSAGE"
echo ""

# 1. Vérifier les changements
echo -e "${BLUE}🔍 Vérification des fichiers modifiés...${NC}"
git status --short

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur : Git n'est pas initialisé dans ce dossier${NC}"
    exit 1
fi

# Compter les fichiers modifiés
MODIFIED_COUNT=$(git status --short | wc -l)

if [ $MODIFIED_COUNT -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Aucun changement détecté. Rien à déployer.${NC}"
    exit 0
fi

echo -e "${GREEN}✅ $MODIFIED_COUNT fichier(s) modifié(s)${NC}"
echo ""

# 2. Tests rapides avant déploiement
echo -e "${BLUE}🧪 Tests de syntaxe Python...${NC}"

# Tester la syntaxe des fichiers Python modifiés
python3 -m py_compile app/**/*.py run.py 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur de syntaxe détectée ! Corrigez avant de déployer.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Syntaxe Python OK${NC}"
echo ""

# 3. Ajout des fichiers
echo -e "${BLUE}📦 Ajout des fichiers au commit...${NC}"
git add .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors de l'ajout des fichiers${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Fichiers ajoutés${NC}"
echo ""

# 4. Commit
echo -e "${BLUE}💾 Création du commit...${NC}"
git commit -m "$MESSAGE"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors du commit${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Commit créé${NC}"
echo ""

# 5. Push vers GitHub
echo -e "${BLUE}🚀 Push vers GitHub...${NC}"
git push origin main

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors du push${NC}"
    echo -e "${YELLOW}💡 Essayez : git pull origin main --rebase${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Push réussi !${NC}"
echo ""

# 6. Informations de déploiement
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ DÉPLOIEMENT DÉCLENCHÉ !           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Prochaines étapes :${NC}"
echo -e "  1. Render détecte automatiquement le push"
echo -e "  2. Build du nouveau code (1-2 min)"
echo -e "  3. Tests et vérifications"
echo -e "  4. Déploiement en production (3-5 min au total)"
echo ""
echo -e "${YELLOW}⏱️  Temps d'attente : 3-5 minutes${NC}"
echo ""
echo -e "${BLUE}🌐 Vérifier le déploiement :${NC}"
echo -e "  • Dashboard Render : https://dashboard.render.com"
echo -e "  • Logs : Section 'Events' du service"
echo ""
echo -e "${GREEN}🎉 C'est tout ! Le site sera mis à jour automatiquement.${NC}"

