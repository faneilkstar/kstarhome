import os
from datetime import timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Chemin racine du projet
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuration de base commune à tous les environnements"""

    # --- SÉCURITÉ ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ma-cle-secrete-super-securisee-2024'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)

    # --- BASE DE DONNÉES ---
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # --- GESTION DES FICHIERS (Uploads) ---
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    DOCUMENTS_FOLDER = os.path.join(basedir, 'documents')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

    # --- PARAMÈTRES ACADÉMIQUES ---
    ANNEE_ACADEMIQUE_ACTUELLE = "2025-2026"
    CREDITS_SEMESTRE = 30
    CREDITS_ANNEE = 60
    NOTE_PASSAGE = 10.0
    NOTE_ELIMINATOIRE = 6.0

    # --- SÉCURITÉ JWT ---
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'votre-cle-secrete-jwt-super-longue')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # --- API ---
    API_TITLE = 'Harmony School API'
    API_VERSION = 'v1'
    API_RATE_LIMIT = '100 per hour'

    @staticmethod
    def init_app(app):
        """Création automatique des dossiers nécessaires"""
        os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
        os.makedirs(Config.DOCUMENTS_FOLDER, exist_ok=True)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'photos'), exist_ok=True)
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'justificatifs'), exist_ok=True)


class DevelopmentConfig(Config):
    """Configuration développement"""
    DEBUG = True
    SQLALCHEMY_ECHO = False

    # Configuration Supabase (si disponible)
    DB_URL = os.environ.get('SUPABASE_DB_URL')

    # Fix pour Supabase
    if DB_URL and DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

    # Utiliser Supabase si configuré, sinon SQLite local
    if DB_URL and 'supabase' in DB_URL:
        SQLALCHEMY_DATABASE_URI = DB_URL
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 1800,
            'pool_pre_ping': True
        }
    else:
        # SQLite local (fallback)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'harmony.db')



class TestingConfig(Config):
    """Configuration pour les tests (reste en local)"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'academique_test.db')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configuration pour la production (Render)"""
    DEBUG = False

    # Priorité: SUPABASE_DB_URL > DATABASE_URL
    DB_URL = os.environ.get('SUPABASE_DB_URL') or os.environ.get('DATABASE_URL')

    # Fix pour Supabase
    if DB_URL and DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = DB_URL or 'sqlite:///' + os.path.join(basedir, 'instance', 'prod.db')

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10
        }
    }


# Dictionnaire de configuration
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}