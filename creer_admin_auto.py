#!/usr/bin/env python3
"""Création automatique de l'admin"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User

app = create_app('development')

with app.app_context():
    print("🔍 Vérification de l'utilisateur admin...")

    # Supprimer l'ancien admin s'il existe
    admin_exist = User.query.filter_by(username='admin').first()
    if admin_exist:
        print("⚠️  Admin existant trouvé, suppression...")
        db.session.delete(admin_exist)
        db.session.commit()

    # Créer le nouvel admin
    print("✨ Création de l'administrateur...")
    admin = User(
        username='admin',
        email='admin@kstarhome.com',
        role='DIRECTEUR',
        statut='actif'
    )
    admin.set_password('admin123')

    db.session.add(admin)
    db.session.commit()

    print("\n" + "=" * 70)
    print("✅ ADMINISTRATEUR CRÉÉ AVEC SUCCÈS!")
    print("=" * 70)
    print(f"👤 Identifiant : admin")
    print(f"🔑 Mot de passe : admin123")
    print(f"📧 Email       : admin@kstarhome.com")
    print(f"🎭 Rôle        : DIRECTEUR")
    print("=" * 70)
    print("\n🚀 Tu peux maintenant te connecter sur http://127.0.0.1:5000")

