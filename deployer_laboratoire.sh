#!/bin/bash

# 🚀 Script de déploiement rapide des nouvelles fonctionnalités

echo "╔═══════════════════════════════════════════════════════╗"
echo "║   🔬 DÉPLOIEMENT LABORATOIRE VIRTUEL - KSTARHOME     ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 ÉTAPE 1/4 : Vérification des fichiers${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "app/routes/laboratoire.py" ]; then
    echo -e "${GREEN}✅ Routes laboratoire présentes${NC}"
else
    echo -e "${YELLOW}❌ Fichier laboratoire.py manquant${NC}"
    exit 1
fi

if grep -q "laboratoire_bp" app/__init__.py; then
    echo -e "${GREEN}✅ Blueprint laboratoire enregistré${NC}"
else
    echo -e "${YELLOW}❌ Blueprint non enregistré${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🗃️  ÉTAPE 2/4 : Migration de la base de données${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Environnement virtuel activé${NC}"
else
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé${NC}"
fi

echo "Exécution de la migration..."
python migration_laboratoire.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migration réussie${NC}"
else
    echo -e "${YELLOW}❌ Échec de la migration${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📦 ÉTAPE 3/4 : Commit et Push vers GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Ajouter tous les changements
git add .

# Créer le commit
git commit -m "✨ Ajout du Laboratoire Virtuel avec simulations et assistants IA

Nouvelles fonctionnalités :
- 🧪 Création et gestion de TPs par les enseignants
- 📊 6 types de simulations interactives
- 🤖 3 assistants IA (ETA, ALPHA, KAYT)
- 📈 Suivi des performances et évaluations
- 💬 Historique des interactions IA
- 📝 Système de mesures et résultats

Tables ajoutées :
- tps
- sessions_tp
- mesures_simulation
- interactions_ia

Routes ajoutées :
- /laboratoire/* (hub, création TP, salle TP, résultats)

Fichiers modifiés/créés :
- app/routes/laboratoire.py (nouveau)
- app/__init__.py (blueprint enregistré)
- app/models.py (import Enum)
- app/templates/enseignant/base.html (lien laboratoire)
- app/templates/etudiant/dashboard_admis.html (lien laboratoire)
- migration_laboratoire.py (script de migration)
- NOUVELLES_FONCTIONNALITES.md (documentation)
- MISE_A_JOUR_TERMINEE.md (récapitulatif)
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Commit créé${NC}"
else
    echo -e "${YELLOW}⚠️  Rien à commiter ou erreur${NC}"
fi

# Push vers GitHub
echo ""
echo "Push vers GitHub..."
git push

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Code envoyé sur GitHub${NC}"
else
    echo -e "${YELLOW}❌ Échec du push${NC}"
    echo "Vérifiez votre connexion et vos identifiants GitHub"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🌐 ÉTAPE 4/4 : Instructions pour Render${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✅ Code déployé sur GitHub !${NC}"
echo ""
echo "Render va automatiquement redéployer votre site."
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT : Une fois le déploiement terminé sur Render${NC}"
echo ""
echo "Allez sur Render.com et exécutez dans le Shell :"
echo ""
echo -e "    ${GREEN}python migration_laboratoire.py${NC}"
echo ""
echo "Cela créera les nouvelles tables du laboratoire."
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🎉 DÉPLOIEMENT TERMINÉ !${NC}"
echo ""
echo "📖 Consultez MISE_A_JOUR_TERMINEE.md pour plus de détails"
echo "🌐 Votre site : https://kstarhome.onrender.com"
echo ""
echo "Nouvelles routes disponibles :"
echo "  - Enseignant : /laboratoire/enseignant"
echo "  - Étudiant : /laboratoire/etudiant"
echo "  - Directeur : /laboratoire/directeur"
echo ""
echo "© 2026 KstarHome - Ing. KOISSI-ZO Tonyi Constantin"
echo ""

