#!/bin/bash

# Script pour configurer GitHub et pusher le code

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     🚀 CONFIGURATION GITHUB ET DÉPLOIEMENT           ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Nettoyer l'ancien remote s'il existe
git remote remove origin 2>/dev/null

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 ÉTAPE 1 : Créer le repository sur GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1. Ouvrez votre navigateur : ${GREEN}https://github.com${NC}"
echo "2. Connectez-vous à votre compte GitHub"
echo "3. Cliquez sur le bouton vert ${GREEN}'New'${NC} ou ${GREEN}'New repository'${NC}"
echo "4. Remplissez :"
echo "   - Repository name : ${GREEN}kstarhome${NC}"
echo "   - Description : ${GREEN}Système de gestion académique - Ing. KOISSI-ZO Tonyi Constantin${NC}"
echo "   - Sélectionnez ${GREEN}Public${NC} ✅"
echo "   - ${YELLOW}NE COCHEZ RIEN D'AUTRE${NC}"
echo "5. Cliquez ${GREEN}'Create repository'${NC}"
echo ""
echo -n "Appuyez sur Entrée quand le repository est créé..."
read

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}👤 ÉTAPE 2 : Nom d'utilisateur GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT : Entrez votre nom d'utilisateur GitHub EXACT${NC}"
echo ""
echo "Comment le trouver :"
echo "  1. Sur GitHub, cliquez sur votre photo de profil"
echo "  2. Vous verrez : 'Signed in as ${GREEN}VOTRE_USERNAME${NC}'"
echo "  3. Ou regardez l'URL de votre profil : github.com/${GREEN}USERNAME${NC}"
echo ""
echo "Exemples CORRECTS :"
echo "  ✅ ${GREEN}faneilkstar${NC}"
echo "  ✅ ${GREEN}kstar-de-la-kartz${NC}"
echo "  ✅ ${GREEN}tonyi-constantin${NC}"
echo ""
echo "Exemples INCORRECTS :"
echo "  ❌ ${RED}faneilkstar-créateur${NC} (avec accent)"
echo "  ❌ ${RED}KOISSI-ZO${NC} (si ce n'est pas votre username)"
echo ""

# Boucle pour redemander en cas d'erreur
while true; do
    echo -n "Entrez votre nom d'utilisateur GitHub : "
    read GITHUB_USERNAME

    # Vérifier que ce n'est pas vide
    if [ -z "$GITHUB_USERNAME" ]; then
        echo -e "${RED}❌ Le nom d'utilisateur ne peut pas être vide${NC}"
        continue
    fi

    # Vérifier les caractères spéciaux
    if [[ "$GITHUB_USERNAME" =~ [éèêëàâäôöûüçÉÈÊËÀÂÄÔÖÛÜÇ] ]]; then
        echo -e "${RED}❌ Le nom d'utilisateur contient des accents !${NC}"
        echo "   GitHub n'accepte que : lettres (a-z), chiffres (0-9), tirets (-)"
        continue
    fi

    echo ""
    echo -e "Vous avez entré : ${GREEN}$GITHUB_USERNAME${NC}"
    echo -n "Est-ce correct ? (o/n) : "
    read CONFIRM

    if [[ "$CONFIRM" == "o" || "$CONFIRM" == "O" ]]; then
        break
    fi
done

echo ""
echo -e "${GREEN}✅ Username confirmé : $GITHUB_USERNAME${NC}"
echo ""

# Configuration du remote
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔗 ÉTAPE 3 : Configuration du remote GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

REPO_URL="https://github.com/$GITHUB_USERNAME/kstarhome.git"
echo "Configuration du remote : ${GREEN}$REPO_URL${NC}"

git remote add origin "$REPO_URL"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Remote configuré avec succès${NC}"
else
    echo -e "${RED}❌ Erreur lors de la configuration du remote${NC}"
    exit 1
fi

# Renommer la branche
echo ""
echo "Renommage de la branche en 'main'..."
git branch -M main
echo -e "${GREEN}✅ Branche renommée${NC}"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔐 ÉTAPE 4 : Personal Access Token${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⚠️  GitHub va vous demander un TOKEN (pas votre mot de passe !)${NC}"
echo ""
echo "Comment créer un token :"
echo "  1. Sur GitHub, cliquez sur votre ${GREEN}photo de profil${NC}"
echo "  2. ${GREEN}Settings${NC}"
echo "  3. Descendez tout en bas : ${GREEN}Developer settings${NC}"
echo "  4. ${GREEN}Personal access tokens${NC} → ${GREEN}Tokens (classic)${NC}"
echo "  5. ${GREEN}Generate new token${NC} → ${GREEN}Generate new token (classic)${NC}"
echo "  6. Note : ${GREEN}KstarHome${NC}"
echo "  7. ☑️  Cochez ${GREEN}repo${NC} (tous les sous-éléments)"
echo "  8. ${GREEN}Generate token${NC}"
echo "  9. ${YELLOW}COPIEZ LE TOKEN${NC} (vous ne le reverrez plus !)"
echo ""
echo "GitHub demandera :"
echo "  ${BLUE}Username:${NC} $GITHUB_USERNAME"
echo "  ${BLUE}Password:${NC} [COLLEZ VOTRE TOKEN ICI]"
echo ""
echo -n "Appuyez sur Entrée quand votre token est prêt..."
read

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 ÉTAPE 5 : Envoi vers GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Envoi du code vers GitHub..."
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ SUCCÈS ! CODE SUR GITHUB ✅           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Votre code est maintenant sur :"
    echo "  ${GREEN}https://github.com/$GITHUB_USERNAME/kstarhome${NC}"
    echo ""

    # Générer une SECRET_KEY
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔑 SECRET_KEY générée pour Render${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null)
    echo "SECRET_KEY pour Render.com :"
    echo "${GREEN}$SECRET_KEY${NC}"
    echo ""
    echo "⚠️  COPIEZ CETTE CLÉ, vous en aurez besoin pour Render !"
    echo ""

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🌐 PROCHAINES ÉTAPES : Déployer sur Render.com${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "1️⃣  Allez sur : ${GREEN}https://render.com${NC}"
    echo ""
    echo "2️⃣  Cliquez : ${GREEN}Get Started for Free${NC}"
    echo "    → Connectez-vous avec ${GREEN}GitHub${NC}"
    echo ""
    echo "3️⃣  Créez un Web Service :"
    echo "    → Dashboard → ${GREEN}New +${NC} → ${GREEN}Web Service${NC}"
    echo "    → Sélectionnez votre repo ${GREEN}kstarhome${NC}"
    echo ""
    echo "4️⃣  Configuration :"
    echo "    ${YELLOW}Name:${NC}           kstarhome"
    echo "    ${YELLOW}Runtime:${NC}        Python 3"
    echo "    ${YELLOW}Build Command:${NC}  pip install -r requirements.txt"
    echo "    ${YELLOW}Start Command:${NC}  gunicorn run:app --bind 0.0.0.0:\$PORT"
    echo "    ${YELLOW}Instance Type:${NC}  Free"
    echo ""
    echo "5️⃣  Variables d'environnement (cliquez ${GREEN}Advanced${NC}) :"
    echo ""
    echo "    Ajoutez ces 3 variables :"
    echo ""
    echo "    ${YELLOW}Clé:${NC} FLASK_ENV"
    echo "    ${GREEN}Valeur:${NC} production"
    echo ""
    echo "    ${YELLOW}Clé:${NC} DEBUG"
    echo "    ${GREEN}Valeur:${NC} False"
    echo ""
    echo "    ${YELLOW}Clé:${NC} SECRET_KEY"
    echo "    ${GREEN}Valeur:${NC} $SECRET_KEY"
    echo ""
    echo "6️⃣  Cliquez : ${GREEN}Create Web Service${NC}"
    echo "    ⏳ Attendez 3-5 minutes (le déploiement se fait)"
    echo ""
    echo "7️⃣  Une fois déployé, dans ${GREEN}Shell${NC} Render :"
    echo "    ${YELLOW}python init_database.py${NC}"
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     🎉 Votre site sera sur kstarhome.onrender.com    ║${NC}"
    echo -e "${GREEN}╚══════════════════��════════════════════════════════════╝${NC}"
    echo ""
    echo "📖 Guide complet : ${BLUE}METHODE_RAPIDE_HEBERGEMENT.md${NC}"
    echo ""
    echo "© 2026 KstarHome - Ing. KOISSI-ZO Tonyi Constantin"
    echo ""

else
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ❌ ÉCHEC DU PUSH VERS GITHUB             ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Problèmes possibles :"
    echo "  ${YELLOW}1.${NC} Le repository ${RED}n'existe pas${NC} sur GitHub"
    echo "     → Vérifiez que vous avez bien créé 'kstarhome' sur GitHub"
    echo ""
    echo "  ${YELLOW}2.${NC} Le nom d'utilisateur ${RED}est incorrect${NC}"
    echo "     → Vérifiez votre username sur github.com/$GITHUB_USERNAME"
    echo ""
    echo "  ${YELLOW}3.${NC} Le token ${RED}est invalide${NC} ou n'a pas les bonnes permissions"
    echo "     → Créez un nouveau token avec la permission 'repo'"
    echo ""
    echo "  ${YELLOW}4.${NC} Vous avez utilisé votre ${RED}mot de passe${NC} au lieu d'un token"
    echo "     → GitHub n'accepte PLUS les mots de passe, utilisez un token"
    echo ""
    echo "Pour réessayer :"
    echo "  ${GREEN}./push_github.sh${NC}"
    echo ""
    exit 1
fi

