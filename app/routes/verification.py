"""
Vérification publique de documents signés
"""

from flask import Blueprint, render_template, request, jsonify

from app.models import SignatureDocument

verification_bp = Blueprint('verification', __name__, url_prefix='/verifier')


@verification_bp.route('/<code_verification>')
def verifier_document(code_verification):
    """Page de vérification d'un document"""

    signature = SignatureDocument.query.filter_by(
        code_verification=code_verification
    ).first()

    if not signature:
        return render_template('verification/invalide.html'), 404

    # Informations sur le document
    document_info = {
        'code': signature.code_verification,
        'type': signature.document_type,
        'date_signature': signature.date_signature,
        'valide': signature.valide
    }

    return render_template('verification/valide.html', info=document_info)


@verification_bp.route('/api/check/<code>')
def api_check(code):
    """API pour vérifier un code"""

    signature = SignatureDocument.query.filter_by(code_verification=code).first()

    if not signature:
        return jsonify({'valid': False, 'message': 'Code invalide'})

    return jsonify({
        'valid': signature.valide,
        'document_type': signature.document_type,
        'date_signature': signature.date_signature.isoformat(),
        'message': 'Document authentique' if signature.valide else 'Document révoqué'
    })



























Installation
JWT: requirements.txt

txt

Flask - JWT - Extended == 4.5
.3
flask - restx == 1.3
.0

bash

pip
install
Flask - JWT - Extended
flask - restx - -
break
-system - packages

Initialisation
JWT: app / __init__.py(ajoute)

python

from flask_jwt_extended import JWTManager

jwt = JWTManager()


def create_app():
    # ... code existant ...

    jwt.init_app(app)

    # Enregistrer les blueprints API
    from app.api.v1 import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app
    from app.utils.cache import cache_result, invalidate_cache


# Dans vos routes
@cache_result(timeout=600, key_prefix='stats')
def get_statistiques_globales():
    """Stats lourdes mises en cache 10 minutes"""
    total_etudiants = Etudiant.query.count()
    total_enseignants = Enseignant.query.count()
    # ... calculs lourds
    return {
        'etudiants': total_etudiants,
        'enseignants': total_enseignants
    }


# Invalider le cache quand les données changent
@app.route('/etudiant/nouveau', methods=['POST'])
def creer_etudiant():
    # ... créer étudiant
    invalidate_cache('stats:*')  # Invalider toutes les stats
    return redirect(...)

