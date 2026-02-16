#!/bin/bash
# Script de démarrage complet de KstarHome avec Supabase

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎓 KstarHome - Plateforme de Gestion Universitaire"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Arrêter les processus existants
echo "🛑 Arrêt des processus existants..."
pkill -9 -f "python.*run.py" 2>/dev/null
fuser -k 5000/tcp 2>/dev/null
sleep 2

# 2. Se placer dans le bon répertoire
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3

# 3. Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# 4. Afficher les informations de connexion
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 INFORMATIONS DE CONNEXION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 URL locale     : http://127.0.0.1:5000"
echo "👤 Identifiant    : admin"
echo "🔑 Mot de passe   : admin123"
echo "🎭 Rôle           : DIRECTEUR"
echo ""
echo "💾 Base de données: Supabase (aws-1-eu-west-1)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 5. Afficher les nouvelles fonctionnalités
echo "✨ NOUVELLES FONCTIONNALITÉS :"
echo "   • Création enseignant avec : date naissance, sexe, téléphone, adresse"
echo "   • Validation automatique IA des inscriptions (après 48h)"
echo "   • Script disponible : python validation_auto_inscriptions.py"
echo ""

# 6. Lancer l'application
echo "🚀 Démarrage de l'application..."
echo ""
python run.py

