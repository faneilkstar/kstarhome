"""
Migration pour améliorer le système d'attribution des UE
- Créer une table d'association ue_classe (many-to-many)
- Rendre classe_id optionnel dans la table ues
- Une UE peut maintenant être attribuée à plusieurs classes

Date : 12 Février 2026
Par : Ing. KOISSI-ZO Tonyi Constantin
"""

from app import db, create_app
from app.models import UE, Classe
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("🔄 Migration du système d'attribution des UE...")

    # 1. Créer la table d'association ue_classe
    print("📝 Création de la table ue_classe...")

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS ue_classe (
        ue_id INTEGER NOT NULL,
        classe_id INTEGER NOT NULL,
        date_attribution DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (ue_id, classe_id),
        FOREIGN KEY (ue_id) REFERENCES ues(id) ON DELETE CASCADE,
        FOREIGN KEY (classe_id) REFERENCES classes(id) ON DELETE CASCADE
    );
    """

    db.session.execute(text(create_table_sql))
    db.session.commit()
    print("✅ Table ue_classe créée")

    # 2. Migrer les données existantes vers la nouvelle table
    print("📦 Migration des attributions existantes...")

    ues_existantes = UE.query.filter(UE.classe_id != None).all()

    for ue in ues_existantes:
        # Insérer dans la table d'association
        insert_sql = text("""
            INSERT OR IGNORE INTO ue_classe (ue_id, classe_id) 
            VALUES (:ue_id, :classe_id)
        """)

        db.session.execute(insert_sql, {'ue_id': ue.id, 'classe_id': ue.classe_id})

    db.session.commit()
    print(f"✅ {len(ues_existantes)} attributions migrées")

    # 3. Créer un index pour les performances
    print("🔍 Création des index...")

    create_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_ue_classe_ue ON ue_classe(ue_id);
    CREATE INDEX IF NOT EXISTS idx_ue_classe_classe ON ue_classe(classe_id);
    """

    db.session.execute(text(create_index_sql))
    db.session.commit()
    print("✅ Index créés")

    print("\n🎉 Migration terminée avec succès !")
    print("\n📋 Prochaines étapes :")
    print("1. Modifier le modèle UE pour utiliser la relation many-to-many")
    print("2. Mettre à jour les routes pour gérer les attributions multiples")
    print("3. Créer l'interface pour attribuer les UE aux classes")

