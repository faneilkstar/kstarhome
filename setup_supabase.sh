#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🚀 SCRIPT DE SETUP COMPLET SUPABASE POUR KSTAR-HOME
# ═══════════════════════════════════════════════════════════════

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║        🚀 SETUP SUPABASE - KSTAR-HOME V3.0 🚀                 ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────
# ÉTAPE 1: Vérifications préalables
# ─────────────────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 ÉTAPE 1: Vérifications"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Vérifier que .env existe
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Fichier .env introuvable !${NC}"
    echo ""
    echo "Créez le fichier .env avec votre URL Supabase:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    echo "Puis relancez ce script."
    exit 1
fi

# Vérifier que SUPABASE_DB_URL est configuré
if ! grep -q "SUPABASE_DB_URL=" .env; then
    echo -e "${RED}❌ SUPABASE_DB_URL non configuré dans .env !${NC}"
    echo ""
    echo "Ajoutez cette ligne dans .env:"
    echo "  SUPABASE_DB_URL=postgresql://postgres.xxx:PASSWORD@xxx.supabase.com:6543/postgres"
    exit 1
fi

# Vérifier que le mot de passe n'est pas un placeholder
if grep -q "\[TON_MOT_DE_PASSE\]" .env || grep -q "\[YOUR-PASSWORD\]" .env; then
    echo -e "${RED}❌ Remplacez [TON_MOT_DE_PASSE] par votre vrai mot de passe dans .env !${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Fichier .env configuré${NC}"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé !${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 installé${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────
# ÉTAPE 2: Grand nettoyage
# ─────────────────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧹 ÉTAPE 2: Nettoyage des anciens fichiers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Supprimer migrations
if [ -d "migrations" ]; then
    echo "🗑️  Suppression de migrations/"
    rm -rf migrations
    echo -e "${GREEN}✅ Dossier migrations supprimé${NC}"
else
    echo "ℹ️  Pas de dossier migrations à supprimer"
fi

# Supprimer les anciens fichiers SQLite
for db_file in site.db app.db instance/*.db; do
    if [ -f "$db_file" ]; then
        echo "🗑️  Suppression de $db_file"
        rm -f "$db_file"
        echo -e "${GREEN}✅ $db_file supprimé${NC}"
    fi
done

# Supprimer __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo -e "${GREEN}✅ Caches Python nettoyés${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────
# ÉTAPE 3: Initialisation Flask-Migrate
# ─────────────────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ÉTAPE 3: Initialisation de Flask-Migrate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

export FLASK_APP=run.py

echo "📦 flask db init..."
if flask db init 2>&1 | tee /tmp/flask_init.log; then
    echo -e "${GREEN}✅ Initialisation réussie${NC}"
else
    if grep -q "already exists" /tmp/flask_init.log; then
        echo -e "${YELLOW}⚠️  Migrations déjà initialisées${NC}"
    else
        echo -e "${RED}❌ Erreur lors de l'initialisation${NC}"
        exit 1
    fi
fi
echo ""

# ─────────────────────────────────────────────────────────────────
# ÉTAPE 4: Génération de la migration
# ─────────────────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 ÉTAPE 4: Génération du script de migration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "🔍 flask db migrate -m 'Creation tables Supabase'..."
if flask db migrate -m "Creation tables Supabase" 2>&1 | tee /tmp/flask_migrate.log; then

    # Vérifier qu'il y a bien des tables détectées
    if grep -q "Detected" /tmp/flask_migrate.log; then
        echo -e "${GREEN}✅ Migration générée avec succès${NC}"
        echo ""
        echo "📋 Tables détectées:"
        grep "Detected" /tmp/flask_migrate.log | sed 's/^/   /'
    else
        echo -e "${YELLOW}⚠️  Aucune table détectée${NC}"
        echo "   Vérifiez vos modèles dans app/models.py"
    fi
else
    echo -e "${RED}❌ Erreur lors de la génération de la migration${NC}"
    cat /tmp/flask_migrate.log
    exit 1
fi
echo ""

# ─────────────────────────────────────────────────────────────────
# ÉTAPE 5: Application sur Supabase
# ─────────────────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 ÉTAPE 5: Création des tables sur Supabase"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏳ Cela peut prendre 10-30 secondes..."
echo ""

if flask db upgrade 2>&1 | tee /tmp/flask_upgrade.log; then
    if ! grep -qi "error" /tmp/flask_upgrade.log; then
        echo ""
        echo -e "${GREEN}✅ Tables créées avec succès sur Supabase !${NC}"
    else
        echo -e "${RED}❌ Erreur lors de la création des tables${NC}"
        cat /tmp/flask_upgrade.log
        exit 1
    fi
else
    echo -e "${RED}❌ Erreur lors de flask db upgrade${NC}"
    exit 1
fi
echo ""

# ─────────────────────────────────────────────────────────────────
# ÉTAPE 6: Création du compte admin
# ─────────────────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "👤 ÉTAPE 6: Création du compte administrateur"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Voulez-vous créer le compte admin maintenant ? (O/n): " CREATE_ADMIN

if [[ "$CREATE_ADMIN" =~ ^[Nn]$ ]]; then
    echo "⏭️  Ignoré. Vous pourrez le créer plus tard avec:"
    echo "   python3 create_admin.py"
else
    python3 create_admin.py
fi
echo ""

# ─────────────────────────────────────────────────────────────────
# ÉTAPE 7: Vérification finale
# ─────────────────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ÉTAPE 7: Vérification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "🔍 Test de connexion à Supabase..."
if python3 -c "
from app import create_app, db
app = create_app('development')
with app.app_context():
    result = db.session.execute(db.text('SELECT 1'))
    print('✅ Connexion Supabase OK')
" 2>/dev/null; then
    echo -e "${GREEN}✅ Base de données accessible${NC}"
else
    echo -e "${RED}❌ Problème de connexion${NC}"
    exit 1
fi
echo ""

# ─────────────────────────────────────────────────────────────────
# RÉCAPITULATIF FINAL
# ─────────────────────────────────────────────────────────────────
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║              🎉 SETUP TERMINÉ AVEC SUCCÈS ! 🎉                ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Ce qui a été fait:"
echo "   ✅ Anciens fichiers nettoyés"
echo "   ✅ Flask-Migrate initialisé"
echo "   ✅ Migration générée"
echo "   ✅ Tables créées sur Supabase"
echo "   ✅ Compte admin créé (si demandé)"
echo ""
echo "🚀 PROCHAINES ÉTAPES:"
echo ""
echo "1️⃣  Lancer l'application:"
echo "   python3 run.py"
echo ""
echo "2️⃣  Ouvrir dans le navigateur:"
echo "   http://localhost:5000"
echo ""
echo "3️⃣  Se connecter avec:"
echo "   👤 Identifiant: admin"
echo "   🔑 Mot de passe: admin123"
echo ""
echo "4️⃣  Vérifier les données sur Supabase:"
echo "   https://supabase.com/dashboard"
echo "   → Table Editor"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 CONSEIL: Changez le mot de passe admin après la 1ère connexion !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

