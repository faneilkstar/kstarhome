#!/bin/bash

# 🏗️ COMMIT ARCHITECTURE V2
# Architecture universitaire avec Départements + Catégories UE

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   🏗️ COMMIT ARCHITECTURE UNIVERSITAIRE V2                      ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📦 Ajout des fichiers modifiés...${NC}"
git add app/models.py
git add ARCHITECTURE_V2_UNIVERSITE.md
git add 🏗️_ARCHITECTURE_V2_CRÉÉE.txt

echo -e "${GREEN}✅ Fichiers ajoutés${NC}"
echo ""

echo -e "${YELLOW}💾 Création du commit...${NC}"
git commit -m "🏗️ Architecture V2: Départements + Types de diplôme + Catégories UE

NOUVEAUX MODÈLES:
- Département (avec chef de département)
- Filière refonte (type_diplome: fondamental/professionnel)
- UE refonte majeure (catégories: fondamentale/spécialité/transversale/libre)

CATÉGORIES D'UE:
🔴 Fondamentale - Le Core (Algo, Maths)
🔵 Spécialité - L'implémentation (Java, Réseaux)
🟢 Transversale - Les Utils (Anglais, Droit)
🟡 Libre - Les Plugins (Sport, Arts)

RÈGLES MÉTIER:
- UE libre DOIT être simple (pas composite)
- UE libre accessible à tous les étudiants
- Hiérarchie: Département → Filière → Classes → UE

Documentation: ARCHITECTURE_V2_UNIVERSITE.md"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Commit créé avec succès !${NC}"
    echo ""
    echo -e "${YELLOW}📤 Prêt pour push :${NC}"
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

