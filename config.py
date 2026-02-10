import os
from datetime import timedelta

# Chemin racine du projet
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuration de base commune à tous les environnements"""

    # --- SÉCURITÉ ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ma-cle-secrete-super-securisee-2024'

    # Durée de vie de la session (déconnexion auto après 60 min d'inactivité)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)

    # --- BASE DE DONNÉES ---
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Par défaut, on enregistre l'heure des requêtes lentes
    SQLALCHEMY_RECORD_QUERIES = True

    # --- GESTION DES FICHIERS (Uploads) ---
    # Limite la taille des fichiers à 16 MB (Évite les attaques par saturation)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    DOCUMENTS_FOLDER = os.path.join(basedir, 'documents')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

    # --- PARAMÈTRES ACADÉMIQUES LMD (CONSTANTES) ---
    ANNEE_ACADEMIQUE_ACTUELLE = "2025-2026"
    CREDITS_SEMESTRE = 30
    CREDITS_ANNEE = 60
    NOTE_PASSAGE = 10.0
    NOTE_ELIMINATOIRE = 6.0  # Utile pour les règles de compensation

    @staticmethod
    def init_app(app):
        """Initialisation automatique des dossiers au démarrage"""
        os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
        os.makedirs(Config.DOCUMENTS_FOLDER, exist_ok=True)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        # Sous-dossiers pour organiser les uploads
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'photos'), exist_ok=True)
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'justificatifs'), exist_ok=True)


class DevelopmentConfig(Config):
    """Configuration pour le développement (votre machine)"""
    DEBUG = True
    # Affiche les requêtes SQL dans la console (très utile pour debug)
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'academique_dev.db')


class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'academique_test.db')
    WTF_CSRF_ENABLED = False  # Désactive la protection CSRF pour faciliter les tests


class ProductionConfig(Config):
    """Configuration pour le déploiement réel"""
    DEBUG = False
    # En production, on utilise souvent PostgreSQL ou MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'academique_prod.db')


# Dictionnaire pour choisir l'environnement facilement
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}