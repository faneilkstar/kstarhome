#!/usr/bin/env python3
"""
Script pour ajouter la colonne avatar à la table users
"""
import sqlite3
import sys
import os

# Chemin de la base de données
DB_PATH = "instance/academique_dev.db"

def ajouter_colonne_avatar():
    """Ajoute la colonne avatar à la table users si elle n'existe pas"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée : {DB_PATH}")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'avatar' in columns:
            print("✅ La colonne 'avatar' existe déjà dans la table users")
            conn.close()
            return True

        # Ajouter la colonne avatar
        print("📝 Ajout de la colonne 'avatar' à la table users...")
        cursor.execute("ALTER TABLE users ADD COLUMN avatar VARCHAR(200);")
        conn.commit()

        print("✅ Colonne 'avatar' ajoutée avec succès !")

        # Vérification
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'avatar' in columns:
            print(f"✅ Vérification OK - Colonnes users : {', '.join(columns)}")
        else:
            print("❌ Erreur : La colonne n'a pas été ajoutée")
            return False

        conn.close()
        return True

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ La colonne 'avatar' existe déjà")
            return True
        else:
            print(f"❌ Erreur SQL : {e}")
            return False
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 MIGRATION BASE DE DONNÉES - Ajout colonne avatar")
    print("=" * 60)

    success = ajouter_colonne_avatar()

    print("=" * 60)
    if success:
        print("✅ Migration réussie !")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ Migration échouée")
        print("=" * 60)
        sys.exit(1)

