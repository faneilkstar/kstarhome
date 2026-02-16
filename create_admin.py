#!/usr/bin/env python3
"""
Script pour créer le compte Administrateur/Directeur initial
À lancer après la migration vers Supabase
"""

import os
import sys
from getpass import getpass

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User

def create_admin():
    """Crée le compte administrateur initial"""

    print("=" * 60)
    print("🔧 CRÉATION DU COMPTE ADMINISTRATEUR")
    print("=" * 60)
    print()

    # Créer l'application
    app = create_app('development')

    with app.app_context():
        # Vérifier si un admin existe déjà
        admin_exist = User.query.filter_by(username='admin').first()

        if admin_exist:
            print("⚠️  Un utilisateur 'admin' existe déjà !")
            reponse = input("Voulez-vous le remplacer ? (o/N): ")
            if reponse.lower() not in ['o', 'oui', 'y', 'yes']:
                print("❌ Annulé.")
                return

            # Supprimer l'ancien admin
            db.session.delete(admin_exist)
            db.session.commit()
            print("✅ Ancien admin supprimé")

        # Demander les informations (ou utiliser les valeurs par défaut)
        print("\n📝 Configuration du compte administrateur:")
        print("   (Appuyez sur Entrée pour utiliser les valeurs par défaut)")
        print()

        username = input("Nom d'utilisateur [admin]: ").strip() or "admin"
        email = input("Email [admin@kstarhome.com]: ").strip() or "admin@kstarhome.com"

        # Mot de passe
        use_default = input("Utiliser le mot de passe par défaut 'admin123' ? (O/n): ")
        if use_default.lower() in ['n', 'non', 'no']:
            while True:
                password = getpass("Mot de passe: ")
                password_confirm = getpass("Confirmer le mot de passe: ")
                if password == password_confirm:
                    break
                else:
                    print("❌ Les mots de passe ne correspondent pas. Réessayez.")
        else:
            password = "admin123"

        print("\n⏳ Création en cours...")

        try:
            # Créer l'utilisateur DIRECTEUR
            admin = User(
                username=username,
                email=email,
                role='DIRECTEUR',
                statut='actif'
            )
            admin.set_password(password)
            db.session.add(admin)

            # Enregistrer
            db.session.commit()

            print()
            print("=" * 60)
            print("✅ SUCCÈS ! Compte administrateur créé")
            print("=" * 60)
            print()
            print(f"👤 Identifiant : {username}")
            print(f"🔑 Mot de passe : {password}")
            print(f"📧 Email       : {email}")
            print(f"👔 Rôle        : DIRECTEUR")
            print()
            print("=" * 60)
            print("✅ COMPTE ADMINISTRATEUR CRÉÉ AVEC SUCCÈS!")
            print("=" * 60)
            print()
            print("📋 INFORMATIONS DE CONNEXION:")
            print(f"   👤 Nom d'utilisateur: {username}")
            print(f"   🔑 Mot de passe: {password}")
            print(f"   📧 Email: {email}")
            print()
            print("🚀 Vous pouvez maintenant vous connecter sur:")
            print("   http://localhost:5000")
            print()
            print("=" * 60)

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERREUR lors de la création: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    create_admin()

