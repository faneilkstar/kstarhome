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

    # ---------------------------------------------------------
    # FORCER SUPABASE (CONFIGURATION FINALE - IRLANDE)
    # ---------------------------------------------------------

    # Voici l'adresse exacte assemblée avec tes infos :
    DB_URL = "postgresql://postgres.pzzfqduntcmklrakhggy:masqquedemort@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'pool_pre_ping': True
    }
    print(f"🔗 [SUPABASE] Connexion forcée sur : aws-1-eu-west-1 (Port 6543)")
    # ---------------------------------------------------------

    # 2. Initialisation des composants avec l'instance de l'app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
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

    # CARTES : Cartes d'étudiant
    from app.routes.cartes import cartes_bp
    app.register_blueprint(cartes_bp, url_prefix='/cartes')

    # API IA : Intelligence Artificielle Gemini
    from app.routes.api_ia import bp as api_ia_bp
    app.register_blueprint(api_ia_bp)

    # 5. Filtres Jinja2 personnalisés
    # ---------------------------------------------------------
    @app.template_filter('ue_classe_name')
    def ue_classe_name(ue):
        """Retourne le nom de la classe d'une UE ou 'N/A'"""
        return ue.classe.nom_classe if ue.classe else 'Non assignée'

    @app.template_filter('ue_filiere_name')
    def ue_filiere_name(ue):
        """Retourne le nom de la filière d'une UE ou 'N/A'"""
        if ue.classe and ue.classe.filiere:
            return ue.classe.filiere.nom_filiere
        return 'N/A'

    return app


# 5. Chargeur d'utilisateur (Indispensable pour Flask-Login)
# ---------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    # Utilise get() car user_id est la clé primaire
    return User.query.get(int(user_id))