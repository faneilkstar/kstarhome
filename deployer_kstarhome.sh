#!/bin/bash

# 🚀 Script automatique de déploiement KstarHome
# Créateur : Ing. KOISSI-ZO Tonyi Constantin

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     🎓 DÉPLOIEMENT AUTOMATIQUE DE KSTARHOME 🎓       ║"
echo "║   Système de Gestion Académique - Version 2026       ║"
echo "║   Créateur : Ing. KOISSI-ZO Tonyi Constantin         ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'erreur
error_exit() {
    echo -e "${RED}❌ ERREUR: $1${NC}" >&2
    exit 1
}

# Fonction de succès
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Fonction d'info
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Fonction d'avertissement
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Vérification des prérequis
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 ÉTAPE 1/6 : Vérification des prérequis${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Vérifier git
if ! command -v git &> /dev/null; then
    error_exit "Git n'est pas installé. Installez-le avec: sudo apt install git"
fi
success "Git installé"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    error_exit "Python 3 n'est pas installé. Installez-le avec: sudo apt install python3"
fi
success "Python 3 installé"

# Vérifier requirements.txt
if [ ! -f "requirements.txt" ]; then
    error_exit "Fichier requirements.txt introuvable"
fi
success "requirements.txt trouvé"

# Vérifier gunicorn dans requirements.txt
if ! grep -q "gunicorn" requirements.txt; then
    warning "gunicorn n'est pas dans requirements.txt. Ajout..."
    echo "gunicorn==21.2.0" >> requirements.txt
    success "gunicorn ajouté à requirements.txt"
fi

echo ""

# Configuration Git
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}⚙️  ÉTAPE 2/6 : Configuration Git${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Vérifier si c'est déjà un repo git
if [ ! -d ".git" ]; then
    info "Initialisation du dépôt Git..."
    git init || error_exit "Échec de l'initialisation Git"
    success "Dépôt Git initialisé"
else
    success "Dépôt Git déjà initialisé"
fi

# Configurer git user si nécessaire
if [ -z "$(git config user.name)" ]; then
    info "Configuration de votre identité Git..."
    echo -n "Entrez votre nom (ex: KOISSI-ZO Tonyi Constantin): "
    read git_name
    git config user.name "$git_name"

    echo -n "Entrez votre email: "
    read git_email
    git config user.email "$git_email"

    success "Identité Git configurée"
fi

echo ""

# Création du .gitignore
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📝 ÉTAPE 3/6 : Création du .gitignore${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/*.db
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Uploads (optionnel - commentez si vous voulez versionner les uploads)
app/static/uploads/*
!app/static/uploads/.gitkeep
app/static/exports/*
!app/static/exports/.gitkeep

# Secrets
.env
config_local.py
EOF

success ".gitignore créé"
echo ""

# Ajout des fichiers
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📦 ÉTAPE 4/6 : Ajout des fichiers${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

git add . || error_exit "Échec de l'ajout des fichiers"
success "Fichiers ajoutés"

# Commit
if git diff --cached --quiet; then
    warning "Aucune modification à commiter"
else
    git commit -m "🎓 KstarHome - Application de gestion académique par Ing. KOISSI-ZO Tonyi Constantin" || error_exit "Échec du commit"
    success "Commit créé"
fi

echo ""

# Configuration du remote GitHub
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔗 ÉTAPE 5/6 : Configuration GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Vérifier si origin existe déjà
if git remote | grep -q "origin"; then
    info "Remote 'origin' existe déjà"
    git remote -v
    echo ""
    echo -n "Voulez-vous le remplacer ? (o/N): "
    read replace_remote
    if [[ "$replace_remote" == "o" || "$replace_remote" == "O" ]]; then
        git remote remove origin
        info "Remote 'origin' supprimé"
    else
        success "Utilisation du remote existant"
    fi
fi

# Ajouter le remote si nécessaire
if ! git remote | grep -q "origin"; then
    echo ""
    info "Configuration du repository GitHub..."
    echo ""
    echo "📌 INSTRUCTIONS :"
    echo "1. Allez sur https://github.com"
    echo "2. Cliquez sur 'New repository' (bouton vert)"
    echo "3. Nom du repository : kstarhome"
    echo "4. Description : Système de gestion académique - Ing. KOISSI-ZO Tonyi Constantin"
    echo "5. Choisissez 'Public'"
    echo "6. NE COCHEZ PAS 'Add a README'"
    echo "7. Cliquez 'Create repository'"
    echo ""
    echo -n "Appuyez sur Entrée quand c'est fait..."
    read

    echo ""
    echo -n "Entrez votre nom d'utilisateur GitHub: "
    read github_username

    git remote add origin "https://github.com/$github_username/kstarhome.git" || error_exit "Échec de l'ajout du remote"
    success "Remote GitHub configuré"
fi

echo ""

# Push vers GitHub
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 ÉTAPE 6/6 : Envoi vers GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

info "Renommage de la branche en 'main'..."
git branch -M main

echo ""
warning "GitHub va vous demander vos identifiants :"
echo "  - Username : votre nom d'utilisateur GitHub"
echo "  - Password : ⚠️  UTILISEZ UN PERSONAL ACCESS TOKEN (pas votre mot de passe !)"
echo ""
echo "📌 Pour créer un token :"
echo "  1. GitHub → Settings → Developer settings"
echo "  2. Personal access tokens → Tokens (classic)"
echo "  3. Generate new token (classic)"
echo "  4. Cochez 'repo'"
echo "  5. Copiez le token et utilisez-le comme mot de passe"
echo ""
echo -n "Appuyez sur Entrée pour continuer..."
read

echo ""
info "Envoi vers GitHub..."
git push -u origin main || error_exit "Échec du push vers GitHub"

success "Code envoyé sur GitHub !"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ SUCCÈS ! CODE SUR GITHUB ✅           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Instructions pour Render
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
echo "    ${YELLOW}SECRET_KEY${NC} = $(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "[Générez-en une]")"
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
echo "📖 Guide complet : ${BLUE}HEBERGEMENT_GITHUB_RENDER.md${NC}"
echo ""
echo "© 2026 KstarHome - Ing. KOISSI-ZO Tonyi Constantin"
echo "Spécialiste en Électronique de Puissance"
echo ""

