#!/bin/bash
# Script de déploiement rapide
echo "🚀 Déploiement de l'application Académique Polytech"
echo "=================================================="
# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color
# Fonction pour afficher les messages
function info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}
function success() {
    echo -e "${GREEN}✅ $1${NC}"
}
function error() {
    echo -e "${RED}❌ $1${NC}"
}
# Menu de choix
echo ""
echo "Choisissez votre méthode de déploiement :"
echo "1) Déploiement local avec Gunicorn"
echo "2) Déploiement avec Docker"
echo "3) Configuration pour Render.com"
echo "4) Configuration pour PythonAnywhere"
echo "5) Configuration pour VPS (Nginx + Supervisor)"
echo "6) Quitter"
echo ""
read -p "Votre choix (1-6): " choice
case $choice in
    1)
        info "Déploiement local avec Gunicorn..."
        # Vérifier si gunicorn est installé
        if ! command -v gunicorn &> /dev/null; then
            info "Installation de gunicorn..."
            pip install gunicorn
        fi
        # Arrêter les processus existants
        info "Arrêt des processus existants..."
        pkill -f "gunicorn"
        # Lancer l'application
        success "Lancement de l'application..."
        gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 run:app --daemon
        success "Application lancée sur http://0.0.0.0:5000"
        success "Pour arrêter: pkill -f gunicorn"
        ;;
    2)
        info "Déploiement avec Docker..."
        # Vérifier si Docker est installé
        if ! command -v docker &> /dev/null; then
            error "Docker n'est pas installé. Installez-le depuis https://docker.com"
            exit 1
        fi
        # Construire l'image
        info "Construction de l'image Docker..."
        docker-compose build
        # Lancer les containers
        info "Lancement des containers..."
        docker-compose up -d
        success "Application lancée avec Docker!"
        echo ""
        info "Commandes utiles:"
        echo "  - Voir les logs: docker-compose logs -f"
        echo "  - Arrêter: docker-compose down"
        echo "  - Redémarrer: docker-compose restart"
        echo "  - Accéder: http://localhost"
        ;;
    3)
        info "Configuration pour Render.com..."
        echo ""
        echo "📝 Étapes à suivre:"
        echo ""
        echo "1. Créez un compte sur https://render.com"
        echo "2. Connectez votre repository GitHub"
        echo "3. Créez un nouveau Web Service avec ces paramètres:"
        echo ""
        echo "   Build Command: pip install -r requirements.txt"
        echo "   Start Command: gunicorn run:app"
        echo ""
        echo "4. Ajoutez ces variables d'environnement:"
        echo "   FLASK_ENV=production"
        echo "   SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
        echo ""
        success "Fichiers nécessaires déjà présents: Procfile, runtime.txt"
        ;;
    4)
        info "Configuration pour PythonAnywhere..."
        echo ""
        echo "📝 Étapes à suivre:"
        echo ""
        echo "1. Créez un compte sur https://www.pythonanywhere.com"
        echo "2. Dans la console Bash:"
        echo ""
        echo "   git clone votre-repo-url academique"
        echo "   cd academique"
        echo "   python3 -m venv venv"
        echo "   source venv/bin/activate"
        echo "   pip install -r requirements.txt"
        echo ""
        echo "3. Configurez l'application Web:"
        echo "   - Web → Add a new web app"
        echo "   - Manual configuration → Python 3.10"
        echo ""
        echo "4. Éditez le fichier WSGI pour pointer vers votre app"
        ;;
    5)
        info "Configuration pour VPS (Ubuntu/Debian)..."
        # Créer le fichier de configuration systemd
        cat > academique.service << 'SYSTEMD'
[Unit]
Description=Academique Polytech Web Application
After=network.target
[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/academique
Environment="PATH=/var/www/academique/venv/bin"
ExecStart=/var/www/academique/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 run:app
[Install]
WantedBy=multi-user.target
SYSTEMD
        # Créer la configuration Nginx
        cat > academique-nginx.conf << 'NGINX'
server {
    listen 80;
    server_name votre-domaine.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location /static {
        alias /var/www/academique/app/static;
        expires 30d;
    }
}
NGINX
        success "Fichiers de configuration créés!"
        echo ""
        echo "📝 Commandes à exécuter sur votre VPS:"
        echo ""
        echo "# 1. Installer les dépendances"
        echo "sudo apt update && sudo apt install python3-pip python3-venv nginx -y"
        echo ""
        echo "# 2. Copier votre code dans /var/www/academique"
        echo ""
        echo "# 3. Installer les dépendances Python"
        echo "cd /var/www/academique"
        echo "python3 -m venv venv"
        echo "source venv/bin/activate"
        echo "pip install -r requirements.txt"
        echo ""
        echo "# 4. Configurer systemd"
        echo "sudo cp academique.service /etc/systemd/system/"
        echo "sudo systemctl enable academique"
        echo "sudo systemctl start academique"
        echo ""
        echo "# 5. Configurer Nginx"
        echo "sudo cp academique-nginx.conf /etc/nginx/sites-available/academique"
        echo "sudo ln -s /etc/nginx/sites-available/academique /etc/nginx/sites-enabled/"
        echo "sudo nginx -t"
        echo "sudo systemctl restart nginx"
        echo ""
        echo "# 6. (Optionnel) SSL avec Let's Encrypt"
        echo "sudo apt install certbot python3-certbot-nginx -y"
        echo "sudo certbot --nginx -d votre-domaine.com"
        ;;
    6)
        info "Au revoir!"
        exit 0
        ;;
    *)
        error "Choix invalide"
        exit 1
        ;;
esac
echo ""
success "✨ Terminé!"
