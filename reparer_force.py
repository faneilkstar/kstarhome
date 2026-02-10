from app import create_app, db
from app.models import User

app = create_app()


def remettre_le_directeur():
    with app.app_context():
        print("🔧 Réparation du compte Directeur en cours...")

        # 1. On supprime l'utilisateur 'directeur' s'il existe déjà (pour éviter les doublons)
        ancien = User.query.filter_by(username='directeur').first()
        if ancien:
            db.session.delete(ancien)
            print("   - Ancien compte supprimé.")

        # 2. On supprime aussi 'admin' si je t'ai fait le créer par erreur
        faux_admin = User.query.filter_by(username='admin').first()
        if faux_admin:
            db.session.delete(faux_admin)
            print("   - Compte 'admin' erroné supprimé.")

        # 3. CRÉATION DU VRAI DIRECTEUR
        directeur = User(
            username='directeur',  # <--- C'est ICI le nom que tu veux
            email='directeur@ecole.tg',
            role='DIRECTEUR',
            statut='actif'
        )

        # Le mot de passe que tu veux
        directeur.password = 'admin123'

        db.session.add(directeur)
        db.session.commit()

        print("\n" + "=" * 50)
        print("✅ COMPTE RÉTABLI AVEC SUCCÈS")
        print("=" * 50)
        print("👉 Identifiant : directeur")
        print("👉 Mot de passe : admin123")
        print("=" * 50)


if __name__ == '__main__':
    remettre_le_directeur()