#!/bin/bash
#═══════════════════════════════════════════════════════════════
# SCRIPT DE DÉPLOIEMENT AUTOMATIQUE - KSTARHOME
# Créé par : Ing. KOISSI-ZO Tonyi Constantin
#═══════════════════════════════════════════════════════════════
# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
echo -e "${PURPLE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║      🚀 DÉPLOIEMENT AUTOMATIQUE KSTARHOME 🚀              ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
# Récupérer le message de commit
if [ -z "$1" ]; then
    echo -e "${YELLOW}📝 Entrez le message du commit :${NC}"
    read -p "→ " COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="🔄 Mise à jour automatique $(date '+%d/%m/%Y %H:%M')"
    fi
else
    COMMIT_MSG="$1"
fi
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📁 Ajout des fichiers modifiés...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
git add -A
# Vérifier s'il y a des changements
if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  Aucun changement à déployer.${NC}"
    exit 0
fi
echo -e "${GREEN}✅ Fichiers ajoutés !${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📝 Création du commit...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✅ Commit créé !${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 Push vers GitHub...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
git push origin main
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║               ✅ DÉPLOIEMENT RÉUSSI ! ✅                  ║"
    echo "║                                                           ║"
    echo "║   Render va automatiquement redéployer le site.          ║"
    echo "║   ⏱️  Attendez 3-5 minutes...                             ║"
    echo "║                                                           ║"
    echo "║   🌐 https://kstarhome.onrender.com                       ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${YELLOW}📊 Statut du déploiement :${NC}"
    echo -e "   → Vérifiez sur: ${CYAN}https://dashboard.render.com${NC}"
    echo ""
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 Votre site sera mis à jour dans quelques minutes !${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo ""
    echo -e "${RED}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║               ❌ ÉCHEC DU DÉPLOIEMENT ❌                  ║"
    echo "║                                                           ║"
    echo "║   Vérifiez votre connexion internet et réessayez.        ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    exit 1
fi
