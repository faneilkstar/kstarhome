#!/usr/bin/env python3
"""
Script de migration pour ajouter le système de pondération des notes
"""
import sqlite3
from datetime import datetime

def migrate_database():
    db_path = "instance/academique_dev.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("🔄 Début de la migration...")

        # 1. Créer la table composantes_notes
        print("📝 Création de la table 'composantes_notes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS composantes_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ue_id INTEGER NOT NULL,
                nom VARCHAR(50) NOT NULL,
                ponderation FLOAT NOT NULL,
                ordre INTEGER DEFAULT 1,
                active BOOLEAN DEFAULT 1,
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ue_id) REFERENCES ues(id) ON DELETE CASCADE
            )
        """)

        # 2. Ajouter la colonne composante_id à la table notes (si elle n'existe pas)
        print("📝 Ajout de la colonne 'composante_id' à la table 'notes'...")
        try:
            cursor.execute("""
                ALTER TABLE notes ADD COLUMN composante_id INTEGER REFERENCES composantes_notes(id) ON DELETE SET NULL
            """)
            print("✅ Colonne 'composante_id' ajoutée avec succès")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("ℹ️  La colonne 'composante_id' existe déjà")
            else:
                raise

        # 3. Créer des index pour optimiser les requêtes
        print("📝 Création des index...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_composantes_ue_id ON composantes_notes(ue_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notes_composante_id ON notes(composante_id)
        """)

        conn.commit()
        print("✅ Migration terminée avec succès!")

        # Afficher un résumé
        cursor.execute("SELECT COUNT(*) FROM composantes_notes")
        nb_composantes = cursor.fetchone()[0]
        print(f"\n📊 Résumé:")
        print(f"   - Composantes de notes existantes: {nb_composantes}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de la migration: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()

