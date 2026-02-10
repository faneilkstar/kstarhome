#!/bin/bash

# Script simplifié pour continuer le déploiement

echo "╔═══════════════════════════════════════════════════════╗"
echo "║   🎯 CONTINUER LE DÉPLOIEMENT DE KSTARHOME           ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 ÉTAPE 1 : Vérifier que le repository existe sur GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Avez-vous créé le repository 'kstarhome' sur GitHub ?"
echo "  1. Allez sur https://github.com"
echo "  2. Cliquez 'New repository'"
echo "  3. Nom : kstarhome"
echo "  4. Public ✅"
echo "  5. Create repository"
echo ""
echo -n "Appuyez sur Entrée quand c'est fait..."
read

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}👤 ÉTAPE 2 : Entrez votre nom d'utilisateur GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "⚠️  IMPORTANT : Entrez votre VRAI nom d'utilisateur GitHub"
echo "   (sans accents, sans caractères spéciaux)"
echo ""
echo "Exemples :"
echo "  ✅ faneilkstar"
echo "  ✅ kstar-de-la-kartz"
echo "  ❌ faneilkstar-créateur (avec accent)"
echo ""
echo -n "Votre nom d'utilisateur GitHub : "
read GITHUB_USERNAME

echo ""
echo -e "${GREEN}✅ Username : $GITHUB_USERNAME${NC}"
echo ""

# Configurer le remote
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔗 ÉTAPE 3 : Configuration du repository${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Vérifier si origin existe déjà
if git remote | grep -q "origin"; then
    echo "Suppression de l'ancien remote..."
    git remote remove origin
fi

echo "Ajout du remote GitHub..."
git remote add origin "https://github.com/$GITHUB_USERNAME/kstarhome.git"

echo -e "${GREEN}✅ Remote configuré : https://github.com/$GITHUB_USERNAME/kstarhome.git${NC}"
echo ""

# Renommer la branche
echo "Renommage de la branche en 'main'..."
git branch -M main
echo -e "${GREEN}✅ Branche renommée${NC}"
echo ""

# Instructions pour le token
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔐 ÉTAPE 4 : Préparez votre Personal Access Token${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⚠️  GitHub va vous demander un TOKEN (pas votre mot de passe !)${NC}"
echo ""
echo "Pour créer un token :"
echo "  1. GitHub → Settings → Developer settings"
echo "  2. Personal access tokens → Tokens (classic)"
echo "  3. Generate new token (classic)"
echo "  4. Note : KstarHome deployment"
echo "  5. Cochez : ☑️ repo (tous les sous-éléments)"
echo "  6. Generate token"
echo "  7. COPIEZ LE TOKEN"
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
echo "Quand demandé :"
echo "  Username: $GITHUB_USERNAME"
echo "  Password: [COLLEZ VOTRE TOKEN]"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ SUCCÈS ! CODE SUR GITHUB ✅           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🌐 PROCHAINES ÉTAPES : Déployer sur Render.com${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "1️⃣  Allez sur : ${GREEN}https://render.com${NC}"
    echo ""
    echo "2️⃣  Cliquez : ${GREEN}Get Started for Free${NC}"
    echo "    → Connectez-vous avec GitHub"
    echo ""
    echo "3️⃣  Créez un Web Service :"
    echo "    → Dashboard → New + → Web Service"
    echo "    → Sélectionnez votre repo ${GREEN}kstarhome${NC}"
    echo ""
    echo "4️⃣  Configuration :"
    echo "    ${YELLOW}Name:${NC} kstarhome"
    echo "    ${YELLOW}Runtime:${NC} Python 3"
    echo "    ${YELLOW}Build Command:${NC} pip install -r requirements.txt"
    echo "    ${YELLOW}Start Command:${NC} gunicorn run:app --bind 0.0.0.0:\$PORT"
    echo "    ${YELLOW}Instance Type:${NC} Free"
    echo ""
    echo "5️⃣  Variables d'environnement (cliquez Advanced) :"
    echo "    ${YELLOW}FLASK_ENV${NC} = production"
    echo "    ${YELLOW}DEBUG${NC} = False"
    echo "    ${YELLOW}SECRET_KEY${NC} = [Générez-en une ci-dessous]"
    echo ""
    echo "    Pour générer une SECRET_KEY :"
    echo "    ${GREEN}python3 -c \"import secrets; print(secrets.token_hex(32))\"${NC}"
    echo ""
    echo "6️⃣  Cliquez : ${GREEN}Create Web Service${NC}"
    echo ""
    echo "7️⃣  Une fois déployé, dans Shell Render :"
    echo "    ${YELLOW}python init_database.py${NC}"
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     🎉 Votre site sera sur kstarhome.onrender.com    ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
else
    echo ""
    echo -e "${YELLOW}❌ Échec du push vers GitHub${NC}"
    echo ""
    echo "Problèmes possibles :"
    echo "  1. Le repository n'existe pas sur GitHub"
    echo "  2. Le nom d'utilisateur est incorrect"
    echo "  3. Le token est invalide ou n'a pas les bonnes permissions"
    echo ""
    echo "Réessayez en exécutant :"
    echo "  ${GREEN}./continuer_deploiement.sh${NC}"
    echo ""
fi

