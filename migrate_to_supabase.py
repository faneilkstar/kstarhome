#!/usr/bin/env python3
"""
Script de Migration vers Supabase
Crée toutes les tables dans la base Supabase et migre les données si besoin
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import *  # Importer tous les modèles

def test_connection():
    """Teste la connexion à Supabase"""
    print("🔍 Test de connexion à Supabase...")

    try:
        # Tester une requête simple
        result = db.session.execute(db.text('SELECT version();'))
        version = result.scalar()
        print(f"✅ Connexion réussie !")
        print(f"   PostgreSQL version: {version}")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def create_tables():
    """Crée toutes les tables dans Supabase"""
    print("\n📦 Création des tables...")

    try:
        # Créer toutes les tables
        db.create_all()
        print("✅ Toutes les tables ont été créées avec succès !")

        # Afficher les tables créées
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📋 Tables créées ({len(tables)}):")
        for table in sorted(tables):
            print(f"   • {table}")

        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def init_default_data():
    """Initialise les données par défaut"""
    print("\n🌱 Initialisation des données par défaut...")

    try:
        from app.services.validation_ia import ValidationIA

        # Initialiser les paramètres système
        ValidationIA.initialiser_parametres_defaut()

        print("✅ Paramètres système initialisés")
        return True
    except Exception as e:
        print(f"⚠️  Avertissement lors de l'initialisation: {e}")
        return True  # Ce n'est pas critique

def migrate_from_sqlite(sqlite_path):
    """Migre les données depuis SQLite vers Supabase"""
    print(f"\n🔄 Migration depuis SQLite: {sqlite_path}")

    if not os.path.exists(sqlite_path):
        print(f"⚠️  Fichier SQLite introuvable: {sqlite_path}")
        return False

    try:
        # TODO: Implémenter la migration si nécessaire
        print("⚠️  Migration SQLite → Supabase pas encore implémentée")
        print("   Utilisez les outils d'export/import SQL si nécessaire")
        return True
    except Exception as e:
        print(f"❌ Erreur de migration: {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚀 MIGRATION VERS SUPABASE - KSTAR-HOME")
    print("=" * 60)

    # Vérifier que SUPABASE_DB_URL est configuré
    supabase_url = os.getenv('SUPABASE_DB_URL')
    if not supabase_url:
        print("\n❌ ERREUR: Variable SUPABASE_DB_URL non configurée !")
        print("\n📝 Instructions:")
        print("   1. Copiez .env.example vers .env")
        print("   2. Remplissez SUPABASE_DB_URL avec votre connexion Supabase")
        print("   3. Relancez ce script")
        sys.exit(1)

    # Vérifier que le mot de passe n'est pas un placeholder
    if '[TON_MOT_DE_PASSE]' in supabase_url:
        print("\n❌ ERREUR: Remplacez [TON_MOT_DE_PASSE] par votre vrai mot de passe !")
        print("\n📝 Éditez le fichier .env et remplacez [TON_MOT_DE_PASSE]")
        sys.exit(1)

    print(f"\n🔗 URL Supabase: {supabase_url[:50]}...")

    # Créer l'application
    print("\n🏗️  Création de l'application Flask...")
    app = create_app('development')

    with app.app_context():
        # Étape 1: Test de connexion
        if not test_connection():
            print("\n❌ Migration annulée: impossible de se connecter à Supabase")
            sys.exit(1)

        # Étape 2: Créer les tables
        if not create_tables():
            print("\n❌ Migration annulée: erreur lors de la création des tables")
            sys.exit(1)

        # Étape 3: Initialiser les données par défaut
        init_default_data()

        # Étape 4: Migration optionnelle depuis SQLite
        migrate_choice = input("\n❓ Voulez-vous migrer des données depuis SQLite ? (o/N): ")
        if migrate_choice.lower() in ['o', 'oui', 'y', 'yes']:
            sqlite_path = input("   Chemin du fichier SQLite: ").strip()
            if sqlite_path:
                migrate_from_sqlite(sqlite_path)

        print("\n" + "=" * 60)
        print("🎉 MIGRATION TERMINÉE AVEC SUCCÈS !")
        print("=" * 60)
        print("\n✅ Votre base de données Supabase est prête !")
        print("\n📝 Prochaines étapes:")
        print("   1. Testez localement: python run.py")
        print("   2. Sur Render, ajoutez SUPABASE_DB_URL dans Environment")
        print("   3. Déployez avec: ./deploy_auto.sh")
        print("\n💡 Conseil: Sauvegardez régulièrement via Supabase Dashboard")
        print("=" * 60)

if __name__ == '__main__':
    main()

