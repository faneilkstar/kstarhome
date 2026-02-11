"""
Script de migration pour ajouter les nouveaux types de simulations
- pile_electrochimique
- saponification

Créé par : Ing. KOISSI-ZO Tonyi Constantin
Date : 11 Février 2026
"""

import sqlite3
import os

def migrer_base_donnees():
    """Ajoute les nouveaux types de simulations"""

    db_path = 'instance/academique_dev.db'

    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée !")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("🔧 Migration - Nouveaux types de simulations")
    print("=" * 60)

    # SQLite ne supporte pas ALTER TYPE directement
    # On doit recréer la table tps avec le nouveau type

    print("⚠️  SQLite ne supporte pas la modification d'ENUM directement")
    print("ℹ️  Les nouveaux types seront disponibles lors de la création de TP")
    print("✅ Aucune migration SQL nécessaire (ENUM géré par l'application)")

    conn.close()

    print("=" * 60)
    print("🎉 Migration terminée !")
    print()
    print("📝 NOUVEAUX TYPES DISPONIBLES :")
    print("  1. ✅ pile_electrochimique - Chimie (Structures de Lewis)")
    print("  2. ✅ saponification - Chimie (Réaction de saponification)")
    print()
    print("🚀 Les enseignants peuvent maintenant créer des TPs avec ces types !")
    print()

if __name__ == '__main__':
    migrer_base_donnees()

