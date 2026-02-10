from app import create_app, db
from app.models import User, Filiere, Classe

# Pas besoin d'importer generate_password_hash ici, le modèle s'en charge !

app = create_app()


def init_system():
    with app.app_context():
        # 1. Nettoyage et Création des tables
        print("Suppression des anciennes données...")
        db.drop_all()
        db.create_all()
        print("Tables créées avec succès.")

        # 2. Création du compte Directeur
        # On vérifie d'abord (même si drop_all a tout effacé, c'est une bonne pratique)
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='directeur@ecole.tg',  # J'ai ajouté l'email pour être complet
                role='DIRECTEUR',
                statut='actif'
            )
            # CORRECTION : On assigne le mot de passe en CLAIR.
            # Le modèle User va le hasher automatiquement grâce au @password.setter
            admin.password = 'admin123'

            db.session.add(admin)

        # 3. Création des données académiques de test
        # Création Filière
        filiere = Filiere(
            nom_filiere="INFORMATIQUE",
            code_filiere="INFO",
            cycle="Licence",
            description="Génie Logiciel et Systèmes"
        )
        db.session.add(filiere)
        db.session.flush()  # Important pour récupérer l'ID de la filière tout de suite

        # Création Classe
        classe = Classe(
            nom_classe="Licence 1",
            code_classe="L1-INFO",  # Ajout du code classe unique
            grade="L1",
            cycle="Licence",
            annee=1,
            filiere_id=filiere.id,
            capacite_max=50
        )
        db.session.add(classe)

        # Validation finale
        db.session.commit()

        print("=" * 40)
        print("✅ SYSTÈME INITIALISÉ AVEC SUCCÈS")
        print("=" * 40)
        print("👤 LOGIN    : admin")
        print("🔑 PASSWORD : admin123")
        print("=" * 40)


if __name__ == '__main__':
    init_system()