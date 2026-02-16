#!/bin/bash
# Script de démarrage rapide Harmony School
# Auteur: Ing. KOISSI-ZO Tonyi Constantin

echo "🎓 Harmony School - Démarrage"
echo "=============================="

# Tuer tous les processus Python sur le port 5000
echo "🔧 Nettoyage du port 5000..."
pkill -f "python.*run.py" 2>/dev/null
lsof -ti:5000 | xargs kill -9 2>/dev/null
sleep 2

# Activer l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé!"
    echo "📦 Créez-le avec: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate

# Vérifier les dépendances
echo "📦 Vérification des dépendances..."
pip install -q flask-jwt-extended google-genai 2>/dev/null

# Lancer l'application
echo "🚀 Lancement de l'application..."
echo ""
python run.py

