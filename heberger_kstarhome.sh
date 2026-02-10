#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════
#  🚀 SCRIPT D'HÉBERGEMENT AUTOMATIQUE - KSTARHOME
#  Créé par : Ing. KOISSI-ZO Tonyi Constantin
# ═══════════════════════════════════════════════════════════════════════

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonctions d'affichage
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

clear

cat << 'EOF'
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║        🌐 HÉBERGEMENT AUTOMATIQUE DE KSTARHOME                    ║
║                                                                    ║
║        Créé par : Ing. KOISSI-ZO Tonyi Constantin                 ║
║        Spécialité : Électronique de Puissance                     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

EOF

echo ""
info "Ce script va vous aider à mettre votre site en ligne"
echo ""

# ═══════════════════════════════════════════════════════════════════════
# ÉTAPE 1 : VÉRIFICATIONS
# ═══════════════════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
info "ÉTAPE 1/5 : Vérification de l'environnement"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier Git
if ! command -v git &> /dev/null; then
    error "Git n'est pas installé"
    info "Installation de Git..."
    sudo apt update && sudo apt install git -y
fi
success "Git est installé : $(git --version)"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    error "Python3 n'est pas installé"
    exit 1
fi
success "Python est installé : $(python3 --version)"

# Vérifier les fichiers nécessaires
if [ ! -f "run.py" ]; then
    error "Fichier run.py introuvable. Êtes-vous dans le bon dossier ?"
    exit 1
fi
success "Fichier run.py trouvé"

if [ ! -f "requirements.txt" ]; then
    error "Fichier requirements.txt introuvable"
    exit 1
fi
success "Fichier requirements.txt trouvé"

if [ ! -f "Procfile" ]; then
    warning "Procfile manquant, création..."
    echo "web: gunicorn run:app" > Procfile
fi
success "Procfile présent"

if [ ! -f "runtime.txt" ]; then
    warning "runtime.txt manquant, création..."
    echo "python-3.12.0" > runtime.txt
fi
success "runtime.txt présent"

echo ""

# ═══════════════════════════════════════════════════════════════════════
# ÉTAPE 2 : CONFIGURATION GIT
# ═══════════════════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
info "ÉTAPE 2/5 : Configuration de Git"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier si Git est configuré
if [ -z "$(git config --global user.name)" ]; then
    echo "Configuration de Git nécessaire."
    echo ""
    read -p "Votre nom complet : " git_name
    read -p "Votre email : " git_email
    git config --global user.name "$git_name"
    git config --global user.email "$git_email"
    success "Git configuré avec succès"
else
    success "Git déjà configuré : $(git config --global user.name)"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════
# ÉTAPE 3 : INITIALISATION DU REPOSITORY
# ═══════════════════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
info "ÉTAPE 3/5 : Préparation du code pour GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier si Git est déjà initialisé
if [ ! -d ".git" ]; then
    info "Initialisation du repository Git..."
    git init
    success "Repository Git initialisé"
else
    success "Repository Git déjà initialisé"
fi

# Créer .gitignore si nécessaire
if [ ! -f ".gitignore" ]; then
    info "Création du fichier .gitignore..."
    cat > .gitignore << 'GITIGNORE'
__pycache__/
*.py[cod]
*$py.class
venv/
ENV/
env/
.venv
instance/
*.db
*.sqlite
*.log
logs/
.env
app/static/uploads/*
!app/static/uploads/.gitkeep
app/static/exports/*
!app/static/exports/.gitkeep
.DS_Store
GITIGNORE
    success ".gitignore créé"
fi

# Ajouter tous les fichiers
info "Ajout des fichiers au repository..."
git add .

# Commit
if git diff-index --quiet HEAD -- 2>/dev/null; then
    warning "Aucun changement à commiter"
else
    info "Création du commit..."
    git commit -m "🎓 KstarHome - Système de Gestion Académique par Ing. KOISSI-ZO Tonyi Constantin"
    success "Commit créé avec succès"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════
# ÉTAPE 4 : CONNEXION À GITHUB
# ═══════════════════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
info "ÉTAPE 4/5 : Connexion à GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier si remote existe déjà
if git remote | grep -q "origin"; then
    warning "Remote 'origin' existe déjà"
    current_url=$(git remote get-url origin)
    echo "URL actuelle : $current_url"
    echo ""
    read -p "Voulez-vous la changer ? (o/n) : " change_remote
    if [ "$change_remote" = "o" ] || [ "$change_remote" = "O" ]; then
        git remote remove origin
        info "Remote supprimé"
    else
        success "Utilisation du remote existant"
        SKIP_REMOTE=true
    fi
fi

if [ -z "$SKIP_REMOTE" ]; then
    echo ""
    echo "📝 CRÉATION DU REPOSITORY SUR GITHUB"
    echo ""
    echo "1. Ouvrez votre navigateur"
    echo "2. Allez sur : https://github.com"
    echo "3. Connectez-vous (ou créez un compte si nécessaire)"
    echo "4. Cliquez sur '+' puis 'New repository'"
    echo "5. Repository name : kstarhome"
    echo "6. Cliquez sur 'Create repository'"
    echo ""
    echo "7. Copiez l'URL de votre repository"
    echo "   Exemple : https://github.com/votre-username/kstarhome.git"
    echo ""
    read -p "Collez l'URL de votre repository GitHub : " github_url

    if [ -z "$github_url" ]; then
        error "URL vide. Arrêt du script."
        exit 1
    fi

    git remote add origin "$github_url"
    success "Remote GitHub ajouté : $github_url"
fi

# Renommer la branche en main
git branch -M main
success "Branche renommée en 'main'"

echo ""
info "Envoi du code sur GitHub..."
echo ""
warning "GitHub va vous demander de vous authentifier"
echo ""
echo "💡 IMPORTANT : Vous devez utiliser un TOKEN GitHub (pas de mot de passe)"
echo ""
echo "Pour créer un token :"
echo "  1. GitHub → Settings → Developer settings"
echo "  2. Personal access tokens → Tokens (classic)"
echo "  3. Generate new token → Cochez 'repo'"
echo "  4. Générez et copiez le token"
echo "  5. Utilisez-le comme mot de passe quand Git vous le demande"
echo ""
read -p "Appuyez sur Entrée quand vous êtes prêt..."

# Push vers GitHub
if git push -u origin main; then
    success "Code envoyé sur GitHub avec succès ! 🎉"
else
    error "Échec de l'envoi sur GitHub"
    echo ""
    info "Solutions possibles :"
    echo "  1. Vérifiez que le repository existe sur GitHub"
    echo "  2. Vérifiez votre token d'authentification"
    echo "  3. Essayez : git push -u origin main --force"
    echo ""
    read -p "Voulez-vous réessayer avec --force ? (o/n) : " retry
    if [ "$retry" = "o" ]; then
        git push -u origin main --force && success "Push réussi !"
    else
        exit 1
    fi
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════
# ÉTAPE 5 : INSTRUCTIONS RENDER
# ═══════════════════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
info "ÉTAPE 5/5 : Déploiement sur Render.com"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

success "Votre code est maintenant sur GitHub ! 🎉"
echo ""

echo "🌐 MAINTENANT, SUR RENDER.COM :"
echo ""
echo "┌─────────────────────────────────────────────────────────────────┐"
echo "│ 1. Allez sur : https://render.com                               │"
echo "│ 2. Cliquez sur 'Get Started'                                    │"
echo "│ 3. Connectez-vous avec GitHub                                   │"
echo "│ 4. Cliquez sur 'New +' → 'Web Service'                         │"
echo "│ 5. Sélectionnez votre repository 'kstarhome'                   │"
echo "│                                                                  │"
echo "│ 6. Configuration :                                               │"
echo "│    Name: kstarhome                                              │"
echo "│    Build Command: pip install -r requirements.txt               │"
echo "│    Start Command: gunicorn run:app                              │"
echo "│    Plan: Free                                                    │"
echo "│                                                                  │"
echo "│ 7. Variables d'environnement (Advanced) :                      │"
echo "│    FLASK_ENV = production                                        │"
echo "│    DEBUG = False                                                 │"
echo "│    SECRET_KEY = [voir ci-dessous]                               │"
echo "│                                                                  │"
echo "│ 8. Cliquez 'Create Web Service'                                 │"
echo "│ 9. Attendez 3-5 minutes...                                      │"
echo "│ 10. Dans Shell Render : python3 init_database.py               │"
echo "└─────────────────────────────────────────────────────────────────┘"
echo ""

# Générer une SECRET_KEY
info "Génération d'une SECRET_KEY pour vous..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null)
if [ -n "$SECRET_KEY" ]; then
    echo ""
    echo "🔑 VOTRE SECRET_KEY (copiez-la) :"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$SECRET_KEY"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

echo ""
echo ""

cat << 'EOF'
🎉 APRÈS LE DÉPLOIEMENT SUR RENDER :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Votre site sera accessible sur :
   🌐 https://kstarhome.onrender.com

Comptes de connexion :
   👨‍💼 Directeur : directeur / directeur123
   👨‍🏫 Enseignant : prof / (voir PDF de détails)
   👨‍🎓 Étudiant : etudiant / etudiant123


📝 N'OUBLIEZ PAS :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Une fois le service créé sur Render, allez dans "Shell"
2. Exécutez : python3 init_database.py
3. Attendez que ça se termine
4. Votre site sera prêt ! 🎉


🔄 MISES À JOUR FUTURES :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quand vous modifiez votre code :
   git add .
   git commit -m "Description de la modification"
   git push

→ Render redéploiera automatiquement ! 🚀


═══════════════════════════════════════════════════════════════════════════
        ✨ KstarHome - Pour l'Excellence Académique ✨
           Créé par Ing. KOISSI-ZO Tonyi Constantin
═══════════════════════════════════════════════════════════════════════════

EOF

success "Script terminé ! Suivez les instructions ci-dessus pour déployer sur Render.com"

