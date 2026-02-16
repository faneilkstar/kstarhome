"""
Point d'entrée pour Vercel Serverless Functions
"""
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app

# Créer l'application Flask
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Vercel cherche cette variable
application = app

# Pour les requêtes serverless
def handler(request):
    return app(request.environ, request.start_response)

