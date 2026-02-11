"""
Script de migration pour ajouter les tables du laboratoire virtuel
"""

import sys
import os

# Ajouter le chemin racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import TP, SessionTP, MesureSimulation, InteractionIA

def migrate_database():
    """Créer les nouvelles tables pour le laboratoire"""
    app = create_app()

    with app.app_context():
        print("🔧 Création des tables du laboratoire virtuel...")

        try:
            # Créer toutes les tables
            db.create_all()
            print("✅ Tables créées avec succès!")

            # Vérifier que les tables existent
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()

            print("\n📋 Tables existantes:")
            for table in sorted(tables):
                print(f"  - {table}")

            # Vérifier spécifiquement les tables du laboratoire
            lab_tables = ['tps', 'sessions_tp', 'resultats_simulation', 'interactions_ia']
            print("\n🔬 Tables du laboratoire:")
            for table in lab_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} - MANQUANTE")

            print("\n🎉 Migration terminée avec succès!")

        except Exception as e:
            print(f"\n❌ Erreur lors de la migration: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrate_database()

