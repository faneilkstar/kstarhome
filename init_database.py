#!/usr/bin/env python
"""
Script d'initialisation de la base de données KstarHome
Crée toutes les tables et le compte administrateur par défaut
"""
import os
import sys

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Filiere, Classe

def init_database():
    """Initialiser la base de données"""
    print("=" * 60)
    print("🔄 INITIALISATION DE LA BASE DE DONNÉES KSTARHOME")
    print("=" * 60)
    print()

    # Créer l'application
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    with app.app_context():
        try:
            # Créer toutes les tables
            print("📋 Création des tables...")
            db.create_all()
            print("✅ Tables créées avec succès")
            print()

            # Créer le compte DIRECTEUR par défaut
            print("👤 Création du compte Directeur...")
            admin = User.query.filter_by(username='admin').first()

            if not admin:
                admin = User(
                    username='admin',
                    email='admin@kstarhome.com',
                    role='DIRECTEUR'
                )
                admin.password = 'admin123'
                db.session.add(admin)
                db.session.commit()
                print("✅ Compte DIRECTEUR créé :")
                print("   Username: admin")
                print("   Password: admin123")
                print("   ⚠️  Changez ce mot de passe en production !")
            else:
                print("ℹ️  Compte admin existe déjà")

            print()
            print("=" * 60)
            print("🎉 BASE DE DONNÉES INITIALISÉE AVEC SUCCÈS !")
            print("=" * 60)
            print()
            print("Vous pouvez maintenant lancer l'application avec :")
            print("   python run.py")
            print()
            print("Connexion Directeur :")
            print("   URL: http://localhost:5000")
            print("   Username: admin")
            print("   Password: admin123")
            print()

        except Exception as e:
            print()
            print("=" * 60)
            print("❌ ERREUR LORS DE L'INITIALISATION")
            print("=" * 60)
            print(f"Erreur: {e}")
            print()
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    init_database()

