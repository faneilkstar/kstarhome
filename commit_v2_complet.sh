#!/bin/bash

# 🏗️ COMMIT COMPLET ARCHITECTURE V2 + IMPLÉMENTATION

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   🏗️ COMMIT ARCHITECTURE V2 + INTERFACES                       ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📦 Ajout des fichiers...${NC}"

# Modèles
git add app/models.py

# Routes
git add app/routes/departements.py
git add app/__init__.py

# Templates
git add app/templates/directeur/departements/

# Documentation
git add ARCHITECTURE_V2_UNIVERSITE.md
git add IMPLEMENTATION_V2_COMPLETE.md
git add GUIDE_MIGRATION_V2.md
git add 🏗️_ARCHITECTURE_V2_CRÉÉE.txt
git add ✅_IMPLEMENTATION_V2_TERMINÉE.txt

echo -e "${GREEN}✅ Fichiers ajoutés${NC}"
echo ""

echo -e "${YELLOW}💾 Création du commit...${NC}"

git commit -m "🏗️ Architecture V2 COMPLÈTE: Départements + Catégories UE + Interface

MODÈLES (Architecture V2):
- ✅ Departement (avec chef de département enseignant)
- ✅ Filiere refonte (departement_id + type_diplome: fondamental/professionnel)
- ✅ UE refonte majeure (catégorie + nature + type_affectation)

CATÉGORIES D'UE:
🔴 Fondamentale  - Le Core (Algo, Maths) - Obligatoire
🔵 Spécialité    - L'implémentation (Java, Réseaux)
🟢 Transversale  - Les Utils (Anglais, Droit) - Partagée
🟡 Libre         - Les Plugins (Sport, Arts) - Au choix

NATURE D'UE:
📦 Simple        - UE atomique classique
📦 Composite     - UE parent avec sous-UE

TRONC COMMUN:
🔄 Une UE enseignée à plusieurs classes EN MÊME TEMPS
🔄 UN SEUL enseignant pour toutes les classes
🔄 Union de classes, pas une filière spéciale

ROUTES & TEMPLATES:
- ✅ /directeur/departements/ - Liste des départements
- ✅ /directeur/departements/nouveau - Créer département
- ✅ /directeur/departements/<id> - Détails avec UE par catégorie (onglets)
- ✅ /directeur/departements/<id>/assigner-chef - Assigner chef département
- ✅ Templates avec visualisation séparée par catégorie
- ✅ Composant tableau UE réutilisable

RÈGLES MÉTIER:
- UE libre DOIT être simple (jamais composite)
- UE libre DOIT être ouverte à tous (est_ouverte_a_tous=True)
- Tronc commun = Mode d'affectation, pas une filière

DOCUMENTATION:
- ARCHITECTURE_V2_UNIVERSITE.md (Architecture complète)
- IMPLEMENTATION_V2_COMPLETE.md (Implémentation détaillée)
- GUIDE_MIGRATION_V2.md (Guide migration BDD)

PROCHAINE ÉTAPE:
flask db migrate -m 'Architecture V2'
flask db upgrade"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Commit créé avec succès !${NC}"
    echo ""
    echo -e "${YELLOW}📤 Pour pusher sur GitHub :${NC}"
    echo "   git push origin main"
    echo ""
    echo -e "${YELLOW}🔄 Prochaine étape - Migration BDD :${NC}"
    echo "   flask db migrate -m 'Architecture V2'"
    echo "   flask db upgrade"
    echo ""
else
    echo -e "${RED}❌ Erreur lors du commit${NC}"
    exit 1
fi

