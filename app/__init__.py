from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config

# Initialisation des instances d'extension (accessibles partout dans l'app)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name='default'):
    """Usine de création de l'application (Application Factory)"""
    app = Flask(__name__)

    # 1. Chargement de la configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 2. Initialisation des composants avec l'instance de l'app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 3. Configuration de la sécurité Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Veuillez vous connecter pour accéder à l'Espace Polytech."
    login_manager.login_message_category = "warning"

    # 4. Enregistrement des Blueprints (Moteurs de l'application)
    # ---------------------------------------------------------

    # AUTH : Racines et Connexion
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/')

    # DIRECTEUR : Administration et Recrutement
    from app.routes.directeur import bp as directeur_bp
    app.register_blueprint(directeur_bp, url_prefix='/directeur')

    # ENSEIGNANT : Gestion des notes et cours
    from app.routes.enseignant import bp as enseignant_bp
    app.register_blueprint(enseignant_bp, url_prefix='/enseignant')

    # ETUDIANT : Portail élèves
    from app.routes.etudiant import bp as etudiant_bp
    app.register_blueprint(etudiant_bp, url_prefix='/etudiant')

    # DOCUMENTS : Gestion des fichiers et supports
    from app.routes.documents import bp as documents_bp
    app.register_blueprint(documents_bp, url_prefix='/documents')

    # ABSENCES : Suivi de la discipline (CORRIGÉ : Maintenant bien enregistré)
    from app.routes.absences import bp as absences_bp
    app.register_blueprint(absences_bp, url_prefix='/absences')

    # LABORATOIRE : Simulations et TPs virtuels
    from app.routes.laboratoire import laboratoire_bp
    app.register_blueprint(laboratoire_bp, url_prefix='/laboratoire')

    return app


# 5. Chargeur d'utilisateur (Indispensable pour Flask-Login)
# ---------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    # Utilise get() car user_id est la clé primaire
    return User.query.get(int(user_id))