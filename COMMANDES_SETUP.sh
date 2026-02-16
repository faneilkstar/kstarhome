#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 🚀 COMMANDES EXACTES À COPIER-COLLER DANS PYCHARM TERMINAL
# ═══════════════════════════════════════════════════════════════
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        🚀 SETUP SUPABASE - COMMANDES PYCHARM 🚀               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
# ───────────────────────────────────────────────────────────────
# ÉTAPE 1: ACTIVER LE VENV (IMPORTANT !)
# ───────────────────────────────────────────────────────────────
echo "📌 ÉTAPE 1: Activation du venv..."
source venv/bin/activate
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ venv activé: $VIRTUAL_ENV"
else
    echo "❌ ERREUR: venv non activé !"
    echo "   Créez-le avec: python3 -m venv venv"
    exit 1
fi
echo ""
# ───────────────────────────────────────────────────────────────
# ÉTAPE 2: GRAND NETTOYAGE
# ───────────────────────────────────────────────────────────────
echo "📌 ÉTAPE 2: Nettoyage des anciens fichiers..."
rm -rf migrations
rm -f instance/*.db
rm -f site.db app.db
echo "✅ Nettoyage terminé"
echo ""
# ───────────────────────────────────────────────────────────────
# ÉTAPE 3: VÉRIFIER .env
# ───────────────────────────────────────────────────────────────
echo "📌 ÉTAPE 3: Vérification de .env..."
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env introuvable !"
    echo "   Création depuis .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Éditez .env et ajoutez votre URL Supabase:"
    echo "   nano .env"
    echo ""
    echo "   SUPABASE_DB_URL=postgresql://postgres.xxx:PASSWORD@xxx.supabase.com:6543/postgres"
    echo ""
    read -p "Appuyez sur Enter après avoir configuré .env..."
fi
# Vérifier que SUPABASE_DB_URL est configuré
if ! grep -q "SUPABASE_DB_URL=" .env; then
    echo "❌ SUPABASE_DB_URL non trouvé dans .env !"
    echo "   Ajoutez cette ligne dans .env:"
    echo "   SUPABASE_DB_URL=postgresql://postgres.xxx:PASSWORD@xxx.supabase.com:6543/postgres"
    exit 1
fi
# Vérifier que ce n'est pas un placeholder
if grep -q "\[" .env; then
    echo "❌ Remplacez [TON_MOT_DE_PASSE] par votre vrai mot de passe dans .env !"
    exit 1
fi
echo "✅ .env configuré"
echo ""
# ───────────────────────────────────────────────────────────────
# ÉTAPE 4: INITIALISER FLASK-MIGRATE
# ───────────────────────────────────────────────────────────────
echo "📌 ÉTAPE 4: Initialisation de Flask-Migrate..."
export FLASK_APP=run.py
echo "   → flask db init"
flask db init
echo ""
echo "   → flask db migrate"
flask db migrate -m "Creation tables Supabase"
echo ""
echo "   → flask db upgrade"
flask db upgrade
echo "✅ Tables créées sur Supabase"
echo ""
# ───────────────────────────────────────────────────────────────
# ÉTAPE 5: CRÉER LE COMPTE ADMIN
# ───────────────────────────────────────────────────────────────
echo "📌 ÉTAPE 5: Création du compte admin..."
read -p "Créer le compte admin maintenant ? (O/n): " CREATE_ADMIN
if [[ "$CREATE_ADMIN" =~ ^[Nn]$ ]]; then
    echo "⏭️  Ignoré. Créez-le plus tard avec: python create_admin.py"
else
    python create_admin.py
fi
echo ""
# ───────────────────────────────────────────────────────────────
# ÉTAPE 6: RÉCAPITULATIF
# ───────────────────────────────────────────────────────────────
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║               ✅ SETUP TERMINÉ AVEC SUCCÈS ! ✅               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Pour lancer l'application:"
echo "   python run.py"
echo ""
echo "📊 Puis ouvrez:"
echo "   http://localhost:5000"
echo ""
echo "🔑 Connectez-vous avec:"
echo "   Identifiant: admin"
echo "   Mot de passe: admin123"
echo ""
echo "✅ Vos données sont maintenant sur Supabase !"
echo ""
