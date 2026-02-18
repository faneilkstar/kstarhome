import os

try:
    from google import genai
    GEMINI_DISPONIBLE = True
except ImportError:
    GEMINI_DISPONIBLE = False

# Configuration de l'IA avec la clé API depuis les variables d'environnement
api_key = os.environ.get("GEMINI_API_KEY")
client = None

if api_key and GEMINI_DISPONIBLE:
    try:
        client = genai.Client(api_key=api_key)
        print("✅ [GEMINI] API configurée avec succès")
    except Exception as e:
        print(f"⚠️ [GEMINI] Erreur configuration: {e}")
else:
    print("⚠️ [GEMINI] Aucune clé API trouvée (variable GEMINI_API_KEY non définie)")

def interroger_ia(prompt, contexte="Tu es un assistant pédagogique utile et bienveillant pour une université."):
    """
    Fonction pour envoyer une question à Gemini et recevoir la réponse.

    Args:
        prompt (str): La question de l'utilisateur
        contexte (str): Le rôle/contexte de l'IA

    Returns:
        str: La réponse de l'IA ou un message d'erreur
    """
    if not client:
        return "❌ L'IA est désactivée (Aucune clé API configurée). Veuillez configurer GEMINI_API_KEY."

    try:
        # Utilisation du modèle Gemini 2.0 Flash
        # Construction du prompt complet avec le contexte
        full_prompt = f"{contexte}\n\nQuestion de l'utilisateur : {prompt}"

        # Génération de la réponse
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=full_prompt
        )

        return response.text

    except Exception as e:
        error_msg = str(e)
        print(f"❌ [GEMINI] Erreur : {error_msg}")
        return f"❌ Erreur de l'IA : {error_msg}"


def valider_reponse_etudiant(question, reponse_etudiant, reponse_attendue=None):
    """
    Valide la réponse d'un étudiant avec l'aide de l'IA.

    Args:
        question (str): La question posée
        reponse_etudiant (str): La réponse de l'étudiant
        reponse_attendue (str, optional): La réponse attendue/correcte

    Returns:
        dict: {
            'valide': bool,
            'note': float (0-20),
            'commentaire': str,
            'suggestions': str
        }
    """
    if not client:
        return {
            'valide': False,
            'note': 0,
            'commentaire': 'IA non disponible',
            'suggestions': 'Configurez GEMINI_API_KEY'
        }

    try:
        # Construction du prompt de validation
        if reponse_attendue:
            prompt = f"""Tu es un correcteur académique bienveillant.

Question : {question}

Réponse de l'étudiant : {reponse_etudiant}

Réponse attendue : {reponse_attendue}

Évalue la réponse de l'étudiant et réponds UNIQUEMENT au format JSON suivant (sans markdown) :
{{
    "valide": true/false,
    "note": 0-20,
    "commentaire": "commentaire constructif",
    "suggestions": "conseils pour améliorer"
}}"""
        else:
            prompt = f"""Tu es un correcteur académique bienveillant.

Question : {question}

Réponse de l'étudiant : {reponse_etudiant}

Évalue la pertinence et la qualité de cette réponse et réponds UNIQUEMENT au format JSON suivant (sans markdown) :
{{
    "valide": true/false,
    "note": 0-20,
    "commentaire": "commentaire constructif",
    "suggestions": "conseils pour améliorer"
}}"""

        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )

        # Parse la réponse JSON
        import json
        response_text = response.text.strip()

        # Nettoyer les balises markdown si présentes
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])

        result = json.loads(response_text)
        return result

    except Exception as e:
        print(f"❌ [GEMINI] Erreur validation : {str(e)}")
        return {
            'valide': False,
            'note': 0,
            'commentaire': f'Erreur de validation : {str(e)}',
            'suggestions': 'Réessayez plus tard'
        }


def generer_exercice(matiere, niveau, type_exercice="QCM"):
    """
    Génère un exercice pédagogique avec l'IA.

    Args:
        matiere (str): La matière (ex: Mathématiques, Physique)
        niveau (str): Le niveau (ex: L1, L2, M1)
        type_exercice (str): Type d'exercice (QCM, Problème, Question ouverte)

    Returns:
        dict: {
            'enonce': str,
            'questions': list,
            'reponses': list (si applicable),
            'correction': str
        }
    """
    if not client:
        return {
            'enonce': 'IA non disponible',
            'questions': [],
            'reponses': [],
            'correction': 'Configurez GEMINI_API_KEY'
        }

    try:
        prompt = f"""Tu es un professeur de {matiere} pour le niveau {niveau}.

Génère un exercice de type "{type_exercice}" et réponds au format JSON suivant (sans markdown) :

{{
    "enonce": "énoncé de l'exercice",
    "questions": ["question 1", "question 2", ...],
    "reponses": ["réponse correcte 1", "réponse correcte 2", ...],
    "correction": "explication détaillée de la correction"
}}

L'exercice doit être pédagogique, clair et adapté au niveau universitaire."""

        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )

        import json
        response_text = response.text.strip()

        # Nettoyer les balises markdown
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])

        result = json.loads(response_text)
        return result

    except Exception as e:
        print(f"❌ [GEMINI] Erreur génération : {str(e)}")
        return {
            'enonce': f'Erreur : {str(e)}',
            'questions': [],
            'reponses': [],
            'correction': ''
        }

