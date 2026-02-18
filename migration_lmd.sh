#!/bin/bash

# Script de mise à jour vers le système LMD complet

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🎓 MIGRATION SYSTÈME LMD COMPLET                            ║"
echo "║   Architecture V2 avec Semestres et UE Composites             ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
source venv/bin/activate

echo "📝 Vérification de la configuration Supabase..."
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL non configurée !"
    echo "⚠️  Consultez le fichier SUPABASE_CONFIGURATION.md"
    echo ""
    echo "Pour configurer DATABASE_URL :"
    echo "1. Allez sur https://supabase.com"
    echo "2. Settings → Database → Connection string"
    echo "3. Cochez 'Use connection pooling' + Transaction (Port 6543)"
    echo "4. Modifiez le fichier .env avec votre URL"
    echo ""
    exit 1
fi

echo "✅ DATABASE_URL configurée"
echo ""

echo "🗑️  Suppression des anciennes migrations SQLite..."
rm -rf migrations/versions/*.py 2>/dev/null
echo "✅ Anciennes migrations supprimées"
echo ""

echo "🔄 Création de la nouvelle migration LMD..."
flask db migrate -m "Système LMD Complet: Semestres S1-S10 + UE Composites avec EC"

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la création de la migration"
    exit 1
fi

echo "✅ Migration créée"
echo ""

echo "📤 Application de la migration sur Supabase..."
flask db upgrade

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'application de la migration"
    exit 1
fi

echo "✅ Migration appliquée sur Supabase"
echo ""

echo "🧪 Test de connexion..."
python -c "
from app import create_app, db
from app.models import UE, Departement

app = create_app()
with app.app_context():
    nb_ues = UE.query.count()
    nb_depts = Departement.query.count()
    print(f'✅ Connexion réussie !')
    print(f'   📊 UE: {nb_ues}')
    print(f'   📊 Départements: {nb_depts}')
"

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du test de connexion"
    exit 1
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   ✅ MIGRATION TERMINÉE AVEC SUCCÈS !                         ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📚 Documentation disponible :"
echo "   - SYSTEME_LMD_COMPLET.md : Guide complet du système LMD"
echo "   - app/services/ue_service.py : Service de gestion des UE"
echo ""
echo "🚀 Prochaines étapes :"
echo "   1. Créer des départements"
echo "   2. Créer des filières"
echo "   3. Créer des UE avec semestres (S1-S10)"
echo "   4. Créer des UE composites avec EC"
echo ""
echo "💡 Pour démarrer l'application :"
echo "   python run.py"
echo ""

