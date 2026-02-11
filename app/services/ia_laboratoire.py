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
        if any(mot in q_lower for mot in ['conclusion', 'rapport', 'fais', 'écris', 'rédige', 'donne la réponse', 'réponds pour moi']):
            return {
                'reponse': "🛑 **Je ne peux pas rédiger ton rapport !**\n\n"
                          "Mon rôle est de t'aider à **comprendre**, pas de faire le travail à ta place. "
                          "Que peux-tu déduire de tes observations ? Quelles tendances remarques-tu ?",
                'pertinence_question': 1,
                'aide_apportee': False
            }

        # Aide RDM - Poutre
        if 'poutre' in q_lower or 'flexion' in q_lower:
            if 'moment' in q_lower:
                L = contexte.get('longueur', 10)
                q_charge = contexte.get('charge', 100)
                return {
                    'reponse': f"📐 **Moment fléchissant dans une poutre**\n\n"
                              f"Le moment fléchissant maximal se trouve généralement au milieu d'une poutre "
                              f"simplement appuyée avec charge uniformément répartie.\n\n"
                              f"**Formule théorique :** M_max = (q × L²) / 8\n\n"
                              f"Avec tes paramètres actuels :\n"
                              f"• Charge : q = {q_charge} N/m\n"
                              f"• Longueur : L = {L} m\n"
                              f"• M_max théorique = ({q_charge} × {L}²) / 8 = **{(q_charge * L**2) / 8:.2f} N·m**\n\n"
                              f"💡 **À faire :**\n"
                              f"1. Compare cette valeur avec ton graphique\n"
                              f"2. Où se situe le moment maximal dans ta simulation ?\n"
                              f"3. Que se passe-t-il si tu doubles la charge ?",
                    'pertinence_question': 5,
                    'aide_apportee': True
                }
            elif 'flèche' in q_lower or 'déformation' in q_lower:
                return {
                    'reponse': "📏 **Flèche maximale d'une poutre**\n\n"
                              "La flèche (déformation verticale) dépend de :\n"
                              "• La charge appliquée (q)\n"
                              "• La longueur de la poutre (L)\n"
                              "• Le module d'Young du matériau (E)\n"
                              "• L'inertie de la section (I)\n\n"
                              "**Formule :** f_max = (5 × q × L⁴) / (384 × E × I)\n\n"
                              "🔬 **Expérience à faire :**\n"
                              "• Change le matériau (E) et observe l'impact\n"
                              "• Augmente L et regarde comment la flèche évolue (attention, c'est à la puissance 4 !)",
                    'pertinence_question': 5,
                    'aide_apportee': True
                }

        # Contrainte
        if 'contrainte' in q_lower or 'sigma' in q_lower:
            return {
                'reponse': "💪 **Contrainte normale (σ) dans une poutre**\n\n"
                          "La contrainte normale est donnée par : **σ = (M × y) / I**\n\n"
                          "Où :\n"
                          "• M = moment fléchissant à la section considérée\n"
                          "• y = distance à la fibre neutre\n"
                          "• I = moment d'inertie de la section\n\n"
                          "📍 **Point important :**\n"
                          "La contrainte maximale se trouve aux fibres extérieures (y_max) "
                          "à l'endroit où le moment est maximal.\n\n"
                          "🎯 **Question pour toi :**\n"
                          "• As-tu identifié où se situe σ_max dans ta poutre ?\n"
                          "• Cette contrainte dépasse-t-elle la limite élastique du matériau ?",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Matériaux
        if 'matériau' in q_lower or 'acier' in q_lower or 'béton' in q_lower or 'bois' in q_lower:
            return {
                'reponse': "🏗️ **Choix du matériau en RDM**\n\n"
                          "Chaque matériau a ses propriétés :\n\n"
                          "**Acier :**\n"
                          "• Module d'Young E ≈ 200 GPa\n"
                          "• Résistance élevée\n"
                          "• Ductile (se déforme avant rupture)\n\n"
                          "**Béton :**\n"
                          "• E ≈ 30 GPa\n"
                          "• Bon en compression, faible en traction\n"
                          "• Souvent armé avec de l'acier\n\n"
                          "**Bois :**\n"
                          "• E ≈ 10 GPa (variable selon essence)\n"
                          "• Anisotrope (propriétés différentes selon le sens des fibres)\n\n"
                          "🧪 **Teste dans ta simulation :**\n"
                          "Change le matériau et observe comment la flèche évolue !",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Aide générale
        if 'aide' in q_lower or 'comment' in q_lower or 'expliqu' in q_lower:
            return {
                'reponse': f"🏗️ **Je suis ETA, ton assistant en Génie Civil !**\n\n"
                          f"Pour ce TP, je peux t'aider sur :\n"
                          f"• 📐 Le calcul des moments fléchissants\n"
                          f"• 📏 La déformation des poutres (flèche)\n"
                          f"• 💪 Les contraintes normales et de cisaillement\n"
                          f"• 🏗️ Le choix des matériaux\n"
                          f"• 📊 L'interprétation de tes graphiques\n\n"
                          f"💡 **Astuce :** Pose des questions précises ! Par exemple :\n"
                          f"• 'Comment calculer le moment maximal ?'\n"
                          f"• 'Pourquoi la flèche augmente avec la longueur ?'\n"
                          f"• 'Où se situe la contrainte maximale ?'",
                'pertinence_question': 3,
                'aide_apportee': True
            }

        # Réponse générique
        return {
            'reponse': f"🏗️ **ETA à ton service !**\n\n"
                      f"Ta question concerne quoi exactement ?\n"
                      f"• La résistance des matériaux (RDM) ?\n"
                      f"• Les charges et réactions ?\n"
                      f"• Le dimensionnement de structures ?\n"
                      f"• Les matériaux de construction ?\n\n"
                      f"Précise ta question et je t'aiderai avec plaisir ! 😊",
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
                'reponse': "🚫 **Je ne rédige pas de rapports !**\n\n"
                          "Analyse tes données et tire tes propres conclusions. "
                          "C'est la meilleure façon d'apprendre ! 📊",
                'pertinence_question': 1,
                'aide_apportee': False
            }

        # Logistique - Stocks
        if 'stock' in q_lower or 'rupture' in q_lower or 'wilson' in q_lower:
            D = contexte.get('demande_annuelle', 1000)
            Cc = contexte.get('cout_commande', 50)
            Cp = contexte.get('cout_possession', 2)

            import math
            QEC = math.sqrt((2 * D * Cc) / Cp) if Cp > 0 else 0

            return {
                'reponse': f"📦 **Modèle de Wilson - Quantité Économique de Commande (QEC)**\n\n"
                          f"**Formule :** QEC = √(2 × D × Cc / Cp)\n\n"
                          f"**Tes paramètres actuels :**\n"
                          f"• Demande annuelle (D) = {D} unités\n"
                          f"• Coût de commande (Cc) = {Cc} €\n"
                          f"• Coût de possession (Cp) = {Cp} €/unité/an\n\n"
                          f"**QEC optimale = {QEC:.0f} unités**\n\n"
                          f"🎯 **Interprétation :**\n"
                          f"• Commander {QEC:.0f} unités à chaque fois minimise les coûts totaux\n"
                          f"• Nombre de commandes/an = {D/QEC if QEC > 0 else 0:.1f}\n"
                          f"• Stock moyen = {QEC/2:.0f} unités\n\n"
                          f"💡 **Point de rupture :**\n"
                          f"Le stock atteint zéro juste avant chaque nouvelle commande.\n"
                          f"As-tu identifié ce point dans ta simulation ?",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Transport - Routage
        if 'route' in q_lower or 'chemin' in q_lower or 'dijkstra' in q_lower or 'plus court' in q_lower:
            return {
                'reponse': "🚚 **Algorithme de Dijkstra - Plus Court Chemin**\n\n"
                          "**Principe :**\n"
                          "Trouve le chemin le plus court entre deux sommets d'un graphe.\n\n"
                          "**Étapes de l'algorithme :**\n"
                          "1. Initialiser toutes les distances à l'infini (sauf le sommet de départ à 0)\n"
                          "2. Choisir le sommet non visité avec la plus petite distance\n"
                          "3. Pour chaque voisin, calculer la distance via ce sommet\n"
                          "4. Mettre à jour si on trouve un chemin plus court\n"
                          "5. Répéter jusqu'à avoir visité tous les sommets\n\n"
                          "🧪 **Dans ta simulation :**\n"
                          "• Modifie les poids des arêtes et observe comment le chemin optimal change\n"
                          "• Un poids élevé = route coûteuse/longue\n"
                          "• Peut représenter : distance, temps, coût, consommation...",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Maths - Fourier
        if 'fourier' in q_lower or 'fft' in q_lower or 'fréquence' in q_lower or 'spectre' in q_lower:
            freq = contexte.get('freq', 5)
            amplitude = contexte.get('amplitude', 1)
            bruit = contexte.get('bruit', 0.1)

            return {
                'reponse': f"📊 **Transformée de Fourier (FFT)**\n\n"
                          f"La FFT décompose un signal temporel en ses composantes fréquentielles.\n\n"
                          f"**Ton signal actuel :**\n"
                          f"• Fréquence fondamentale : {freq} Hz\n"
                          f"• Amplitude : {amplitude}\n"
                          f"• Niveau de bruit : {bruit}\n\n"
                          f"🔍 **Ce que tu devrais observer :**\n"
                          f"• Un pic à {freq} Hz dans le spectre (ta fréquence)\n"
                          f"• Des composantes aléatoires dues au bruit\n"
                          f"• Plus le bruit est élevé, plus le spectre est 'bruité'\n\n"
                          f"💡 **Expériences à faire :**\n"
                          f"1. Change la fréquence → le pic se déplace\n"
                          f"2. Augmente le bruit → observe la dégradation\n"
                          f"3. Ajoute plusieurs fréquences → vois les harmoniques\n\n"
                          f"📐 **Applications réelles :**\n"
                          f"Analyse audio, traitement d'images, télécommunications, sismologie...",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Optimisation
        if 'optimisation' in q_lower or 'optimiser' in q_lower:
            return {
                'reponse': "🎯 **Optimisation en logistique**\n\n"
                          "Plusieurs problèmes d'optimisation classiques :\n\n"
                          "**1. Minimiser les coûts de stock**\n"
                          "→ Modèle de Wilson (QEC)\n\n"
                          "**2. Minimiser les distances de transport**\n"
                          "→ Algorithme de Dijkstra, problème du voyageur de commerce\n\n"
                          "**3. Maximiser la capacité de production**\n"
                          "→ Programmation linéaire\n\n"
                          "🔬 **Dans ta simulation :**\n"
                          "• Identifie la fonction objectif (ce qu'on veut optimiser)\n"
                          "• Identifie les contraintes (limites à respecter)\n"
                          "• Teste différentes configurations",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Algorithmes
        if 'algorithme' in q_lower or 'complexité' in q_lower:
            return {
                'reponse': "💻 **Algorithmes et Complexité**\n\n"
                          "**Complexités courantes :**\n"
                          "• O(1) - Constant : accès direct à un élément\n"
                          "• O(log n) - Logarithmique : recherche dichotomique\n"
                          "• O(n) - Linéaire : parcourir un tableau\n"
                          "• O(n log n) - Linéarithmique : tri rapide, tri fusion\n"
                          "• O(n²) - Quadratique : tri à bulles, recherche naïve\n"
                          "• O(2^n) - Exponentielle : problèmes NP-complets\n\n"
                          "🎯 **Dijkstra :**\n"
                          "Complexité avec tas : O((V + E) log V)\n"
                          "Où V = sommets, E = arêtes",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Statistiques
        if 'statistique' in q_lower or 'moyenne' in q_lower or 'écart-type' in q_lower or 'variance' in q_lower:
            return {
                'reponse': "📈 **Statistiques Descriptives**\n\n"
                          "**Indicateurs de position :**\n"
                          "• Moyenne : μ = Σxi / n\n"
                          "• Médiane : valeur centrale\n"
                          "• Mode : valeur la plus fréquente\n\n"
                          "**Indicateurs de dispersion :**\n"
                          "• Variance : σ² = Σ(xi - μ)² / n\n"
                          "• Écart-type : σ = √variance\n"
                          "• Étendue : max - min\n\n"
                          "🔬 **Dans ta simulation :**\n"
                          "Calcule ces indicateurs sur tes données et compare !",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Probabilités
        if 'probabilité' in q_lower or 'loi normale' in q_lower or 'gauss' in q_lower:
            return {
                'reponse': "🎲 **Probabilités et Lois**\n\n"
                          "**Loi Normale (Gauss) :**\n"
                          "• Moyenne μ, écart-type σ\n"
                          "• 68% des valeurs dans [μ-σ, μ+σ]\n"
                          "• 95% dans [μ-2σ, μ+2σ]\n"
                          "• 99.7% dans [μ-3σ, μ+3σ]\n\n"
                          "**Autres lois courantes :**\n"
                          "• Binomiale : n essais, proba p\n"
                          "• Poisson : événements rares\n"
                          "• Exponentielle : durée de vie\n\n"
                          "❓ Quelle loi utilises-tu dans ta simulation ?",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Matrices
        if 'matrice' in q_lower or 'déterminant' in q_lower or 'inverse' in q_lower:
            return {
                'reponse': "🔢 **Calcul Matriciel**\n\n"
                          "**Opérations de base :**\n"
                          "• Addition : A + B (même dimension)\n"
                          "• Multiplication : A × B (colonnes A = lignes B)\n"
                          "• Transposée : Aᵀ (lignes ↔ colonnes)\n\n"
                          "**Déterminant (2×2) :**\n"
                          "det(A) = ad - bc pour A = [[a,b],[c,d]]\n\n"
                          "**Matrice inverse :**\n"
                          "• Existe si det(A) ≠ 0\n"
                          "• A × A⁻¹ = I (identité)\n\n"
                          "🔬 **Application :**\n"
                          "Résolution de systèmes linéaires : X = A⁻¹ × B",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Équations différentielles
        if 'différentielle' in q_lower or 'edo' in q_lower or 'dy/dx' in q_lower:
            return {
                'reponse': "📐 **Équations Différentielles**\n\n"
                          "**EDO du 1er ordre :**\n"
                          "dy/dx = f(x,y)\n\n"
                          "**Méthodes de résolution :**\n"
                          "• Séparation des variables\n"
                          "• Variation de la constante\n"
                          "• Euler numérique : y(n+1) = y(n) + h×f(x,y)\n\n"
                          "**EDO du 2nd ordre :**\n"
                          "y'' + ay' + by = f(x)\n"
                          "→ Équation caractéristique : r² + ar + b = 0\n\n"
                          "🔬 **Dans ta simulation :**\n"
                          "Compare Euler avec la solution analytique !",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Aide générale
        if 'aide' in q_lower or 'comment' in q_lower or 'expliqu' in q_lower:
            return {
                'reponse': "🧮 **ALPHA - Expert Multi-domaines**\n\n"
                          "Je peux t'aider sur :\n"
                          "• 📦 **Logistique :** gestion des stocks, modèle de Wilson\n"
                          "• 🚚 **Transport :** optimisation de routes, Dijkstra\n"
                          "• 📊 **Mathématiques :** Fourier, matrices, EDO\n"
                          "• 📈 **Statistiques :** moyenne, variance, lois\n"
                          "• 💻 **Informatique :** algorithmes, complexité\n\n"
                          "💡 **Exemples de questions :**\n"
                          "• 'Comment calculer la QEC ?'\n"
                          "• 'Explique-moi l'algorithme de Dijkstra'\n"
                          "• 'Comment résoudre une EDO ?'\n"
                          "• 'À quoi sert la transformée de Fourier ?'",
                'pertinence_question': 3,
                'aide_apportee': True
            }

        # Réponse générique
        return {
            'reponse': "🧮 **Je suis ALPHA !**\n\n"
                      "Spécialiste en :\n"
                      "• 📊 Mathématiques appliquées\n"
                      "• 💻 Informatique et algorithmes\n"
                      "• 📦 Logistique et gestion\n"
                      "• 🚚 Transport et optimisation\n\n"
                      "Précise ta question (stocks, routes, Fourier, algorithmes...) "
                      "et je t'aiderai avec plaisir ! 🎯",
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
        if any(mot in q_lower for mot in ['conclusion', 'rapport', 'fais', 'écris', 'rédige']):
            return {
                'reponse': "⚡ **Je ne fais pas les rapports !**\n\n"
                          "Mon rôle : t'aider à **comprendre** l'électronique de puissance.\n"
                          "Observe tes courbes et déduis par toi-même. C'est comme ça qu'on apprend ! 💪",
                'pertinence_question': 1,
                'aide_apportee': False
            }

        # Buck converter
        if 'buck' in q_lower or 'hacheur' in q_lower or 'abaisseur' in q_lower:
            alpha = contexte.get('alpha', 0.5)
            vin = contexte.get('vin', 24)
            vout_theorique = alpha * vin

            if 'tension' in q_lower or 'vout' in q_lower:
                return {
                    'reponse': f"⚙️ **Convertisseur Buck (Abaisseur de tension)**\n\n"
                              f"**Principe :** Vout = α × Vin\n\n"
                              f"**Tes paramètres actuels :**\n"
                              f"• Vin = {vin} V\n"
                              f"• Rapport cyclique α = {alpha}\n"
                              f"• **Vout théorique = {vout_theorique:.2f} V**\n\n"
                              f"🔍 **Vérifie dans ta simulation :**\n"
                              f"1. Ta tension de sortie est-elle proche de {vout_theorique:.2f}V ?\n"
                              f"2. Si elle est inférieure, c'est normal (pertes dans le circuit)\n"
                              f"3. L'ondulation résiduelle dépend du filtre LC\n\n"
                              f"💡 **Astuce :** Change α et observe l'impact instantané sur Vout !",
                    'pertinence_question': 5,
                    'aide_apportee': True
                }
            elif 'courant' in q_lower:
                return {
                    'reponse': f"⚡ **Courant dans le Buck**\n\n"
                              f"Le courant de sortie dépend de la charge (résistance R_load).\n\n"
                              f"**Formules :**\n"
                              f"• I_out = V_out / R_load\n"
                              f"• Le courant dans l'inductance est continu (mode CCM) si L est assez grand\n\n"
                              f"🔬 **Expérience :**\n"
                              f"• Augmente R_load → le courant diminue\n"
                              f"• Augmente L → l'ondulation du courant diminue",
                    'pertinence_question': 4,
                    'aide_apportee': True
                }

        # Ondulation
        if 'ondulation' in q_lower or 'ripple' in q_lower or 'filtrage' in q_lower:
            C = contexte.get('C', 100)
            L = contexte.get('L', 1)
            return {
                'reponse': f"📉 **Ondulation de tension (Ripple)**\n\n"
                          f"L'ondulation diminue quand tu augmentes **C** ou **L**.\n\n"
                          f"**Tes valeurs actuelles :**\n"
                          f"• C = {C} μF\n"
                          f"• L = {L} mH\n\n"
                          f"**Formule approximative :**\n"
                          f"ΔV ≈ (I_load × T) / (8 × C)\n\n"
                          f"Où T = période de découpage\n\n"
                          f"🧪 **Teste :**\n"
                          f"1. Double C → l'ondulation est divisée par 2\n"
                          f"2. Augmente la fréquence → l'ondulation diminue",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Rendement
        if 'rendement' in q_lower or 'efficacité' in q_lower or 'perte' in q_lower:
            return {
                'reponse': "📊 **Rendement d'un convertisseur Buck**\n\n"
                          "Le rendement η = (P_out / P_in) × 100%\n\n"
                          "**Les pertes viennent de :**\n"
                          "• Résistance de l'inductance (pertes Joule)\n"
                          "• Résistance série du condensateur (ESR)\n"
                          "• Commutation du transistor\n"
                          "• Diode de roue libre\n\n"
                          "Un bon Buck a un rendement > 90% !\n\n"
                          "🎯 **Dans ta simulation :**\n"
                          "Compare Pin = Vin × Iin et Pout = Vout × Iout",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Mode de conduction
        if 'ccm' in q_lower or 'dcm' in q_lower or 'conduction' in q_lower:
            return {
                'reponse': "🔄 **Modes de conduction**\n\n"
                          "**CCM (Continuous Conduction Mode) :**\n"
                          "• Le courant dans L ne s'annule jamais\n"
                          "• Se produit avec forte charge ou grande inductance\n\n"
                          "**DCM (Discontinuous Conduction Mode) :**\n"
                          "• Le courant dans L atteint zéro pendant une partie de la période\n"
                          "• Se produit avec faible charge ou petite inductance\n\n"
                          "💡 Pour rester en CCM : augmente L ou augmente la charge !",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Boost converter
        if 'boost' in q_lower or 'élévateur' in q_lower or 'survolteur' in q_lower:
            alpha = contexte.get('alpha', 0.5)
            vin = contexte.get('vin', 12)
            vout_theorique = vin / (1 - alpha) if alpha < 1 else float('inf')
            return {
                'reponse': f"⬆️ **Convertisseur Boost (Élévateur de tension)**\n\n"
                          f"**Principe :** Vout = Vin / (1 - α)\n\n"
                          f"**Tes paramètres actuels :**\n"
                          f"• Vin = {vin} V\n"
                          f"• Rapport cyclique α = {alpha}\n"
                          f"• **Vout théorique = {vout_theorique:.2f} V**\n\n"
                          f"⚠️ **Attention :**\n"
                          f"• Le Boost ne peut QU'AUGMENTER la tension\n"
                          f"• α proche de 1 → Vout très élevé (mais pertes aussi !)\n"
                          f"• En pratique, limiter α < 0.8 pour un bon rendement\n\n"
                          f"🔬 **Expérience :** Varie α de 0.3 à 0.7 et observe Vout !",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Moteur électrique
        if 'moteur' in q_lower or 'mcc' in q_lower or 'mcc' in q_lower or 'machine' in q_lower:
            return {
                'reponse': "🔌 **Moteur à Courant Continu (MCC)**\n\n"
                          "**Équations fondamentales :**\n"
                          "• U = E + R×I (équation électrique)\n"
                          "• E = k×Φ×Ω (f.é.m.)\n"
                          "• C = k×Φ×I (couple)\n\n"
                          "**Où :**\n"
                          "• U = tension d'alimentation\n"
                          "• E = force électromotrice\n"
                          "• Ω = vitesse angulaire (rad/s)\n"
                          "• C = couple moteur (N·m)\n\n"
                          "**Pour varier la vitesse :**\n"
                          "1. Varier la tension U → le plus courant\n"
                          "2. Varier le flux Φ (défuxage)\n\n"
                          "🔬 **Dans ta simulation :**\n"
                          "Change U et observe l'impact sur Ω !",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Régulateur PID
        if 'pid' in q_lower or 'régulateur' in q_lower or 'asservissement' in q_lower:
            Kp = contexte.get('Kp', 1)
            Ki = contexte.get('Ki', 0.1)
            Kd = contexte.get('Kd', 0.01)
            return {
                'reponse': f"🎛️ **Régulateur PID**\n\n"
                          f"**Formule :** u(t) = Kp×e + Ki×∫e dt + Kd×de/dt\n\n"
                          f"**Tes paramètres actuels :**\n"
                          f"• Kp (Proportionnel) = {Kp}\n"
                          f"• Ki (Intégral) = {Ki}\n"
                          f"• Kd (Dérivé) = {Kd}\n\n"
                          f"**Rôle de chaque terme :**\n"
                          f"• **Kp** : Réduit l'erreur rapidement (⚠️ si trop grand → oscillations)\n"
                          f"• **Ki** : Élimine l'erreur statique (⚠️ si trop grand → instabilité)\n"
                          f"• **Kd** : Anticipe les variations (amortit les oscillations)\n\n"
                          f"💡 **Méthode de réglage :**\n"
                          f"1. Commence avec Ki = Kd = 0\n"
                          f"2. Augmente Kp jusqu'aux oscillations\n"
                          f"3. Ajoute Ki pour annuler l'erreur\n"
                          f"4. Ajoute Kd pour stabiliser",
                'pertinence_question': 5,
                'aide_apportee': True
            }

        # Transformateur
        if 'transformateur' in q_lower or 'transfo' in q_lower:
            return {
                'reponse': "🔄 **Transformateur**\n\n"
                          "**Rapport de transformation :**\n"
                          "m = N2/N1 = U2/U1 = I1/I2\n\n"
                          "**Types :**\n"
                          "• m < 1 : Abaisseur de tension\n"
                          "• m > 1 : Élévateur de tension\n"
                          "• m = 1 : Isolement galvanique\n\n"
                          "**Puissance :**\n"
                          "• Idéal : P1 = P2 (pas de pertes)\n"
                          "• Réel : P2 < P1 (pertes fer + cuivre)\n\n"
                          "🔬 **Expérience :**\n"
                          "Change le rapport N2/N1 et mesure U2 !",
                'pertinence_question': 4,
                'aide_apportee': True
            }

        # Aide générale
        if 'aide' in q_lower or 'comment' in q_lower or 'expliqu' in q_lower:
            return {
                'reponse': "⚡ **KAYT à ton service - Expert en Génie Électrique !**\n\n"
                          "Je peux t'aider sur :\n"
                          "• ⚙️ Les convertisseurs (Buck, Boost, Buck-Boost)\n"
                          "• 🔌 Les moteurs électriques (MCC, MAS)\n"
                          "• 🎛️ Les régulateurs PID\n"
                          "• 🔄 Les transformateurs\n"
                          "• 📉 L'ondulation et le filtrage\n"
                          "• 📈 Le rendement et les pertes\n\n"
                          "💡 **Questions utiles :**\n"
                          "• 'Comment calculer Vout du Buck ?'\n"
                          "• 'Comment régler un PID ?'\n"
                          "• 'Explique le fonctionnement du Boost'\n"
                          "• 'Comment améliorer le rendement ?'",
                'pertinence_question': 3,
                'aide_apportee': True
            }

        # Réponse générique
        return {
            'reponse': f"⚡ **KAYT - Expert Électronique de Puissance**\n\n"
                      f"Ta question concerne :\n"
                      f"• Le circuit Buck (convertisseur abaisseur) ?\n"
                      f"• Les tensions de sortie ?\n"
                      f"• Le filtrage et l'ondulation ?\n"
                      f"• Le rendement énergétique ?\n\n"
                      f"Précise ta question pour que je puisse mieux t'aider ! ⚡",
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