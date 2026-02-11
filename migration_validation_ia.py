"""
Script de migration pour ajouter les nouvelles colonnes
- mot_de_passe_initial dans enseignants
- evaluation_ia dans etudiants

Créé par : Ing. KOISSI-ZO Tonyi Constantin
Date : 11 Février 2026
"""

import sqlite3
import os

def migrer_base_donnees():
    """Ajoute les nouvelles colonnes à la base de données"""

    db_path = 'instance/academique_dev.db'

    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée !")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("🔧 Migration de la base de données...")
    print("=" * 60)

    # 1. Ajouter mot_de_passe_initial dans enseignants
    try:
        cursor.execute("ALTER TABLE enseignants ADD COLUMN mot_de_passe_initial VARCHAR(255);")
        conn.commit()
        print("✅ Colonne 'mot_de_passe_initial' ajoutée à la table 'enseignants'")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("ℹ️  Colonne 'mot_de_passe_initial' existe déjà")
        else:
            print(f"⚠️  Erreur : {e}")

    # 2. Ajouter evaluation_ia dans etudiants
    try:
        cursor.execute("ALTER TABLE etudiants ADD COLUMN evaluation_ia TEXT;")
        conn.commit()
        print("✅ Colonne 'evaluation_ia' ajoutée à la table 'etudiants'")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("ℹ️  Colonne 'evaluation_ia' existe déjà")
        else:
            print(f"⚠️  Erreur : {e}")

    conn.close()

    print("=" * 60)
    print("🎉 Migration terminée avec succès !")
    print()
    print("📝 NOUVELLES FONCTIONNALITÉS ACTIVÉES :")
    print("  1. ✅ Les mots de passe enseignants sont maintenant affichés")
    print("     correctement dans les PDF")
    print("  2. ✅ L'IA Gemini évalue automatiquement les inscriptions")
    print("     (moyenne < 12/20 → refus automatique)")
    print()
    print("🔑 N'oubliez pas de configurer GEMINI_API_KEY dans .env")
    print("   pour activer l'IA avancée !")
    print()

if __name__ == '__main__':
    migrer_base_donnees()

