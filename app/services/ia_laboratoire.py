"""
Service IA pour le Laboratoire Virtuel
3 Assistants spécialisés : ETA, ALPHA, KAYT
"""

import json
import random
from datetime import datetime
from app.models import SessionTP, MesureSimulation, InteractionIA, TP
from app import db

class AssistantIA:
    """Classe de base pour les assistants IA"""

    def __init__(self, nom, domaine, couleur):
        self.nom = nom
        self.domaine = domaine
        self.couleur = couleur
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self):
        return f"""
        Tu es {self.nom}, l'assistant IA spécialisé en {self.domaine}.
        Ton rôle : Guider l'étudiant dans ses expérimentations, expliquer les concepts, 
        et l'aider à analyser ses résultats.
        
        RÈGLES ABSOLUES :
        1. Tu NE DOIS JAMAIS faire le travail à la place de l'étudiant
        2. Tu NE DOIS JAMAIS rédiger ses conclusions ou son rapport
        3. Tu dois poser des questions pour stimuler la réflexion
        4. Tu dois valider la compréhension avant de donner la réponse
        5. Tu dois encourager l'expérimentation
        
        Si l'étudiant demande "Fais ma conclusion", réponds :
        "Je suis là pour t'aider à comprendre, pas pour faire ton travail. 
        Que remarques-tu dans tes résultats ?"
        """

    def generer_reponse(self, question, contexte_simulation, session_tp):
        """
        Génère une réponse contextuelle

        Args:
            question (str): Question de l'étudiant
            contexte_simulation (dict): Paramètres actuels de la simulation
            session_tp (SessionTP): Session en cours

        Returns:
            dict: {
                'reponse': str,
                'pertinence_question': int (1-5),
                'aide_apportee': bool
            }
        """
        # Cette méthode sera surchargée par chaque assistant
        pass

    def evaluer_session(self, session_tp):
        """
        Évalue automatiquement une session de TP

        Returns:
            dict: {
                'note': float (sur 20),
                'commentaire': str,
                'criteres': dict
            }
        """
        pass

    def enregistrer_interaction(self, session_id, question, reponse, contexte):
        """Enregistre une interaction dans la BDD"""
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


class ETA(AssistantIA):
    """Assistant IA pour le Génie Civil"""

    def __init__(self):
        super().__init__(
            nom="ETA",
            domaine="Génie Civil (RDM, Structures, Matériaux)",
            couleur="#e74c3c"
        )

    def generer_reponse(self, question, contexte, session_tp):
        q_lower = question.lower()

        # Détection des tentatives de triche
        if any(mot in q_lower for mot in ['conclusion', 'rapport', 'fais', 'écris', 'rédige']):
            return {
                'reponse': "🛑 Je ne peux pas rédiger ton rapport. Mon rôle est de t'aider à **comprendre**. "
                          "Que peux-tu déduire de tes observations ?",
                'pertinence_question': 1,
                'aide_apportee': False
            }

        # Aide RDM - Poutre
        if 'poutre' in q_lower or 'flexion' in q_lower:
            if 'moment' in q_lower:
                return {
                    'reponse': f"📐 Le moment fléchissant maximal se trouve généralement au milieu d'une poutre "
                              f"simplement appuyée avec charge uniformément répartie. "
                              f"Formule : M_max = (q × L²) / 8. "
                              f"Avec tes paramètres actuels, essaie de calculer cette valeur et compare avec ta simulation.",
                    'pertinence_question': 5,
                    'aide_apportee': True
                }

        # Contrainte
        if 'contrainte' in q_lower or 'sigma' in q_lower:
            return {
                'reponse': "La contrainte normale σ = M/I × y, où M est le moment, I l'inertie, et y la distance à la fibre neutre. "
                          "As-tu identifié où se situe la contrainte maximale dans ta poutre ?",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Réponse générique
        return {
            'reponse': f"🏗️ Je suis ETA, ton assistant en Génie Civil. Ta question concerne quoi exactement : "
                      f"la résistance des matériaux, les charges, ou le dimensionnement ?",
            'pertinence_question': 3,
            'aide_apportee': False
        }

    def evaluer_session(self, session_tp):
        """Évalue une session RDM"""
        mesures = MesureSimulation.query.filter_by(session_id=session_tp.id).all()

        criteres = {
            'nombre_mesures': 0,
            'variation_parametres': 0,
            'temps_passe': 0,
            'precision_resultats': 0,
            'autonomie': 0
        }

        # Nombre de mesures
        nb_mesures = len(mesures)
        if nb_mesures >= 20:
            criteres['nombre_mesures'] = 4
        elif nb_mesures >= 10:
            criteres['nombre_mesures'] = 3
        elif nb_mesures >= 5:
            criteres['nombre_mesures'] = 2
        else:
            criteres['nombre_mesures'] = 1

        # Variation des paramètres (a-t-il testé différentes configurations ?)
        parametres_testes = set()
        for mesure in mesures:
            if mesure.parametres:
                params = json.loads(mesure.parametres)
                parametres_testes.add(json.dumps(params, sort_keys=True))

        if len(parametres_testes) >= 5:
            criteres['variation_parametres'] = 4
        elif len(parametres_testes) >= 3:
            criteres['variation_parametres'] = 3
        else:
            criteres['variation_parametres'] = 2

        # Temps passé (en minutes)
        if session_tp.duree_minutes:
            if session_tp.duree_minutes >= 45:
                criteres['temps_passe'] = 4
            elif session_tp.duree_minutes >= 30:
                criteres['temps_passe'] = 3
            else:
                criteres['temps_passe'] = 2

        # Autonomie (moins d'interactions IA = plus autonome)
        nb_interactions = InteractionIA.query.filter_by(session_id=session_tp.id).count()
        if nb_interactions <= 3:
            criteres['autonomie'] = 4
        elif nb_interactions <= 7:
            criteres['autonomie'] = 3
        else:
            criteres['autonomie'] = 2

        # Calcul note finale
        note = sum(criteres.values()) / len(criteres) * 5  # Sur 20

        commentaire = f"""
        ✅ **Évaluation automatique ETA**
        
        - Nombre de mesures : {nb_mesures} ({criteres['nombre_mesures']}/4)
        - Variation paramètres : {len(parametres_testes)} configs ({criteres['variation_parametres']}/4)
        - Temps investi : {session_tp.duree_minutes or 0} min ({criteres['temps_passe']}/4)
        - Autonomie : {4 - nb_interactions//3} interactions ({criteres['autonomie']}/4)
        
        **Note automatique : {note:.1f}/20**
        
        💡 Cette note sera ajustée par ton enseignant après lecture de ton rapport.
        """

        return {
            'note': round(note, 2),
            'commentaire': commentaire,
            'criteres': criteres
        }


class ALPHA(AssistantIA):
    """Assistant IA pour Maths, Info, Logistique, Transport"""

    def __init__(self):
        super().__init__(
            nom="ALPHA",
            domaine="Mathématiques, Informatique, Logistique & Transport",
            couleur="#2ecc71"
        )

    def generer_reponse(self, question, contexte, session_tp):
        q_lower = question.lower()

        # Anti-triche
        if any(mot in q_lower for mot in ['conclusion', 'rapport', 'fais', 'écris']):
            return {
                'reponse': "🚫 Je ne rédige pas de rapports. Analyse tes données et tire tes propres conclusions.",
                'pertinence_question': 1,
                'aide_apportee': False
            }

        # Logistique - Stocks
        if 'stock' in q_lower or 'rupture' in q_lower:
            return {
                'reponse': "📦 Le modèle de Wilson permet d'optimiser la quantité économique de commande (QEC). "
                          "Formule : QEC = √(2 × D × Cc / Cp), où D = demande annuelle, Cc = coût de commande, Cp = coût de possession. "
                          "As-tu identifié le point de rupture dans ta simulation ?",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Transport - Routage
        if 'route' in q_lower or 'chemin' in q_lower or 'dijkstra' in q_lower:
            return {
                'reponse': "🚚 L'algorithme de Dijkstra trouve le plus court chemin. "
                          "As-tu essayé de modifier les poids des arêtes pour voir l'impact sur le trajet optimal ?",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Maths - Fourier
        if 'fourier' in q_lower or 'fft' in q_lower or 'fréquence' in q_lower:
            freq = contexte.get('freq', 5)
            return {
                'reponse': f"📊 La transformée de Fourier décompose ton signal en fréquences. "
                          f"Avec une fréquence de {freq} Hz, tu devrais voir un pic à cette valeur dans le spectre. "
                          f"Le bruit génère des composantes aléatoires. Que remarques-tu ?",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        return {
            'reponse': "🧮 Je suis ALPHA, spécialiste en maths, info et logistique. Précise ta question : "
                      "algorithme, optimisation, ou analyse de signal ?",
            'pertinence_question': 3,
            'aide_apportee': False
        }

    def evaluer_session(self, session_tp):
        # Similar evaluation logic to ETA
        mesures = MesureSimulation.query.filter_by(session_id=session_tp.id).all()
        nb_mesures = len(mesures)

        note = min(20, nb_mesures / 2 + 10)  # Formule simplifiée

        return {
            'note': round(note, 2),
            'commentaire': f"Évaluation ALPHA : {nb_mesures} mesures effectuées.",
            'criteres': {'mesures': nb_mesures}
        }


class KAYT(AssistantIA):
    """Assistant IA pour le Génie Électrique"""

    def __init__(self):
        super().__init__(
            nom="KAYT",
            domaine="Génie Électrique (Électronique, Électrotechnique)",
            couleur="#f1c40f"
        )

    def generer_reponse(self, question, contexte, session_tp):
        q_lower = question.lower()

        # Anti-triche
        if any(mot in q_lower for mot in ['conclusion', 'rapport']):
            return {
                'reponse': "⚡ Je ne fais pas les rapports. Observe tes courbes et déduis par toi-même.",
                'pertinence_question': 1,
                'aide_apportee': False
            }

        # Buck converter
        if 'buck' in q_lower or 'hacheur' in q_lower:
            alpha = contexte.get('alpha', 0.5)
            vin = contexte.get('vin', 24)
            return {
                'reponse': f"⚙️ Dans un Buck, Vout = α × Vin. "
                          f"Avec α={alpha} et Vin={vin}V, tu devrais obtenir théoriquement {alpha * vin:.1f}V. "
                          f"Compare avec ta mesure. L'écart vient du filtre LC. Augmente C pour réduire l'ondulation.",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Ondulation
        if 'ondulation' in q_lower or 'ripple' in q_lower:
            return {
                'reponse': "📉 L'ondulation (ripple) diminue quand tu augmentes C ou L. "
                          "Formule : ΔV ≈ (I_load × T) / (8 × C). Teste différentes valeurs !",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        return {
            'reponse': "⚡ Je suis KAYT, ton expert en génie électrique. "
                      "Question sur le circuit, les tensions, ou le filtrage ?",
            'pertinence_question': 3,
            'aide_apportee': False
        }

    def evaluer_session(self, session_tp):
        mesures = MesureSimulation.query.filter_by(session_id=session_tp.id).all()

        note = min(20, len(mesures) / 1.5 + 8)

        return {
            'note': round(note, 2),
            'commentaire': f"Évaluation KAYT : {len(mesures)} mesures.",
            'criteres': {}
        }


# Factory Pattern
class IAFactory:
    """Factory pour créer le bon assistant IA"""

    @staticmethod
    def creer_assistant(nom_ia):
        if nom_ia == 'ETA':
            return ETA()
        elif nom_ia == 'ALPHA':
            return ALPHA()
        elif nom_ia == 'KAYT':
            return KAYT()
        else:
            raise ValueError(f"IA inconnue : {nom_ia}")