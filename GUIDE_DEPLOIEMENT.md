# Guide de Déploiement - Système de Gestion Académique

## 🚀 Options d'hébergement

Voici plusieurs options pour héberger votre application Flask :

---

## 1️⃣ **Render.com** (RECOMMANDÉ - Gratuit et Simple)

### Avantages :
- ✅ Gratuit avec limite généreuse
- ✅ Base de données PostgreSQL gratuite
- ✅ SSL automatique
- ✅ Déploiement automatique via Git

### Instructions :

1. **Créer un compte sur Render.com**
   - Allez sur https://render.com
   - Inscrivez-vous avec votre compte GitHub

2. **Créer un nouveau Web Service**
   - Cliquez sur "New +" → "Web Service"
   - Connectez votre repository GitHub

3. **Configuration**
   ```
   Name: academique-polytech
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn run:app
   ```

4. **Variables d'environnement**
   ```
   FLASK_ENV=production
   SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
   DATABASE_URL=(Render le générera automatiquement)
   ```

5. **Déployer** → Cliquez sur "Create Web Service"

---

## 2️⃣ **PythonAnywhere** (Gratuit, Facile)

### Avantages :
- ✅ 100% gratuit pour toujours
- ✅ Facile pour les débutants
- ✅ Console web intégrée

### Instructions :

1. **Créer un compte**
   - https://www.pythonanywhere.com
   - Choisissez le plan "Beginner" (gratuit)

2. **Uploader votre code**
   ```bash
   # Via console PythonAnywhere
   git clone https://github.com/votre-repo/academique.git
   cd academique
   ```

3. **Installer les dépendances**
   ```bash
   pip3 install --user -r requirements.txt
   ```

4. **Configurer l'application Web**
   - Allez dans "Web" → "Add a new web app"
   - Choisissez "Manual configuration" → Python 3.10
   - WSGI file: `/var/www/votre_username_pythonanywhere_com_wsgi.py`

5. **Éditer le fichier WSGI**
   ```python
   import sys
   path = '/home/votre_username/academique'
   if path not in sys.path:
       sys.path.append(path)
   
   from run import app as application
   ```

---

## 3️⃣ **Heroku** (Puissant mais payant maintenant)

### Note : Heroku n'est plus gratuit depuis novembre 2022

### Instructions :

1. **Installer Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Se connecter**
   ```bash
   heroku login
   ```

3. **Créer l'application**
   ```bash
   cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
   heroku create academique-polytech
   ```

4. **Ajouter PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Déployer**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

---

## 4️⃣ **Railway.app** (Moderne et Simple)

### Avantages :
- ✅ $5 gratuits par mois
- ✅ Déploiement automatique
- ✅ Base de données incluse

### Instructions :

1. **Créer un compte**
   - https://railway.app
   - Connexion via GitHub

2. **Nouveau projet**
   - "New Project" → "Deploy from GitHub repo"
   - Sélectionnez votre repository

3. **Configuration automatique**
   - Railway détecte automatiquement Python
   - Ajoute PostgreSQL si nécessaire

4. **Variables d'environnement**
   ```
   FLASK_ENV=production
   SECRET_KEY=votre-cle-secrete
   ```

---

## 5️⃣ **VPS Personnel** (DigitalOcean, Linode, AWS EC2)

### Pour un contrôle total (Recommandé pour production)

### Configuration sur Ubuntu Server :

```bash
# 1. Mise à jour du système
sudo apt update && sudo apt upgrade -y

# 2. Installer Python et dépendances
sudo apt install python3-pip python3-venv nginx supervisor -y

# 3. Créer un utilisateur
sudo adduser academique
sudo su - academique

# 4. Cloner le projet
git clone https://github.com/votre-repo/academique.git
cd academique

# 5. Environnement virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configuration Nginx
sudo nano /etc/nginx/sites-available/academique
```

**Fichier Nginx :**
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /home/academique/academique/app/static;
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/academique /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 7. Configuration Supervisor (pour maintenir l'app en ligne)
sudo nano /etc/supervisor/conf.d/academique.conf
```

**Fichier Supervisor :**
```ini
[program:academique]
command=/home/academique/academique/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 run:app
directory=/home/academique/academique
user=academique
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/academique/err.log
stdout_logfile=/var/log/academique/out.log
```

```bash
# Démarrer l'application
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start academique

# 8. SSL avec Let's Encrypt (HTTPS)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d votre-domaine.com
```

---

## 6️⃣ **Docker + Docker Compose** (Pour déploiement containerisé)

Créez ces fichiers dans votre projet :

**Dockerfile :**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p instance logs app/static/uploads app/static/exports

# Exposer le port
EXPOSE 5000

# Commande de démarrage
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

**docker-compose.yml :**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=changez-cette-cle-secrete
    volumes:
      - ./instance:/app/instance
      - ./logs:/app/logs
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./app/static:/usr/share/nginx/html/static
    depends_on:
      - web
    restart: unless-stopped
```

**Déployer avec Docker :**
```bash
# Construire l'image
docker-compose build

# Lancer l'application
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter l'application
docker-compose down
```

---

## 📝 **Fichiers déjà préparés dans votre projet**

✅ **Procfile** - Pour Heroku/Render
```
web: gunicorn run:app
```

✅ **runtime.txt** - Version Python
```
python-3.12.0
```

✅ **requirements.txt** - Dépendances (avec gunicorn ajouté)

---

## 🔒 **Sécurité et Configuration**

### Variables d'environnement à configurer :

```bash
# Secret key (générez-en une nouvelle !)
SECRET_KEY=votre-cle-tres-secrete-et-aleatoire-123456

# Environnement
FLASK_ENV=production

# Base de données (si PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/database

# Debug (TOUJOURS False en production)
DEBUG=False
```

### Générer une clé secrète :
```python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🎯 **Ma Recommandation**

Pour commencer rapidement et gratuitement :

1. **PythonAnywhere** - Si vous voulez quelque chose de simple et gratuit pour toujours
2. **Render.com** - Si vous voulez une solution moderne avec base de données
3. **VPS (DigitalOcean)** - Si vous voulez un contrôle total (~$6/mois)

---

## 📞 **Support**

Si vous choisissez une de ces options, je peux vous aider avec :
- La configuration détaillée
- Le débogage des erreurs
- L'optimisation des performances
- La configuration du domaine personnalisé

**Quelle option préférez-vous ?** 🚀

