from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.ai_manager import interroger_ia, valider_reponse_etudiant, generer_exercice

bp = Blueprint('api_ia', __name__, url_prefix='/api/ia')

@bp.route('/test', methods=['GET'])
@login_required
def test_page():
    """
    Page de test pour l'IA Gemini.
    Accessible à tous les utilisateurs connectés.
    """
    return render_template('test_ia.html')

@bp.route('/chat', methods=['POST'])
@login_required
def chat_ia():
    """
    Route pour discuter avec l'IA Gemini.

    POST /api/ia/chat
    Body: {
        "question": "Explique-moi la photosynthèse",
        "role": "Tu es un professeur de biologie" (optionnel)
    }

    Returns: {
        "reponse": "La réponse de l'IA",
        "succes": true
    }
    """
    try:
        data = request.json
        question = data.get('question')
        role = data.get('role', 'Tu es un assistant pédagogique universitaire bienveillant.')

        if not question:
            return jsonify({
                'error': 'Aucune question fournie',
                'succes': False
            }), 400

        # Appel à l'IA
        reponse = interroger_ia(question, contexte=role)

        return jsonify({
            'reponse': reponse,
            'succes': True
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'succes': False
        }), 500


@bp.route('/valider', methods=['POST'])
@login_required
def valider_reponse():
    """
    Route pour valider une réponse d'étudiant avec l'IA.

    POST /api/ia/valider
    Body: {
        "question": "Qu'est-ce que la photosynthèse ?",
        "reponse_etudiant": "C'est le processus...",
        "reponse_attendue": "La photosynthèse est..." (optionnel)
    }

    Returns: {
        "valide": true/false,
        "note": 15.5,
        "commentaire": "Bonne réponse mais...",
        "suggestions": "Pour améliorer...",
        "succes": true
    }
    """
    try:
        data = request.json
        question = data.get('question')
        reponse_etudiant = data.get('reponse_etudiant')
        reponse_attendue = data.get('reponse_attendue')

        if not question or not reponse_etudiant:
            return jsonify({
                'error': 'Question et réponse requises',
                'succes': False
            }), 400

        # Validation par l'IA
        resultat = valider_reponse_etudiant(question, reponse_etudiant, reponse_attendue)
        resultat['succes'] = True

        return jsonify(resultat)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'succes': False
        }), 500


@bp.route('/generer-exercice', methods=['POST'])
@login_required
def generer_exercice_route():
    """
    Route pour générer un exercice avec l'IA.
    Réservé aux enseignants et directeurs.

    POST /api/ia/generer-exercice
    Body: {
        "matiere": "Mathématiques",
        "niveau": "L1",
        "type": "QCM"
    }

    Returns: {
        "enonce": "...",
        "questions": [...],
        "reponses": [...],
        "correction": "...",
        "succes": true
    }
    """
    # Vérifier que l'utilisateur est enseignant ou directeur
    if current_user.role not in ['ENSEIGNANT', 'DIRECTEUR']:
        return jsonify({
            'error': 'Accès réservé aux enseignants et directeurs',
            'succes': False
        }), 403

    try:
        data = request.json
        matiere = data.get('matiere', 'Mathématiques')
        niveau = data.get('niveau', 'L1')
        type_exercice = data.get('type', 'QCM')

        # Génération de l'exercice
        exercice = generer_exercice(matiere, niveau, type_exercice)
        exercice['succes'] = True

        return jsonify(exercice)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'succes': False
        }), 500


@bp.route('/status', methods=['GET'])
def status():
    """
    Route pour vérifier si l'IA est disponible.

    GET /api/ia/status

    Returns: {
        "disponible": true/false,
        "modele": "gemini-pro",
        "message": "..."
    }
    """
    import os
    api_key = os.environ.get("GEMINI_API_KEY")

    return jsonify({
        'disponible': bool(api_key),
        'modele': 'gemini-pro' if api_key else None,
        'message': 'IA Gemini opérationnelle' if api_key else 'IA non configurée (GEMINI_API_KEY manquante)'
    })

