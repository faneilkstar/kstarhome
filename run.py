import os
from app import create_app, db
from app.models import User, Etudiant, Enseignant, Filiere, Classe, UE

# 1. Initialisation de l'application
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# 2. Contexte du Shell (pour débugger en ligne de commande avec 'flask shell')
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

# 3. Lancement du serveur
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)