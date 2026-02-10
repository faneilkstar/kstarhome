FROM python:3.12-slim
WORKDIR /app
# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# Copier requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copier le code de l'application
COPY . .
# Créer les dossiers nécessaires
RUN mkdir -p instance logs app/static/uploads app/static/exports app/static/avatars documents
# Exposer le port
EXPOSE 5000
# Commande de démarrage
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "run:app"]
