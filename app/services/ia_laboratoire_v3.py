"""
IA Laboratoire V3 - Version Ultra-Avancée avec Gemini
Système d'assistance intelligent pour le laboratoire virtuel
Avec fallback robuste multi-niveaux
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configuration Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_ENABLED = bool(GEMINI_API_KEY)
GEMINI_CLIENT = None  # Alias utilisé dans la classe

# Tentative de chargement de Gemini
try:
    import google.generativeai as genai
    if GEMINI_ENABLED:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')
        GEMINI_CLIENT = GEMINI_MODEL  # Alias
        print("✅ [IA V3] Gemini Pro initialisé")
    else:
        GEMINI_MODEL = None
        print("⚠️ [IA V3] Gemini désactivé (pas de clé API)")
except Exception as e:
    GEMINI_MODEL = None
    print(f"⚠️ [IA V3] Gemini non disponible: {e}")


class IALaboratoireV3:
    """Assistant IA pour le laboratoire - Version 3 avec Gemini"""

    def __init__(self, nom='ETA-V3', specialite='Pédagogie'):
        self.nom = nom
        self.specialite = specialite
        self.version = '3.0'
        self.gemini_actif = GEMINI_CLIENT is not None

    def analyser_session(self, session_data: Dict) -> Dict:
        """Analyse complète d'une session de TP"""

        # Extraire les données
        mesures = session_data.get('mesures', [])
        interactions = session_data.get('interactions', [])
        type_simulation = session_data.get('type_simulation', 'buck')

        # Analyse multi-dimensionnelle
        analyse = {
            'qualite_mesures': self._evaluer_qualite_mesures(mesures, type_simulation),
            'progression': self._analyser_progression(mesures, interactions),
            'engagement': self._evaluer_engagement(interactions),
            'comprehension': self._evaluer_comprehension(interactions, mesures),
            'autonomie': self._evaluer_autonomie(interactions),
            'note_suggeree': 0,
            'points_forts': [],
            'points_amelioration': [],
            'recommandations': []
        }

        # Calculer note globale
        analyse['note_suggeree'] = self._calculer_note_globale(analyse)

        # Générer feedback personnalisé
        analyse['feedback'] = self._generer_feedback(analyse, type_simulation)

        return analyse

    def _evaluer_qualite_mesures(self, mesures: List, type_sim: str) -> Dict:
        """Évalue la qualité et la pertinence des mesures"""

        if not mesures:
            return {
                'score': 0,
                'nb_mesures': 0,
                'pertinence': 0,
                'precision': 0,
                'commentaire': "Aucune mesure effectuée"
            }

        nb_mesures = len(mesures)

        # Analyser la diversité des paramètres testés
        parametres_testes = set()
        for m in mesures:
            params = m.get('parametres', {})
            parametres_testes.update(params.keys())

        diversite = len(parametres_testes)

        # Évaluer la progression des tests
        progression_logique = self._verifier_progression_logique(mesures)

        # Score global
        score = min(100, (nb_mesures * 5) + (diversite * 10) + (progression_logique * 20))

        return {
            'score': score,
            'nb_mesures': nb_mesures,
            'diversite_parametres': diversite,
            'progression_logique': progression_logique,
            'pertinence': min(100, diversite * 25),
            'commentaire': self._generer_commentaire_mesures(nb_mesures, diversite, progression_logique)
        }

    def _verifier_progression_logique(self, mesures: List) -> int:
        """Vérifie si l'étudiant a suivi une démarche logique"""

        if len(mesures) < 2:
            return 50

        # Vérifier que l'étudiant ne change pas tout d'un coup
        changements_progressifs = 0
        changements_totaux = len(mesures) - 1

        for i in range(len(mesures) - 1):
            params_avant = mesures[i].get('parametres', {})
            params_apres = mesures[i + 1].get('parametres', {})

            # Compter combien de paramètres ont changé
            changements = sum(1 for k in params_avant if params_avant.get(k) != params_apres.get(k))

            if changements <= 2:  # Maximum 2 paramètres changés à la fois
                changements_progressifs += 1

        if changements_totaux > 0:
            progression = int((changements_progressifs / changements_totaux) * 100)
        else:
            progression = 50

        return progression

    def _analyser_progression(self, mesures: List, interactions: List) -> Dict:
        """Analyse la progression de l'étudiant durant le TP"""

        if not mesures and not interactions:
            return {'score': 0, 'tendance': 'aucune'}

        # Analyser l'évolution temporelle
        if len(mesures) >= 3:
            # Les dernières mesures sont-elles meilleures ?
            dernieres = mesures[-3:]
            premieres = mesures[:3] if len(mesures) > 3 else mesures

            # Comparer la qualité (ex: proximité des objectifs)
            tendance = 'amelioration' if len(dernieres) > len(premieres) else 'stable'
        else:
            tendance = 'debutant'

        return {
            'score': min(100, len(mesures) * 10),
            'tendance': tendance,
            'nb_etapes': len(mesures)
        }

    def _evaluer_engagement(self, interactions: List) -> Dict:
        """Évalue l'engagement de l'étudiant"""

        nb_interactions = len(interactions)

        if nb_interactions == 0:
            niveau = 'faible'
            score = 20
        elif nb_interactions < 5:
            niveau = 'moyen'
            score = 50
        elif nb_interactions < 10:
            niveau = 'bon'
            score = 75
        else:
            niveau = 'excellent'
            score = 95

        return {
            'score': score,
            'niveau': niveau,
            'nb_interactions': nb_interactions
        }

    def _evaluer_comprehension(self, interactions: List, mesures: List) -> Dict:
        """Évalue le niveau de compréhension de l'étudiant"""

        # Analyser la pertinence des questions
        questions_pertinentes = 0
        questions_repetitives = 0

        mots_cles_pertinents = [
            'pourquoi', 'comment', 'influence', 'effet', 'optimal',
            'relation', 'calcul', 'formule', 'théorie', 'principe'
        ]

        for inter in interactions:
            message = inter.get('message_etudiant', '').lower()

            if any(mot in message for mot in mots_cles_pertinents):
                questions_pertinentes += 1

            # Détecter les répétitions
            if len([i for i in interactions if i.get('message_etudiant') == inter.get('message_etudiant')]) > 1:
                questions_repetitives += 1

        if len(interactions) > 0:
            score = int((questions_pertinentes / len(interactions)) * 100)
        else:
            score = 50

        # Bonus si beaucoup de mesures (expérimentation)
        if len(mesures) >= 5:
            score = min(100, score + 20)

        return {
            'score': score,
            'questions_pertinentes': questions_pertinentes,
            'questions_repetitives': questions_repetitives
        }

    def _evaluer_autonomie(self, interactions: List) -> Dict:
        """Évalue le niveau d'autonomie de l'étudiant"""

        nb_interactions = len(interactions)

        # Plus l'étudiant pose de questions, moins il est autonome
        # Mais il faut un équilibre
        if nb_interactions == 0:
            score = 80  # Autonome mais peut-être trop
            niveau = 'très autonome'
        elif nb_interactions < 5:
            score = 90
            niveau = 'autonome'
        elif nb_interactions < 10:
            score = 70
            niveau = 'moyennement autonome'
        else:
            score = 50
            niveau = 'peu autonome'

        return {
            'score': score,
            'niveau': niveau
        }

    def _calculer_note_globale(self, analyse: Dict) -> float:
        """Calcule la note finale sur 20"""

        # Pondération des critères
        poids = {
            'qualite_mesures': 0.40,
            'progression': 0.20,
            'engagement': 0.15,
            'comprehension': 0.15,
            'autonomie': 0.10
        }

        note = 0
        for critere, poids_critere in poids.items():
            if critere in analyse:
                score = analyse[critere].get('score', 0)
                note += (score / 100) * 20 * poids_critere

        return round(note, 2)

    def _generer_commentaire_mesures(self, nb_mesures: int, diversite: int, progression: int) -> str:
        """Génère un commentaire sur la qualité des mesures"""

        commentaires = []

        if nb_mesures < 3:
            commentaires.append("⚠️ Nombre de mesures insuffisant")
        elif nb_mesures < 5:
            commentaires.append("✓ Nombre de mesures acceptable")
        else:
            commentaires.append("✅ Bon nombre de mesures effectuées")

        if diversite < 2:
            commentaires.append("⚠️ Peu de paramètres testés")
        elif diversite < 4:
            commentaires.append("✓ Diversité acceptable des tests")
        else:
            commentaires.append("✅ Excellente diversité d'expérimentation")

        if progression < 50:
            commentaires.append("⚠️ Démarche peu méthodique")
        elif progression < 75:
            commentaires.append("✓ Démarche assez méthodique")
        else:
            commentaires.append("✅ Démarche très méthodique")

        return " | ".join(commentaires)

    def _generer_feedback(self, analyse: Dict, type_simulation: str) -> str:
        """Génère un feedback personnalisé"""

        feedback_parts = []

        # Feedback global
        note = analyse['note_suggeree']
        if note >= 16:
            feedback_parts.append("🌟 Excellent travail ! Vous maîtrisez très bien les concepts.")
        elif note >= 12:
            feedback_parts.append("👍 Bon travail ! Vous avez bien compris les concepts principaux.")
        elif note >= 10:
            feedback_parts.append("📚 Travail satisfaisant. Quelques points à approfondir.")
        else:
            feedback_parts.append("💪 Continuez vos efforts. Plusieurs concepts restent à maîtriser.")

        # Points forts
        points_forts = []
        if analyse['qualite_mesures']['score'] >= 70:
            points_forts.append("mesures de qualité")
        if analyse['engagement']['score'] >= 70:
            points_forts.append("bon engagement")
        if analyse['comprehension']['score'] >= 70:
            points_forts.append("bonne compréhension")

        if points_forts:
            feedback_parts.append(f"\n\n✨ Points forts : {', '.join(points_forts)}")

        # Points à améliorer
        points_amelioration = []
        if analyse['qualite_mesures']['score'] < 50:
            points_amelioration.append("augmenter le nombre et la diversité des mesures")
        if analyse['comprehension']['score'] < 50:
            points_amelioration.append("approfondir les concepts théoriques")
        if analyse['engagement']['score'] < 50:
            points_amelioration.append("interagir davantage avec l'assistant IA")

        if points_amelioration:
            feedback_parts.append(f"\n\n📈 Axes d'amélioration : {', '.join(points_amelioration)}")

        return "\n".join(feedback_parts)

    def repondre_question(self, question: str, contexte: Dict) -> str:
        """Répond à une question de l'étudiant"""

        # Essayer d'abord avec Gemini
        if self.gemini_actif:
            try:
                reponse = self._repondre_avec_gemini(question, contexte)
                if reponse:
                    return reponse
            except Exception as e:
                print(f"⚠️ [IA V3] Gemini error: {e}")

        # Fallback sur réponses intelligentes prédéfinies
        return self._repondre_fallback(question, contexte)

    def _repondre_avec_gemini(self, question: str, contexte: Dict) -> Optional[str]:
        """Utilise Gemini pour répondre"""

        if not GEMINI_CLIENT:
            return None

        # Construire le prompt
        type_sim = contexte.get('type_simulation', 'buck')
        parametres = contexte.get('parametres', {})
        mesure_actuelle = contexte.get('mesure_actuelle', {})

        prompt = f"""Tu es {self.nom}, un assistant pédagogique expert en {self.specialite}.
L'étudiant travaille sur une simulation de type: {type_sim}

Paramètres actuels: {json.dumps(parametres, indent=2)}
Dernière mesure: {json.dumps(mesure_actuelle, indent=2)}

Question de l'étudiant: "{question}"

Réponds de manière pédagogique et concise (max 150 mots), en français.
Aide l'étudiant à comprendre sans donner directement la réponse complète.
"""

        try:
            response = GEMINI_CLIENT.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"⚠️ [IA V3] Gemini generation error: {e}")
            return None

    def _repondre_fallback(self, question: str, contexte: Dict) -> str:
        """Réponses de secours intelligentes"""

        question_lower = question.lower()
        type_sim = contexte.get('type_simulation', 'buck')

        # Base de connaissances par type de simulation
        reponses = self._get_base_connaissances(type_sim)

        # Recherche de mots-clés
        for mots_cles, reponse in reponses.items():
            if any(mot in question_lower for mot in mots_cles.split('|')):
                return reponse

        # Réponse générique
        return f"""Je suis {self.nom}, votre assistant pédagogique. 
        
Votre question concerne la simulation "{type_sim}". Pourriez-vous préciser votre demande ? 

Quelques suggestions:
• Modifiez les paramètres un par un pour observer leur effet
• Comparez vos résultats avec la théorie
• N'hésitez pas à faire plusieurs mesures

💡 Astuce: Une bonne démarche expérimentale consiste à varier un seul paramètre à la fois."""

    def _get_base_connaissances(self, type_sim: str) -> Dict[str, str]:
        """Retourne la base de connaissances pour un type de simulation"""

        bases = {
            'buck': {
                'tension|voltage|sortie': """Un convertisseur Buck abaisse la tension. La tension de sortie dépend du rapport cyclique α :
Vs = α × Ve
où α est le rapport cyclique (duty cycle) entre 0 et 1.
Essayez de varier α pour observer l'effet sur Vs.""",

                'rapport|cyclique|duty|alpha': """Le rapport cyclique (α ou duty cycle) contrôle la fraction de temps où le transistor est passant.
• α = 0.5 → Vs = 0.5 × Ve
• α proche de 1 → Vs proche de Ve
• α proche de 0 → Vs proche de 0""",

                'ondulation|ripple': """L'ondulation (ripple) dépend de:
• La valeur de l'inductance L (plus L est grand, moins d'ondulation)
• La valeur de la capacité C (plus C est grand, moins d'ondulation)
• La fréquence de commutation f (plus f est grande, moins d'ondulation)""",

                'inductance|bobine': """L'inductance L lisse le courant et réduit l'ondulation.
Une valeur typique est entre 100µH et 1mH.
Trop faible → forte ondulation
Trop élevée → encombrement et coût""",

                'rendement|efficacité': """Le rendement η d'un convertisseur Buck est généralement bon (>80%).
Il dépend des pertes dans:
• Le transistor (résistance à l'état passant)
• La diode (chute de tension)
• L'inductance (résistance série)"""
            },

            'signal_fourier': {
                'fourier|fréquence|harmonique': """La transformée de Fourier décompose un signal en somme de sinusoïdes.
Un signal périodique contient:
• Une fréquence fondamentale f0
• Des harmoniques: 2f0, 3f0, 4f0, etc.
L'amplitude de chaque harmonique donne le spectre.""",

                'échantillonnage|shannon': """Le théorème de Shannon stipule :
Fréquence d'échantillonnage Fe ≥ 2 × Fmax
où Fmax est la fréquence maximale du signal.
Sinon: repliement spectral (aliasing).""",

                'filtre|filtrage': """Un filtre modifie le contenu fréquentiel:
• Passe-bas: laisse passer les basses fréquences
• Passe-haut: laisse passer les hautes fréquences
• Passe-bande: laisse passer une plage de fréquences"""
            },

            'thermodynamique': {
                'chaleur|température|thermique': """La chaleur Q transférée dépend de:
• La différence de température ΔT
• La résistance thermique Rth
• Le coefficient d'échange h
Q = ΔT / Rth""",

                'convection|conduction|rayonnement': """Les 3 modes de transfert thermique:
• Conduction: dans un solide (loi de Fourier)
• Convection: fluide en mouvement
• Rayonnement: ondes électromagnétiques"""
            },

            'chute_libre': {
                'chute|gravité|accélération': """En chute libre, l'accélération est g ≈ 9.81 m/s².
Position: y = y0 - (1/2)gt²
Vitesse: v = v0 - gt
Sans frottement de l'air.""",

                'vitesse|position|temps': """Les équations du mouvement:
• Position: fonction du carré du temps
• Vitesse: fonction linéaire du temps
• Accélération: constante (g)"""
            }
        }

        return bases.get(type_sim, {
            'aide|help': """Je suis là pour vous guider dans votre expérimentation.
N'hésitez pas à:
• Varier les paramètres un par un
• Observer les résultats
• Me poser des questions spécifiques"""
        })


class IAFactoryV3:
    """Factory pour créer des assistants IA spécialisés - V3"""

    @staticmethod
    def creer_assistant(nom: str = 'ETA', type_simulation: str = 'buck') -> IALaboratoireV3:
        """Crée un assistant IA adapté"""

        assistants = {
            'ETA': IALaboratoireV3('ETA-V3', 'Pédagogie et Assistance'),
            'ALPHA': IALaboratoireV3('ALPHA-V3', 'Électronique de Puissance'),
            'KAYT': IALaboratoireV3('KAYT-V3', 'Simulations Numériques'),
            'SIGMA': IALaboratoireV3('SIGMA-V3', 'Traitement du Signal'),
            'THETA': IALaboratoireV3('THETA-V3', 'Thermodynamique')
        }

        return assistants.get(nom, assistants['ETA'])


# Export
__all__ = ['IALaboratoireV3', 'IAFactoryV3']

