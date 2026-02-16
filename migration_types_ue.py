"""
Migration pour ajouter les types d'UE : Simple, Tronc Commun, Composite
- Ajout du champ type_ue_creation
- Ajout du champ ue_parent_id pour les UE composites

Date : 13 Février 2026
"""

from app import db, create_app
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("🔄 Migration des types d'UE...")

    try:
        # Vérifier si les colonnes existent déjà (PostgreSQL)
        with db.engine.connect() as conn:
            # Vérifier type_ue_creation
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='ues' AND column_name='type_ue_creation'
            """))

            if result.fetchone() is None:
                print("📝 Ajout de la colonne type_ue_creation...")
                conn.execute(text("ALTER TABLE ues ADD COLUMN type_ue_creation VARCHAR(20) DEFAULT 'simple'"))
                conn.commit()
                print("✅ Colonne type_ue_creation ajoutée")
            else:
                print("ℹ️  Colonne type_ue_creation existe déjà")

            # Vérifier ue_parent_id
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='ues' AND column_name='ue_parent_id'
            """))

            if result.fetchone() is None:
                print("📝 Ajout de la colonne ue_parent_id...")
                conn.execute(text("ALTER TABLE ues ADD COLUMN ue_parent_id INTEGER REFERENCES ues(id)"))
                conn.commit()
                print("✅ Colonne ue_parent_id ajoutée")
            else:
                print("ℹ️  Colonne ue_parent_id existe déjà")

            # Mettre à jour les UE existantes
            print("📝 Mise à jour des UE existantes...")
            conn.execute(text("UPDATE ues SET type_ue_creation = 'simple' WHERE type_ue_creation IS NULL"))
            conn.commit()
            print("✅ UE existantes mises à jour")

        print("\n🎉 Migration réussie !")
        print("\n📋 Types d'UE disponibles :")
        print("   - simple : UE normale (1 par classe)")
        print("   - tronc_commun : UE partagée (plusieurs classes, 1 prof)")
        print("   - composite : UE composée de sous-UE")

    except Exception as e:
        print(f"❌ Erreur lors de la migration : {e}")
        db.session.rollback()

