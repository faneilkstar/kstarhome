"""
Service IA Ultra-Avancé pour le Laboratoire Virtuel
Version 3.0 - Intelligence Conversationnelle avec Mémoire
Créé par : Ing. KOISSI-ZO Tonyi Constantin
"""

import json
import os
from datetime import datetime, timedelta
from collections import Counter

# Import conditionnel de google.generativeai
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

from app.models import (
    SessionTP, MesureSimulation, InteractionIA, TP,
    Badge, BadgeEtudiant, Etudiant
)
from app import db

# Configuration Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY and GENAI_AVAILABLE:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[IA Ultra] Erreur configuration Gemini: {e}")
        GEMINI_API_KEY = None
# ============================================================
# ANALYSEUR COMPORTEMENTAL
# ============================================================
class AnalyseurComportemental:
    """Analyse le comportement de l'étudiant pendant la session"""
    @staticmethod
    def detecter_blocage(session_tp):
        """Détecte si l'étudiant est bloqué"""
        mesures = MesureSimulation.query.filter_by(
            session_id=session_tp.id
        ).order_by(MesureSimulation.timestamp.desc()).limit(10).all()
        if len(mesures) < 3:
            return False, None
        # Vérifier si les paramètres n'ont pas changé depuis longtemps
        derniers_params = []
        for m in mesures[:5]:
            if m.parametres:
                try:
                    derniers_params.append(json.loads(m.parametres))
                except:
                    pass
        if len(derniers_params) >= 3:
            # Si tous les paramètres sont identiques
            if all(p == derniers_params[0] for p in derniers_params):
                return True, "parametres_identiques"
        # Vérifier le temps depuis la dernière mesure
        if mesures:
            temps_depuis_derniere = (datetime.utcnow() - mesures[0].timestamp).total_seconds()
            if temps_depuis_derniere > 300:  # 5 minutes sans activité
                return True, "inactivite"
        return False, None
    @staticmethod
    def analyser_progression(session_tp):
        """Analyse la progression de l'étudiant"""
        mesures = MesureSimulation.query.filter_by(
            session_id=session_tp.id
        ).order_by(MesureSimulation.timestamp).all()
        interactions = InteractionIA.query.filter_by(
            session_id=session_tp.id
        ).order_by(InteractionIA.timestamp).all()
        analyse = {
            'nb_mesures': len(mesures),
            'nb_questions': len(interactions),
            'parametres_explores': set(),
            'tendance': 'stable',
            'points_forts': [],
            'points_ameliorer': [],
            'autonomie_score': 0,
            'exploration_score': 0,
            'comprehension_score': 0
        }
        # Analyser les paramètres explorés
        for m in mesures:
            if m.parametres:
                try:
                    params = json.loads(m.parametres)
                    for key in params.keys():
                        analyse['parametres_explores'].add(key)
                except:
                    pass
        analyse['parametres_explores'] = list(analyse['parametres_explores'])
        # Calculer le score d'exploration
        nb_params = len(analyse['parametres_explores'])
        if nb_params >= 5:
            analyse['exploration_score'] = 5
        elif nb_params >= 3:
            analyse['exploration_score'] = 3
        else:
            analyse['exploration_score'] = 1
        # Calculer le score d'autonomie
        if len(interactions) == 0:
            analyse['autonomie_score'] = 5  # Très autonome
        elif len(interactions) <= 3:
            analyse['autonomie_score'] = 4
        elif len(interactions) <= 7:
            analyse['autonomie_score'] = 3
        else:
            analyse['autonomie_score'] = 2
        # Analyser la qualité des questions
        questions_pertinentes = sum(
            1 for i in interactions
            if i.pertinence_question and i.pertinence_question >= 4
        )
        if questions_pertinentes >= 3:
            analyse['comprehension_score'] = 5
            analyse['points_forts'].append("Questions pertinentes et réfléchies")
        elif questions_pertinentes >= 1:
            analyse['comprehension_score'] = 3
            analyse['points_forts'].append("Bonnes questions posées")
        else:
            analyse['comprehension_score'] = 2
            analyse['points_ameliorer'].append("Poser des questions plus ciblées")
        # Calculer la tendance
        if len(mesures) >= 5:
            debut = len([m for m in mesures[:5] if m.resultats])
            fin = len([m for m in mesures[-5:] if m.resultats])
            if fin > debut:
                analyse['tendance'] = 'progression'
            elif fin < debut:
                analyse['tendance'] = 'regression'
        return analyse
    @staticmethod
    def detecter_pattern_erreur(session_tp):
        """Détecte si l'étudiant fait des erreurs répétitives"""
        mesures = MesureSimulation.query.filter_by(
            session_id=session_tp.id
        ).order_by(MesureSimulation.timestamp.desc()).limit(20).all()
        erreurs = []
        for m in mesures:
            if m.resultats:
                try:
                    resultats = json.loads(m.resultats)
                    if resultats.get('erreur') or resultats.get('invalide'):
                        erreurs.append(resultats)
                except:
                    pass
        if len(erreurs) >= 3:
            return True, "erreurs_repetees"
        return False, None
# ============================================================
# GÉNÉRATEUR DE HINTS PROGRESSIFS
# ============================================================
class HintProgressif:
    """Génère des indices de plus en plus précis"""
    def __init__(self, session_tp, contexte):
        self.session_tp = session_tp
        self.contexte = contexte
        self.niveau_hint = self._calculer_niveau()
    def _calculer_niveau(self):
        """Calcule le niveau de hint à donner (1-5)"""
        interactions = InteractionIA.query.filter_by(
            session_id=self.session_tp.id
        ).count()
        # Plus l'étudiant a demandé d'aide, plus les hints sont précis
        if interactions <= 1:
            return 1
        elif interactions <= 3:
            return 2
        elif interactions <= 5:
            return 3
        elif interactions <= 8:
            return 4
        else:
            return 5
    def generer_hint(self, sujet):
        """Génère un hint adapté au niveau"""
        hints_buck = {
            1: "💡 **Indice :** Pense à la relation entre le rapport cyclique et la tension de sortie...",
            2: "💡 **Indice :** La formule du Buck relie α, Vin et Vout de manière directe.",
            3: "💡 **Indice :** Vout = α × Vin. As-tu vérifié tes valeurs ?",
            4: "💡 **Indice :** Avec α = {} et Vin = {}V, calcule Vout.".format(self.contexte.get('alpha', 0.5), self.contexte.get('vin', 24)),
            5: "💡 **Solution :** Vout = {} × {} = {:.2f}V".format(self.contexte.get('alpha', 0.5), self.contexte.get('vin', 24), self.contexte.get('alpha', 0.5) * self.contexte.get('vin', 24))
        }
        hints_rdm = {
            1: "💡 **Indice :** Pense au diagramme des moments fléchissants...",
            2: "💡 **Indice :** Le moment maximal se trouve souvent au milieu pour une poutre simplement appuyée.",
            3: "💡 **Indice :** M_max = (q × L²) / 8 pour une charge uniformément répartie.",
            4: "💡 **Indice :** Avec q = {} N/m et L = {}m...".format(self.contexte.get('charge', 100), self.contexte.get('longueur', 10)),
            5: "💡 **Solution :** M_max = ({} × {}²) / 8 = {:.2f} N·m".format(self.contexte.get('charge', 100), self.contexte.get('longueur', 10), (self.contexte.get('charge', 100) * self.contexte.get('longueur', 10)**2) / 8)
        }
        hints_logistique = {
            1: "💡 **Indice :** Le modèle de Wilson optimise les coûts totaux...",
            2: "💡 **Indice :** La QEC équilibre coûts de commande et de possession.",
            3: "💡 **Indice :** QEC = √(2 × D × Cc / Cp)",
            4: "💡 **Indice :** Avec D = {}, Cc = {}€...".format(self.contexte.get('demande_annuelle', 1000), self.contexte.get('cout_commande', 50)),
            5: "💡 **Solution :** QEC = √(2 × {} × {} / {}) = {:.0f} unités".format(self.contexte.get('demande_annuelle', 1000), self.contexte.get('cout_commande', 50), self.contexte.get('cout_possession', 2), ((2 * self.contexte.get('demande_annuelle', 1000) * self.contexte.get('cout_commande', 50)) / self.contexte.get('cout_possession', 2))**0.5)
        }
        # Sélectionner le bon set de hints
        if 'buck' in sujet or 'tension' in sujet or 'électrique' in sujet:
            hints = hints_buck
        elif 'rdm' in sujet or 'poutre' in sujet or 'moment' in sujet:
            hints = hints_rdm
        elif 'stock' in sujet or 'logistique' in sujet or 'wilson' in sujet:
            hints = hints_logistique
        else:
            return "💡 **Niveau {}/5 :** Je t'encourage à expérimenter davantage !".format(self.niveau_hint)
        return hints.get(self.niveau_hint, hints[3])
# ============================================================
# SUGGESTIONS PROACTIVES
# ============================================================
class SuggestionProactive:
    """Génère des suggestions d'expériences personnalisées"""
    @staticmethod
    def generer_suggestions(session_tp, contexte, type_simulation):
        """Génère des suggestions basées sur le contexte"""
        suggestions = []
        if type_simulation == 'buck':
            alpha = contexte.get('alpha', 0.5)
            vin = contexte.get('vin', 24)
            C = contexte.get('C', 100)
            L = contexte.get('L', 1)
            suggestions = [
                "🔬 **Expérience 1 :** Fixe α à 0.3, puis 0.5, puis 0.7. Compare les Vout.",
                "🔬 **Expérience 2 :** Double la capacité C ({} μF) et observe l'ondulation.".format(C*2),
                "🔬 **Expérience 3 :** Teste avec une charge plus importante pour voir le mode CCM.",
                "🔬 **Expérience 4 :** Compare les rendements à différentes fréquences de découpage.",
            ]
            # Suggestion adaptée à l'état actuel
            if alpha < 0.3:
                suggestions.insert(0, "⚠️ α est très faible. Essaie avec α = 0.5 pour voir un résultat plus visible.")
            elif alpha > 0.8:
                suggestions.insert(0, "⚠️ α est élevé (>80%). Vout sera proche de Vin. Essaie α = 0.5.")
        elif type_simulation == 'rdm_poutre':
            L = contexte.get('longueur', 10)
            q = contexte.get('charge', 100)
            suggestions = [
                "🔬 **Expérience 1 :** Double la longueur ({}m) et observe l'impact sur la flèche.".format(L*2),
                "🔬 **Expérience 2 :** Compare acier, béton et bois pour la même poutre.",
                "🔬 **Expérience 3 :** Charge ponctuelle vs charge répartie : quelles différences ?",
                "🔬 **Expérience 4 :** Trouve la charge limite avant dépassement de σ_admissible.",
            ]
        elif type_simulation == 'logistique':
            D = contexte.get('demande_annuelle', 1000)
            suggestions = [
                "🔬 **Expérience 1 :** Double la demande ({}) et observe l'impact sur QEC.".format(D*2),
                "🔬 **Expérience 2 :** Augmente le coût de possession et vois comment QEC réagit.",
                "🔬 **Expérience 3 :** Avec un coût de commande élevé, que devient le nombre de commandes ?",
                "🔬 **Expérience 4 :** Simule une rupture de stock et analyse l'impact.",
            ]
        elif type_simulation == 'fourier':
            freq = contexte.get('freq', 5)
            suggestions = [
                "🔬 **Expérience 1 :** Ajoute du bruit et observe la dégradation du spectre.",
                "🔬 **Expérience 2 :** Combine 2 fréquences et identifie les pics.",
                "🔬 **Expérience 3 :** Augmente l'échantillonnage pour améliorer la résolution.",
                "🔬 **Expérience 4 :** Filtre passe-bas : supprime les hautes fréquences.",
            ]
        else:
            suggestions = [
                "🔬 Fais varier les paramètres un par un pour observer leur impact.",
                "🔬 Compare les résultats théoriques et expérimentaux.",
                "🔬 Note les valeurs extrêmes (min et max).",
            ]
        return suggestions[:4]
# ============================================================
# GESTIONNAIRE DE BADGES AUTOMATIQUE
# ============================================================
class GestionnaireBadges:
    """Gère l'attribution automatique des badges"""
    BADGES_CONFIG = {
        'premier_tp': {
            'nom': 'Premier Pas',
            'description': 'A complété son premier TP',
            'icone': 'fa-star',
            'couleur': '#ffd700',
            'criteres': {'nb_sessions': 1},
            'points': 10
        },
        'explorateur': {
            'nom': 'Explorateur',
            'description': 'A testé plus de 10 configurations différentes',
            'icone': 'fa-compass',
            'couleur': '#3498db',
            'criteres': {'nb_configs': 10},
            'points': 25
        },
        'autonome': {
            'nom': 'Autonome',
            'description': 'A terminé un TP sans aide de l\'IA',
            'icone': 'fa-shield-halved',
            'couleur': '#27ae60',
            'criteres': {'sans_aide': True},
            'points': 50
        },
        'perseverant': {
            'nom': 'Persévérant',
            'description': 'A passé plus d\'une heure sur un TP',
            'icone': 'fa-hourglass-half',
            'couleur': '#9b59b6',
            'criteres': {'temps_min': 60},
            'points': 30
        },
        'perfectionniste': {
            'nom': 'Perfectionniste',
            'description': 'A obtenu 18/20 ou plus',
            'icone': 'fa-trophy',
            'couleur': '#e74c3c',
            'criteres': {'note_min': 18},
            'points': 100
        },
        'curieux': {
            'nom': 'Curieux',
            'description': 'A posé 10 questions pertinentes',
            'icone': 'fa-question-circle',
            'couleur': '#f39c12',
            'criteres': {'questions_pertinentes': 10},
            'points': 40
        },
        'scientifique': {
            'nom': 'Scientifique',
            'description': 'A pris plus de 50 mesures',
            'icone': 'fa-flask',
            'couleur': '#1abc9c',
            'criteres': {'nb_mesures': 50},
            'points': 35
        }
    }
    @staticmethod
    def verifier_badges(etudiant_id, session_tp=None):
        """Vérifie et attribue les badges mérités"""
        badges_obtenus = []
        # Récupérer les stats de l'étudiant
        sessions = SessionTP.query.filter_by(etudiant_id=etudiant_id).all()
        nb_sessions = len([s for s in sessions if s.statut == 'terminee'])
        # Badge: Premier TP
        if nb_sessions >= 1:
            badge = GestionnaireBadges._attribuer_badge(etudiant_id, 'premier_tp', session_tp)
            if badge:
                badges_obtenus.append(badge)
        # Vérifier les badges liés à la session actuelle
        if session_tp:
            # Badge: Autonome (sans aide IA)
            nb_interactions = InteractionIA.query.filter_by(session_id=session_tp.id).count()
            if nb_interactions == 0 and session_tp.statut == 'terminee':
                badge = GestionnaireBadges._attribuer_badge(etudiant_id, 'autonome', session_tp)
                if badge:
                    badges_obtenus.append(badge)
            # Badge: Persévérant (>1h)
            if session_tp.duree_minutes and session_tp.duree_minutes >= 60:
                badge = GestionnaireBadges._attribuer_badge(etudiant_id, 'perseverant', session_tp)
                if badge:
                    badges_obtenus.append(badge)
            # Badge: Perfectionniste (note >= 18)
            if session_tp.note_ia and session_tp.note_ia >= 18:
                badge = GestionnaireBadges._attribuer_badge(etudiant_id, 'perfectionniste', session_tp)
                if badge:
                    badges_obtenus.append(badge)
            # Badge: Scientifique (>50 mesures)
            nb_mesures = MesureSimulation.query.filter_by(session_id=session_tp.id).count()
            if nb_mesures >= 50:
                badge = GestionnaireBadges._attribuer_badge(etudiant_id, 'scientifique', session_tp)
                if badge:
                    badges_obtenus.append(badge)
        # Badge: Explorateur (>10 configs au total)
        total_configs = set()
        for s in sessions:
            mesures = MesureSimulation.query.filter_by(session_id=s.id).all()
            for m in mesures:
                if m.parametres:
                    total_configs.add(m.parametres)
        if len(total_configs) >= 10:
            badge = GestionnaireBadges._attribuer_badge(etudiant_id, 'explorateur', session_tp)
            if badge:
                badges_obtenus.append(badge)
        # Badge: Curieux (10 questions pertinentes)
        total_questions_pertinentes = InteractionIA.query.filter(
            InteractionIA.session_id.in_([s.id for s in sessions]),
            InteractionIA.pertinence_question >= 4
        ).count()
        if total_questions_pertinentes >= 10:
            badge = GestionnaireBadges._attribuer_badge(etudiant_id, 'curieux', session_tp)
            if badge:
                badges_obtenus.append(badge)
        return badges_obtenus
    @staticmethod
    def _attribuer_badge(etudiant_id, badge_key, session_tp=None):
        """Attribue un badge s'il n'est pas déjà obtenu"""
        config = GestionnaireBadges.BADGES_CONFIG.get(badge_key)
        if not config:
            return None
        # Vérifier si le badge existe
        badge = Badge.query.filter_by(nom=config['nom']).first()
        if not badge:
            # Créer le badge
            badge = Badge(
                nom=config['nom'],
                description=config['description'],
                icone=config['icone'],
                couleur=config['couleur'],
                criteres=json.dumps(config['criteres']),
                points=config['points']
            )
            db.session.add(badge)
            db.session.commit()
        # Vérifier si l'étudiant a déjà ce badge
        deja_obtenu = BadgeEtudiant.query.filter_by(
            etudiant_id=etudiant_id,
            badge_id=badge.id
        ).first()
        if not deja_obtenu:
            nouveau_badge = BadgeEtudiant(
                etudiant_id=etudiant_id,
                badge_id=badge.id,
                session_id=session_tp.id if session_tp else None
            )
            db.session.add(nouveau_badge)
            db.session.commit()
            return badge
        return None
# ============================================================
# ASSISTANT IA ULTRA AVANCÉ
# ============================================================
class AssistantIAUltra:
    """Assistant IA de nouvelle génération avec mémoire conversationnelle"""
    def __init__(self, nom, domaine, couleur):
        self.nom = nom
        self.domaine = domaine
        self.couleur = couleur
        self.model = None
        if GEMINI_API_KEY and GENAI_AVAILABLE and genai:
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                try:
                    self.model = genai.GenerativeModel('gemini-pro')
                except Exception:
                    self.model = None
    def _build_system_prompt(self, session_tp, historique, analyse):
        """Construit un prompt système ultra-enrichi"""
        return """
# 🤖 TU ES {} - ASSISTANT PÉDAGOGIQUE INTELLIGENT
## 🎓 DOMAINE D'EXPERTISE
{}
## 🎯 MISSION PRINCIPALE
Tu guides l'étudiant dans son apprentissage expérimental SANS faire le travail à sa place.
Tu utilises la méthode SOCRATIQUE : poser des questions pour faire réfléchir.
## 📊 ANALYSE DE L'ÉTUDIANT (en temps réel)
- Nombre de mesures effectuées : {}
- Nombre de questions posées : {}
- Score d'autonomie : {}/5
- Score d'exploration : {}/5
- Score de compréhension : {}/5
- Tendance : {}
- Paramètres explorés : {}
## 🧠 HISTORIQUE DE LA CONVERSATION
{}
## ❌ INTERDICTIONS ABSOLUES
1. NE JAMAIS rédiger la conclusion ou le rapport
2. NE JAMAIS donner la réponse complète directement
3. NE JAMAIS faire les calculs complets sans explication pédagogique
4. NE JAMAIS valider un résultat sans questionnement
## ✅ APPROCHE PÉDAGOGIQUE
1. Commence par reconnaître la question
2. Pose une question de clarification si nécessaire
3. Donne des indices progressifs (pas la réponse directe)
4. Encourage l'expérimentation
5. Utilise des emojis pour rendre la conversation vivante
6. Reste bienveillant et encourageant
## 📏 FORMAT DE RÉPONSE
- Maximum 200 mots
- Structuré avec des emojis
- Termine par une question ou une suggestion d'expérience
- Utilise le Markdown pour la mise en forme
## 🚨 SI L'ÉTUDIANT DEMANDE DE TRICHER
Réponds poliment mais fermement que tu ne peux pas faire son travail.
Propose-lui de l'aider à COMPRENDRE plutôt qu'à copier.
""".format(
            self.nom,
            self.domaine,
            analyse.get('nb_mesures', 0),
            analyse.get('nb_questions', 0),
            analyse.get('autonomie_score', 0),
            analyse.get('exploration_score', 0),
            analyse.get('comprehension_score', 0),
            analyse.get('tendance', 'stable'),
            ', '.join(analyse.get('parametres_explores', [])),
            historique
        )
    def _get_historique_complet(self, session_id, limit=5):
        """Récupère l'historique avec contexte"""
        interactions = InteractionIA.query.filter_by(
            session_id=session_id
        ).order_by(InteractionIA.timestamp.desc()).limit(limit).all()
        if not interactions:
            return "Première question de l'étudiant."
        historique = []
        for i in reversed(interactions):
            historique.append("👤 Étudiant : {}".format(i.question_etudiant))
            historique.append("🤖 {} : {}...".format(self.nom, i.reponse_ia[:150]))
            historique.append("")
        return "\n".join(historique)
    def generer_reponse(self, question, contexte, session_tp):
        """Génère une réponse ultra-intelligente"""
        # Analyse comportementale
        analyseur = AnalyseurComportemental()
        analyse = analyseur.analyser_progression(session_tp)
        # Vérifier si l'étudiant est bloqué
        est_bloque, raison_blocage = analyseur.detecter_blocage(session_tp)
        # Récupérer l'historique
        historique = self._get_historique_complet(session_tp.id)
        # Détecter les tentatives de triche
        q_lower = question.lower()
        mots_triche = ['conclusion', 'rapport', 'fais pour moi', 'écris', 'rédige',
                       'donne la réponse', 'réponds pour moi', 'fait le travail']
        if any(mot in q_lower for mot in mots_triche):
            return {
                'reponse': """🛑 **Holà, je ne peux pas faire ça !**
Mon rôle est de t'aider à **comprendre**, pas de faire ton travail à ta place.
📝 **Ce que je PEUX faire :**
- Expliquer les concepts
- Poser des questions pour te guider
- Donner des indices progressifs
- Vérifier ta compréhension
❓ **Question pour toi :**
Qu'as-tu observé dans tes mesures ? Y a-t-il une tendance qui se dégage ?
Je suis là pour t'aider à **apprendre** ! 💪
""",
                'pertinence_question': 1,
                'aide_apportee': False,
                'est_triche': True
            }
        # Générer des suggestions proactives si bloqué
        suggestions = None
        if est_bloque:
            type_sim = session_tp.tp.type_simulation if session_tp.tp else 'general'
            suggestions = SuggestionProactive.generer_suggestions(session_tp, contexte, type_sim)
        # Construire le prompt pour Gemini
        system_prompt = self._build_system_prompt(session_tp, historique, analyse)
        prompt_complet = """
{}
## 📊 PARAMÈTRES ACTUELS DE SIMULATION
```json
{}
```
## 🚨 ÉTAT DE L'ÉTUDIANT
- Est bloqué : {} ({})
- Points forts : {}
- Points à améliorer : {}
## ❓ QUESTION ACTUELLE DE L'ÉTUDIANT
"{}"
## 🎯 TA RÉPONSE (max 200 mots, en français) :
""".format(
            system_prompt,
            json.dumps(contexte, indent=2, ensure_ascii=False),
            est_bloque,
            raison_blocage or 'Non',
            ', '.join(analyse.get('points_forts', ['À développer'])),
            ', '.join(analyse.get('points_ameliorer', ['À développer'])),
            question
        )
        try:
            if self.model:
                response = self.model.generate_content(prompt_complet)
                reponse_texte = response.text
                # Ajouter des suggestions si l'étudiant est bloqué
                if est_bloque and suggestions:
                    reponse_texte += "\n\n---\n📍 **Je vois que tu explores. Voici quelques idées :**\n"
                    for s in suggestions[:2]:
                        reponse_texte += "\n{}".format(s)
                pertinence = self._calculer_pertinence(question, analyse)
            else:
                reponse_texte = self._reponse_fallback_intelligente(question, contexte, est_bloque, suggestions)
                pertinence = 3
            return {
                'reponse': reponse_texte,
                'pertinence_question': pertinence,
                'aide_apportee': True,
                'analyse': analyse,
                'suggestions': suggestions
            }
        except Exception as e:
            print("Erreur Gemini: {}".format(e))
            return {
                'reponse': self._reponse_fallback_intelligente(question, contexte, est_bloque, suggestions),
                'pertinence_question': 3,
                'aide_apportee': True
            }
    def _calculer_pertinence(self, question, analyse):
        """Calcule la pertinence de la question (1-5)"""
        q_lower = question.lower()
        # Mots clés de haute pertinence
        if any(mot in q_lower for mot in ['pourquoi', 'comment', 'expliquer', 'comprendre']):
            return 5
        elif any(mot in q_lower for mot in ['différence', 'comparer', 'relation', 'impact']):
            return 5
        elif any(mot in q_lower for mot in ['aide', 'problème', 'erreur', 'bizarre']):
            return 4
        elif any(mot in q_lower for mot in ['résultat', 'valeur', 'normal', 'attendu']):
            return 3
        else:
            return 3
    def _reponse_fallback_intelligente(self, question, contexte, est_bloque, suggestions):
        """Génère une réponse intelligente sans Gemini"""
        q_lower = question.lower()
        intro = "🤖 Je suis **{}**, ton assistant en {}.\n\n".format(self.nom, self.domaine)
        # Réponse adaptée au contexte
        if est_bloque:
            reponse = intro + "💡 Je vois que tu réfléchis... Voici quelques pistes :\n\n"
            if suggestions:
                for s in suggestions[:2]:
                    reponse += "{}\n".format(s)
            reponse += "\n❓ Sur quel aspect as-tu besoin d'aide ?"
        elif 'aide' in q_lower or 'comment' in q_lower:
            reponse = intro + """📚 **Je peux t'aider avec :**
- 📐 Les formules théoriques
- 📊 L'interprétation de tes résultats
- 🔬 Des suggestions d'expériences
- 💡 Des indices pour avancer
❓ **Quelle est ta question précise ?**
"""
        elif 'résultat' in q_lower or 'bon' in q_lower:
            reponse = intro + """🔍 **Pour vérifier tes résultats :**
1. Compare avec la formule théorique
2. Vérifie que les ordres de grandeur sont cohérents
3. Observe si les variations sont logiques
❓ Quelle valeur t'interroge exactement ?
"""
        else:
            reponse = intro + """Je suis là pour t'aider à comprendre !
📊 Je vois que tu travailles avec les paramètres actuels.
Peux-tu me préciser ta question ?
💡 **Exemples de bonnes questions :**
- "Pourquoi ma valeur est différente de la théorie ?"
- "Comment interpréter ce résultat ?"
- "Quel paramètre a le plus d'impact ?"
"""
        return reponse
    def evaluer_session(self, session_tp):
        """Évaluation avancée avec analyse comportementale"""
        analyseur = AnalyseurComportemental()
        analyse = analyseur.analyser_progression(session_tp)
        # Critères pondérés
        criteres = {
            'nombre_mesures': 0,
            'exploration': analyse['exploration_score'],
            'autonomie': analyse['autonomie_score'],
            'comprehension': analyse['comprehension_score'],
            'temps_investissement': 0,
            'qualite_demarche': 0
        }
        # Nombre de mesures
        nb_mesures = analyse['nb_mesures']
        if nb_mesures >= 30:
            criteres['nombre_mesures'] = 5
        elif nb_mesures >= 20:
            criteres['nombre_mesures'] = 4
        elif nb_mesures >= 10:
            criteres['nombre_mesures'] = 3
        elif nb_mesures >= 5:
            criteres['nombre_mesures'] = 2
        else:
            criteres['nombre_mesures'] = 1
        # Temps investi
        duree = session_tp.duree_minutes or 0
        if duree >= 60:
            criteres['temps_investissement'] = 5
        elif duree >= 45:
            criteres['temps_investissement'] = 4
        elif duree >= 30:
            criteres['temps_investissement'] = 3
        elif duree >= 15:
            criteres['temps_investissement'] = 2
        else:
            criteres['temps_investissement'] = 1
        # Qualité de la démarche scientifique
        if analyse['tendance'] == 'progression':
            criteres['qualite_demarche'] = 5
        elif len(analyse['parametres_explores']) >= 4:
            criteres['qualite_demarche'] = 4
        else:
            criteres['qualite_demarche'] = 3
        # Calcul note finale (pondérée)
        poids = {
            'nombre_mesures': 1.5,
            'exploration': 2.0,
            'autonomie': 1.5,
            'comprehension': 2.0,
            'temps_investissement': 1.0,
            'qualite_demarche': 2.0
        }
        total_points = sum(criteres[k] * poids[k] for k in criteres)
        max_points = sum(5 * poids[k] for k in poids)
        note = (total_points / max_points) * 20
        # Générer commentaire via IA si disponible
        if self.model and GEMINI_API_KEY and GENAI_AVAILABLE:
            try:
                commentaire = self._generer_commentaire_evaluation(session_tp, criteres, note, analyse)
            except:
                commentaire = self._commentaire_fallback(session_tp, criteres, note, analyse)
        else:
            commentaire = self._commentaire_fallback(session_tp, criteres, note, analyse)
        # Vérifier les badges
        badges = GestionnaireBadges.verifier_badges(session_tp.etudiant_id, session_tp)
        return {
            'note': round(note, 2),
            'commentaire': commentaire,
            'criteres': criteres,
            'analyse': analyse,
            'badges_obtenus': [b.nom for b in badges] if badges else []
        }
    def _generer_commentaire_evaluation(self, session_tp, criteres, note, analyse):
        """Génère un commentaire personnalisé via Gemini"""
        prompt = """
Tu es {}, assistant pédagogique évaluant une session de TP.
📊 DONNÉES DE LA SESSION :
- Durée : {} minutes
- Mesures : {}
- Questions posées : {}
- Note calculée : {:.1f}/20
- Tendance : {}
📈 CRITÈRES D'ÉVALUATION :
{}
📝 ANALYSE :
- Points forts : {}
- Points à améliorer : {}
🎯 RÉDIGE UN COMMENTAIRE D'ÉVALUATION (150 mots max) :
- Sois encourageant et constructif
- Mentionne 2-3 points positifs spécifiques
- Donne 1-2 conseils d'amélioration concrets
- Termine par une phrase motivante
- Utilise des emojis
Format Markdown.
""".format(
            self.nom,
            session_tp.duree_minutes or 0,
            analyse.get('nb_mesures', 0),
            analyse.get('nb_questions', 0),
            note,
            analyse.get('tendance', 'stable'),
            json.dumps(criteres, indent=2),
            ', '.join(analyse.get('points_forts', ['À développer'])),
            ', '.join(analyse.get('points_ameliorer', ['À développer']))
        )
        response = self.model.generate_content(prompt)
        return response.text
    def _commentaire_fallback(self, session_tp, criteres, note, analyse):
        """Commentaire de secours détaillé"""
        niveau = "Excellent" if note >= 16 else "Très bien" if note >= 14 else "Bien" if note >= 12 else "Satisfaisant" if note >= 10 else "À améliorer"
        points_forts_str = '\n'.join(['- ' + p for p in analyse.get('points_forts', ['Engagement dans le TP'])]) or '- Participation active'
        points_ameliorer_str = '\n'.join(['- ' + p for p in analyse.get('points_ameliorer', ['Continuer à explorer'])]) or '- Continuer sur cette lancée'
        conclusion = '🌟 **Excellent travail !** Continue ainsi !' if note >= 15 else '👍 **Bon travail !** Tu progresses bien.' if note >= 12 else '💪 **Tu peux y arriver !** Persévère et explore davantage.'
        return """
## ✅ Évaluation par {}
### 📊 Résumé de ta session
| Critère | Score |
|---------|-------|
| 📏 Nombre de mesures | {}/5 |
| 🔬 Exploration | {}/5 |
| 🎯 Autonomie | {}/5 |
| 🧠 Compréhension | {}/5 |
| ⏱️ Temps investi | {}/5 |
| 📐 Démarche scientifique | {}/5 |
### 🎯 Note automatique : **{:.1f}/20** ({})
### 💡 Points forts
{}
### 📈 Axes d'amélioration
{}
---
*💡 Cette note sera ajustée par ton enseignant après lecture de ton rapport.*
{}
""".format(
            self.nom,
            criteres['nombre_mesures'],
            criteres['exploration'],
            criteres['autonomie'],
            criteres['comprehension'],
            criteres['temps_investissement'],
            criteres['qualite_demarche'],
            note,
            niveau,
            points_forts_str,
            points_ameliorer_str,
            conclusion
        )
    def enregistrer_interaction(self, session_id, question, reponse_data, contexte):
        """Enregistre l'interaction dans la BDD"""
        interaction = InteractionIA(
            session_id=session_id,
            question_etudiant=question,
            reponse_ia=reponse_data['reponse'],
            contexte_simulation=json.dumps(contexte),
            ia_nom=self.nom,
            pertinence_question=reponse_data.get('pertinence_question', 3),
            aide_apportee=reponse_data.get('aide_apportee', True)
        )
        db.session.add(interaction)
        db.session.commit()
# ============================================================
# ASSISTANTS SPÉCIALISÉS ULTRA
# ============================================================
class ETAUltra(AssistantIAUltra):
    """Assistant IA Ultra pour le Génie Civil"""
    def __init__(self):
        super().__init__(
            nom="ETA",
            domaine="Génie Civil : RDM, Structures, Matériaux, Dimensionnement, BTP",
            couleur="#e74c3c"
        )
class ALPHAUltra(AssistantIAUltra):
    """Assistant IA Ultra pour Maths, Info, Logistique"""
    def __init__(self):
        super().__init__(
            nom="ALPHA",
            domaine="Mathématiques Appliquées, Informatique, Logistique, Transport, Optimisation, Algorithmes",
            couleur="#2ecc71"
        )
class KAYTUltra(AssistantIAUltra):
    """Assistant IA Ultra pour le Génie Électrique"""
    def __init__(self):
        super().__init__(
            nom="KAYT",
            domaine="Génie Électrique : Électronique de Puissance, Électrotechnique, Automatique, Convertisseurs",
            couleur="#f1c40f"
        )
# ============================================================
# FACTORY PATTERN ULTRA
# ============================================================
class IAFactoryUltra:
    """Factory pour créer les assistants IA Ultra"""
    @staticmethod
    def creer_assistant(nom_ia):
        if nom_ia == 'ETA':
            return ETAUltra()
        elif nom_ia == 'ALPHA':
            return ALPHAUltra()
        elif nom_ia == 'KAYT':
            return KAYTUltra()
        else:
            # Fallback sur ETA par défaut
            return ETAUltra()
    @staticmethod
    def get_tous_assistants():
        """Retourne la liste de tous les assistants"""
        return [
            {'nom': 'ETA', 'domaine': 'Génie Civil', 'couleur': '#e74c3c'},
            {'nom': 'ALPHA', 'domaine': 'Maths/Info/Logistique', 'couleur': '#2ecc71'},
            {'nom': 'KAYT', 'domaine': 'Génie Électrique', 'couleur': '#f1c40f'}
        ]
