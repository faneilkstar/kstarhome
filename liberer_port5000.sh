#!/bin/bash

# 🛑 Script pour arrêter les processus Python qui bloquent le port 5000

echo "🔍 Recherche des processus sur le port 5000..."

# Trouver les PIDs
PIDS=$(lsof -ti:5000 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "✅ Aucun processus n'utilise le port 5000"
    exit 0
fi

echo "📋 Processus trouvés :"
lsof -i:5000

echo ""
echo "🛑 Arrêt des processus..."

# Arrêter proprement d'abord
for PID in $PIDS; do
    echo "   Arrêt du processus $PID..."
    kill $PID 2>/dev/null
done

# Attendre 2 secondes
sleep 2

# Vérifier si certains processus sont encore actifs
REMAINING=$(lsof -ti:5000 2>/dev/null)

if [ ! -z "$REMAINING" ]; then
    echo "⚠️  Certains processus résistent, arrêt forcé..."
    for PID in $REMAINING; do
        echo "   Arrêt forcé du processus $PID..."
        kill -9 $PID 2>/dev/null
    done
fi

# Vérification finale
sleep 1
FINAL_CHECK=$(lsof -ti:5000 2>/dev/null)

if [ -z "$FINAL_CHECK" ]; then
    echo "✅ Port 5000 libéré avec succès !"
    echo ""
    echo "Vous pouvez maintenant lancer votre application :"
    echo "   python run.py"
else
    echo "❌ Échec de la libération du port 5000"
    echo "Processus restants :"
    lsof -i:5000
    exit 1
fi

