"""
Service IA Avancé avec Google Gemini
Vraie IA conversationnelle pour le laboratoire
"""

import json
import os
from datetime import datetime

# Import conditionnel de google.generativeai
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

from app.models import SessionTP, MesureSimulation, InteractionIA, TP
from app import db

# Configuration Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # À mettre dans .env
if GEMINI_API_KEY and GENAI_AVAILABLE and genai:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[IA Avancée] Erreur configuration Gemini: {e}")
        GEMINI_API_KEY = None


class AssistantIAAvance:
    """Assistant IA utilisant Google Gemini"""

    def __init__(self, nom, domaine, couleur):
        self.nom = nom
        self.domaine = domaine
        self.couleur = couleur
        self.model = None
        if GEMINI_API_KEY and GENAI_AVAILABLE and genai:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
            except Exception:
                self.model = None
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self):
        return f"""
Tu es {self.nom}, un assistant IA pédagogique expert en {self.domaine}.

🎯 TES MISSIONS :
1. Guider l'étudiant dans ses expérimentations (SANS faire le travail à sa place)
2. Poser des questions socratiques pour stimuler la réflexion
3. Expliquer les concepts physiques/mathématiques avec clarté
4. Donner des indices progressifs (jamais la réponse directe)
5. Encourager l'expérimentation et la découverte

❌ INTERDICTIONS ABSOLUES :
- NE JAMAIS rédiger la conclusion du rapport
- NE JAMAIS donner les réponses toutes faites
- NE JAMAIS faire les calculs à la place de l'étudiant
- NE JAMAIS valider un résultat sans que l'étudiant comprenne

✅ APPROCHE PÉDAGOGIQUE :
- Utilise la méthode socratique (questions guidées)
- Donne des analogies pour faciliter la compréhension
- Décompose les problèmes complexes en étapes simples
- Encourage les erreurs comme opportunités d'apprentissage

📊 CONTEXTE TECHNIQUE :
Tu as accès aux paramètres de simulation en temps réel.
Utilise ces données pour contextualiser tes réponses.

EXEMPLE DE BON DIALOGUE :
Étudiant : "Pourquoi ma tension de sortie est différente de la théorie ?"
Toi : "Excellente observation ! Regarde ton graphique : vois-tu de l'ondulation ? 
      Quelle composante du circuit pourrait causer cela ? 💡"

EXEMPLE DE MAUVAIS DIALOGUE (À ÉVITER) :
Étudiant : "Donne-moi la conclusion"
Toi : "Voici la conclusion : Le convertisseur Buck..." ❌ NON !

Bonne réponse :
Toi : "Je ne peux pas faire ton rapport 😊 Mais dis-moi : qu'as-tu observé sur tes courbes ? 
      Y a-t-il un lien entre le duty cycle et la tension de sortie ?"

Reste toujours bienveillant, pédagogique, et encourage l'autonomie ! 🚀
"""

    def generer_reponse(self, question, contexte_simulation, session_tp):
        """
        Génère une réponse intelligente via Gemini

        Returns:
            dict: {
                'reponse': str,
                'pertinence_question': int,
                'aide_apportee': bool
            }
        """

        # Construction du prompt enrichi
        prompt = f"""
{self.system_prompt}

📚 CONTEXTE DU TP :
- Titre : {session_tp.tp.titre}
- Type de simulation : {session_tp.tp.type_simulation}
- Durée écoulée : {self._get_duree_session(session_tp)} minutes
- Nombre de mesures déjà prises : {session_tp.nb_mesures or 0}

📊 PARAMÈTRES ACTUELS DE SIMULATION :
{json.dumps(contexte_simulation, indent=2, ensure_ascii=False)}

💬 HISTORIQUE DES 3 DERNIÈRES INTERACTIONS :
{self._get_historique_recent(session_tp.id)}

❓ QUESTION DE L'ÉTUDIANT :
"{question}"

🎯 TA RÉPONSE (en français, max 200 mots) :
"""

        try:
            if self.model:
                # Utiliser Gemini
                response = self.model.generate_content(prompt)
                reponse_texte = response.text

                # Analyse de la pertinence (simple heuristique)
                pertinence = self._analyser_pertinence(question, reponse_texte)
                aide = not any(mot in question.lower() for mot in ['conclusion', 'fais', 'écris'])

            else:
                # Fallback si pas de clé API
                reponse_texte = self._reponse_fallback(question, contexte_simulation)
                pertinence = 3
                aide = True

            return {
                'reponse': reponse_texte,
                'pertinence_question': pertinence,
                'aide_apportee': aide
            }

        except Exception as e:
            print(f"Erreur Gemini : {e}")
            # Fallback en cas d'erreur
            return {
                'reponse': self._reponse_fallback(question, contexte_simulation),
                'pertinence_question': 3,
                'aide_apportee': True
            }

    def _get_duree_session(self, session_tp):
        """Calcule la durée de la session en minutes"""
        if session_tp.date_debut:
            duree = (datetime.utcnow() - session_tp.date_debut).total_seconds() / 60
            return int(duree)
        return 0

    def _get_historique_recent(self, session_id):
        """Récupère les 3 dernières interactions"""
        interactions = InteractionIA.query.filter_by(
            session_id=session_id
        ).order_by(InteractionIA.timestamp.desc()).limit(3).all()

        if not interactions:
            return "Aucune interaction précédente"

        historique = []
        for i in reversed(interactions):
            historique.append(f"Q: {i.question_etudiant}\nR: {i.reponse_ia[:100]}...")

        return "\n\n".join(historique)

    def _analyser_pertinence(self, question, reponse):
        """Analyse la pertinence de la question (1-5)"""
        # Heuristique simple
        if any(mot in question.lower() for mot in ['pourquoi', 'comment', 'expliquer']):
            return 5
        elif any(mot in question.lower() for mot in ['aide', 'comprends pas']):
            return 4
        elif any(mot in question.lower() for mot in ['résultat', 'normal']):
            return 3
        else:
            return 3

    def _reponse_fallback(self, question, contexte):
        """Réponse de secours si Gemini indisponible"""
        return f"""
🤖 Je suis {self.nom}, ton assistant en {self.domaine}.

Je vois que tu travailles sur la simulation. Pour mieux t'aider, 
peux-tu préciser ta question ? Par exemple :
- Que observes-tu sur ton graphique ?
- Quel paramètre te pose problème ?
- Quelle formule aimerais-tu comprendre ?

💡 Astuce : N'hésite pas à faire varier les paramètres pour voir leur impact !
"""

    def evaluer_session(self, session_tp):
        """
        Évalue la session avec analyse IA avancée
        """
        mesures = MesureSimulation.query.filter_by(session_id=session_tp.id).all()
        interactions = InteractionIA.query.filter_by(session_id=session_tp.id).all()

        criteres = {
            'nombre_mesures': 0,
            'variation_parametres': 0,
            'temps_investissement': 0,
            'qualite_questions': 0,
            'autonomie': 0
        }

        # 1. Nombre de mesures
        nb_mesures = len(mesures)
        if nb_mesures >= 20:
            criteres['nombre_mesures'] = 4
        elif nb_mesures >= 10:
            criteres['nombre_mesures'] = 3
        elif nb_mesures >= 5:
            criteres['nombre_mesures'] = 2
        else:
            criteres['nombre_mesures'] = 1

        # 2. Variation des paramètres
        parametres_uniques = set()
        for mesure in mesures:
            if mesure.parametres:
                parametres_uniques.add(mesure.parametres)

        if len(parametres_uniques) >= 10:
            criteres['variation_parametres'] = 4
        elif len(parametres_uniques) >= 5:
            criteres['variation_parametres'] = 3
        else:
            criteres['variation_parametres'] = 2

        # 3. Temps d'investissement
        if session_tp.duree_minutes:
            if session_tp.duree_minutes >= 60:
                criteres['temps_investissement'] = 4
            elif session_tp.duree_minutes >= 30:
                criteres['temps_investissement'] = 3
            else:
                criteres['temps_investissement'] = 2

        # 4. Qualité des questions posées à l'IA
        questions_pertinentes = sum(
            1 for i in interactions
            if i.pertinence_question and i.pertinence_question >= 4
        )

        if questions_pertinentes >= 5:
            criteres['qualite_questions'] = 4
        elif questions_pertinentes >= 3:
            criteres['qualite_questions'] = 3
        else:
            criteres['qualite_questions'] = 2

        # 5. Autonomie
        if len(interactions) <= 5:
            criteres['autonomie'] = 4
        elif len(interactions) <= 10:
            criteres['autonomie'] = 3
        else:
            criteres['autonomie'] = 2

        # Calcul de la note finale
        note = sum(criteres.values()) / len(criteres) * 5  # Sur 20

        # Génération du commentaire via IA
        if self.model and GEMINI_API_KEY:
            try:
                commentaire = self._generer_commentaire_ia(session_tp, criteres, note)
            except:
                commentaire = self._commentaire_fallback(session_tp, criteres, note)
        else:
            commentaire = self._commentaire_fallback(session_tp, criteres, note)

        return {
            'note': round(note, 2),
            'commentaire': commentaire,
            'criteres': criteres
        }

    def _generer_commentaire_ia(self, session_tp, criteres, note):
        """Génère un commentaire personnalisé via IA"""
        prompt = f"""
Tu es {self.nom}, évaluant une session de TP.

📊 DONNÉES DE LA SESSION :
- Durée : {session_tp.duree_minutes} minutes
- Mesures effectuées : {session_tp.nb_mesures}
- Critères détaillés : {json.dumps(criteres, indent=2)}
- Note calculée : {note}/20

🎯 RÉDIGE UN COMMENTAIRE PÉDAGOGIQUE (150 mots max) :
- Sois encourageant et constructif
- Souligne les points forts
- Donne des axes d'amélioration concrets
- Termine par une phrase motivante

Format : utilise des emojis et des sections claires.
"""

        response = self.model.generate_content(prompt)
        return response.text

    def _commentaire_fallback(self, session_tp, criteres, note):
        """Commentaire de secours"""
        return f"""
✅ **Évaluation automatique par {self.nom}**

📊 **Résumé de ta session :**
- Mesures effectuées : {session_tp.nb_mesures} ({criteres['nombre_mesures']}/4)
- Exploration : {criteres['variation_parametres']}/4
- Temps investi : {session_tp.duree_minutes or 0} min ({criteres['temps_investissement']}/4)
- Qualité des questions : {criteres['qualite_questions']}/4
- Autonomie : {criteres['autonomie']}/4

🎯 **Note automatique : {note:.1f}/20**

💡 Cette note sera ajustée par ton enseignant après lecture de ton rapport complet.

{'🌟 Excellent travail !' if note >= 15 else '👍 Bon effort, continue comme ça !' if note >= 12 else '💪 Tu progresses, persévère !'}
"""

    def enregistrer_interaction(self, session_id, question, reponse, contexte):
        """Enregistre l'interaction dans la BDD"""
        interaction = InteractionIA(
            session_id=session_id,
            question_etudiant=question,
            reponse_ia=reponse['reponse'],
            contexte_simulation=json.dumps(contexte),
            ia_nom=self.nom,
            pertinence_question=reponse.get('pertinence_question', 3),
            aide_apportee=reponse.get('aide_apportee', True)
        )
        db.session.add(interaction)
        db.session.commit()


# ============================================================
# ASSISTANTS SPÉCIALISÉS AVEC IA RÉELLE
# ============================================================

class ETAAvance(AssistantIAAvance):
    """Assistant IA avancé pour le Génie Civil"""

    def __init__(self):
        super().__init__(
            nom="ETA",
            domaine="Génie Civil (RDM, Structures, Matériaux, BTP)",
            couleur="#e74c3c"
        )


class ALPHAAvance(AssistantIAAvance):
    """Assistant IA avancé pour Maths, Info, Logistique"""

    def __init__(self):
        super().__init__(
            nom="ALPHA",
            domaine="Mathématiques, Informatique, Logistique, Transport, Optimisation",
            couleur="#2ecc71"
        )


class KAYTAvance(AssistantIAAvance):
    """Assistant IA avancé pour le Génie Électrique"""

    def __init__(self):
        super().__init__(
            nom="KAYT",
            domaine="Génie Électrique (Électronique, Électrotechnique, Automatique)",
            couleur="#f1c40f"
        )


# Factory Pattern
class IAFactoryAvancee:
    """Factory pour créer les assistants IA avancés"""

    @staticmethod
    def creer_assistant(nom_ia):
        if nom_ia == 'ETA':
            return ETAAvance()
        elif nom_ia == 'ALPHA':
            return ALPHAAvance()
        elif nom_ia == 'KAYT':
            return KAYTAvance()
        else:
            raise ValueError(f"IA inconnue : {nom_ia}")