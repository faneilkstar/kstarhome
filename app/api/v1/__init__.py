"""
API REST v1 avec documentation Swagger
"""

from flask import Blueprint
from flask_restx import Api

api_bp = Blueprint('api', __name__)

api = Api(
    api_bp,
    title='Harmony School API',
    version='1.0',
    description='API complète pour la gestion scolaire',
    doc='/docs',  # Swagger UI à /api/v1/docs
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Token au format: Bearer <token>'
        }
    },
    security='Bearer'
)

# Importer les namespaces
from app.api.v1 import auth, etudiants, notes, tps

# Enregistrer les namespaces
api.add_namespace(auth.ns, path='/auth')
api.add_namespace(etudiants.ns, path='/etudiants')
api.add_namespace(notes.ns, path='/notes')
api.add_namespace(tps.ns, path='/laboratoire')