import os
from app import create_app, db
from app.models import User, Etudiant, Enseignant, Filiere, Classe, UE
from flask_migrate import upgrade

# 1. Initialisation de l'application
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# 2. Automatisation au lancement (Initialisation système)
with app.app_context():
    # Crée les tables si elles n'existent pas (pratique en dev)
    db.create_all()

    # Création du compte DIRECTEUR par défaut s'il n'existe pas
    admin = User.query.filter_by(role='DIRECTEUR').first()
    if not admin:
        print("--- Initialisation du compte Direction ---")
        admin_user = User(
            username="admin",
            email="admin@polytech.tg",
            role="DIRECTEUR"
        )
        admin_user.password = "admin123"  # Utilise ton système de hashage automatique
        db.session.add(admin_user)
        db.session.commit()
        print("Compte créé : admin / admin123")


# 3. Contexte du Shell (pour débugger en ligne de commande avec 'flask shell')
@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Etudiant=Etudiant,
        Enseignant=Enseignant,
        Filiere=Filiere,
        Classe=Classe,
        UE=UE
    )


# 4. Lancement du serveur
if __name__ == '__main__':
    # host='0.0.0.0' permet l'accès depuis d'autres appareils sur le même réseau
    app.run(host='0.0.0.0', port=5000, debug=True)