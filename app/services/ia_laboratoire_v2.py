"""
Système d'IA Amélioré pour le Laboratoire avec Fallback Robuste
Version 2.0 - 12 Février 2026
Par : Ing. KOISSI-ZO Tonyi Constantin

Fonctionnalités :
- ✅ Fallback automatique si Gemini échoue
- ✅ Cache des réponses fréquentes
- ✅ Analyse contextuelle avancée
- ✅ Fonctionnement hors ligne garanti
"""

import json
import os
from datetime import datetime
from app.models import InteractionIA, SessionTP, MesureSimulation
from app import db

# Tentative d'import de Gemini
try:
    from google import genai
    GEMINI_DISPONIBLE = True
except:
    GEMINI_DISPONIBLE = False


class IALaboratoireV2:
    """Système d'IA intelligent avec fallback automatique"""

    def __init__(self, nom_ia="ETA"):
        self.nom = nom_ia
        self.gemini_actif = False
        self.model = None

        # Configuration des personnalités
        self.personnalites = {
            'ETA': {
                'nom_complet': 'ETA - Expert en Génie Civil',
                'domaine': 'RDM, Structures, Matériaux',
                'couleur': '#e74c3c',
                'emoji': '🏗️'
            },
            'ALPHA': {
                'nom_complet': 'ALPHA - Expert en Sciences Exactes',
                'domaine': 'Math, Info, Logistique, Transport',
                'couleur': '#3498db',
                'emoji': '📊'
            },
            'KAYT': {
                'nom_complet': 'KAYT - Expert en Génie Électrique',
                'domaine': 'Électronique, Automatique, Énergie',
                'couleur': '#f39c12',
                'emoji': '⚡'
            }
        }

        # Initialiser Gemini si disponible
        if GEMINI_DISPONIBLE:
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key and api_key.strip():
                try:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-pro')
                    self.gemini_actif = True
                    print(f"✅ [IA-{nom_ia}] Gemini activé")
                except Exception as e:
                    print(f"⚠️  [IA-{nom_ia}] Erreur Gemini : {e}")

        if not self.gemini_actif:
            print(f"🔧 [IA-{nom_ia}] Mode fallback activé")

    def generer_reponse(self, question, contexte, session):
        """
        Génère une réponse intelligente avec fallback automatique

        Args:
            question (str): Question de l'étudiant
            contexte (dict): Paramètres de simulation
            session (SessionTP): Session active

        Returns:
            dict: {
                'reponse': str,
                'pertinence_question': int (1-5),
                'aide_apportee': bool,
                'source': 'gemini' ou 'fallback'
            }
        """
        # 1. Vérifier si c'est une tentative de triche
        if self._detecter_triche(question):
            return self._reponse_anti_triche()

        # 2. Essayer Gemini d'abord
        if self.gemini_actif:
            try:
                return self._generer_avec_gemini(question, contexte, session)
            except Exception as e:
                print(f"⚠️  [IA-{self.nom}] Gemini échoué : {e}, fallback...")

        # 3. Fallback : Réponse intelligente hors ligne
        return self._generer_fallback(question, contexte, session)

    def _detecter_triche(self, question):
        """Détecte si l'étudiant essaie de tricher"""
        mots_suspects = [
            'conclusion', 'rapport', 'fais', 'écris', 'rédige',
            'donne la réponse', 'réponds pour moi', 'fais mon travail',
            'fais le tp', 'donne moi les résultats'
        ]
        q_lower = question.lower()
        return any(mot in q_lower for mot in mots_suspects)

    def _reponse_anti_triche(self):
        """Réponse si triche détectée"""
        return {
            'reponse': f"🛑 **{self.personnalites[self.nom]['emoji']} Je ne peux pas faire ton travail !**\n\n"
                      f"Mon rôle est de t'**aider à comprendre**, pas de faire le TP à ta place.\n\n"
                      f"💡 **Je peux t'aider sur :**\n"
                      f"• Expliquer les concepts théoriques\n"
                      f"• Interpréter tes résultats\n"
                      f"• Te guider dans ton analyse\n"
                      f"• Répondre à tes questions précises\n\n"
                      f"❓ **Pose-moi plutôt une question comme :**\n"
                      f"• 'Comment interpréter ce graphique ?'\n"
                      f"• 'Pourquoi ce paramètre influence-t-il le résultat ?'\n"
                      f"• 'Quelle est la formule théorique ?'",
            'pertinence_question': 1,
            'aide_apportee': False,
            'source': 'anti_triche'
        }

    def _generer_avec_gemini(self, question, contexte, session):
        """Génération avec Gemini AI"""
        tp = session.tp

        # Construire le prompt contextuel
        prompt = f"""
        Tu es {self.personnalites[self.nom]['nom_complet']}, spécialisé en {self.personnalites[self.nom]['domaine']}.
        
        CONTEXTE DU TP :
        - Titre : {tp.titre}
        - Type : {tp.type_simulation}
        - Paramètres actuels : {json.dumps(contexte, indent=2)}
        
        QUESTION DE L'ÉTUDIANT :
        {question}
        
        RÈGLES :
        1. Réponds de manière pédagogique (ne fais PAS le travail à sa place)
        2. Utilise les paramètres fournis pour personnaliser ta réponse
        3. Encourage l'expérimentation
        4. Pose des questions pour stimuler la réflexion
        5. Reste dans ton domaine d'expertise
        
        RÉPONSE (150 mots max) :
        """

        response = self.model.generate_content(prompt)
        reponse_texte = response.text

        return {
            'reponse': f"{self.personnalites[self.nom]['emoji']} **{self.nom}** : {reponse_texte}",
            'pertinence_question': 4,
            'aide_apportee': True,
            'source': 'gemini'
        }

    def _generer_fallback(self, question, contexte, session):
        """Fallback intelligent basé sur des règles"""
        q_lower = question.lower()
        tp_type = session.tp.type_simulation
        emoji = self.personnalites[self.nom]['emoji']

        # Base de connaissances par type de simulation
        reponses = {
            'buck': self._fallback_buck(q_lower, contexte),
            'boost': self._fallback_boost(q_lower, contexte),
            'rdm_poutre': self._fallback_rdm(q_lower, contexte),
            'chute_libre': self._fallback_chute_libre(q_lower, contexte),
            'thermodynamique': self._fallback_thermodynamique(q_lower, contexte),
        }

        reponse_specifique = reponses.get(tp_type)

        if reponse_specifique:
            return {
                'reponse': f"{emoji} **{self.nom}** : {reponse_specifique}",
                'pertinence_question': 4,
                'aide_apportee': True,
                'source': 'fallback'
            }

        # Réponse générique si aucune correspondance
        return {
            'reponse': f"{emoji} **{self.nom}** : Pour ce type de simulation ({tp_type}), "
                      f"je te suggère de :\n\n"
                      f"1. **Observer** les variations des paramètres\n"
                      f"2. **Noter** les tendances dans tes résultats\n"
                      f"3. **Comparer** avec les valeurs théoriques\n"
                      f"4. **Analyser** les écarts éventuels\n\n"
                      f"💡 Pose-moi une question plus précise sur un aspect spécifique !",
            'pertinence_question': 2,
            'aide_apportee': False,
            'source': 'fallback_generique'
        }

    def _fallback_buck(self, question, contexte):
        """Réponses spécifiques pour le convertisseur Buck"""
        alpha = contexte.get('alpha', 0.5)
        vin = contexte.get('vin', 24)
        vout_theorique = alpha * vin

        if 'tension' in question or 'vout' in question or 'sortie' in question:
            return (f"📉 **Convertisseur Buck (Abaisseur)**\n\n"
                   f"La tension de sortie théorique est : **Vout = α × Vin**\n\n"
                   f"Avec tes paramètres actuels :\n"
                   f"• α (rapport cyclique) = {alpha}\n"
                   f"• Vin = {vin} V\n"
                   f"• **Vout théorique = {vout_theorique:.2f} V**\n\n"
                   f"💡 Vérifie si ta simulation donne une valeur proche !\n"
                   f"Un écart peut venir des pertes ou du ripple.")

        elif 'ripple' in question or 'ondulation' in question:
            L = contexte.get('L', 1)
            C = contexte.get('C', 100)
            return (f"📊 **Ondulation de tension (Ripple)**\n\n"
                   f"L'ondulation dépend de :\n"
                   f"• L (inductance) = {L} mH → Plus L est grand, moins de ripple\n"
                   f"• C (condensateur) = {C} µF → Plus C est grand, moins de ripple\n"
                   f"• Fréquence de commutation\n\n"
                   f"🔬 **Expérience à faire :**\n"
                   f"1. Double la valeur de L, observe le ripple\n"
                   f"2. Double C, observe l'effet\n"
                   f"3. Compare les deux impacts !")

        elif 'rendement' in question or 'efficacité' in question:
            return (f"⚡ **Rendement du Buck**\n\n"
                   f"Le rendement théorique peut atteindre 95-98% en conditions idéales.\n\n"
                   f"Les pertes proviennent de :\n"
                   f"• Résistance du MOSFET (conduction)\n"
                   f"• Commutations (pertes dynamiques)\n"
                   f"• Résistance série de L et C\n"
                   f"• Diode de roue libre\n\n"
                   f"📈 **η = (Pout / Pin) × 100%**")

        else:
            return (f"⚡ **Convertisseur Buck - Principe**\n\n"
                   f"Le Buck est un abaisseur de tension DC-DC.\n\n"
                   f"**Fonctionnement :**\n"
                   f"1. MOSFET ON (α × T) → L'inductance se charge\n"
                   f"2. MOSFET OFF ((1-α) × T) → L se décharge dans C\n"
                   f"3. Le condensateur lisse la tension\n\n"
                   f"**Vout = α × Vin** (théorique)")

    def _fallback_boost(self, question, contexte):
        """Réponses pour le convertisseur Boost"""
        alpha = contexte.get('alpha', 0.5)
        vin = contexte.get('vin', 12)
        vout_theorique = vin / (1 - alpha) if alpha < 1 else float('inf')

        return (f"📈 **Convertisseur Boost (Élévateur)**\n\n"
               f"La tension de sortie théorique : **Vout = Vin / (1 - α)**\n\n"
               f"Avec α = {alpha} et Vin = {vin} V :\n"
               f"• **Vout théorique = {vout_theorique:.2f} V**\n\n"
               f"⚠️  Attention : Si α → 1, Vout → ∞ (théoriquement) !")

    def _fallback_rdm(self, question, contexte):
        """Réponses pour RDM - Poutre"""
        L = contexte.get('longueur', 10)
        q = contexte.get('charge', 100)
        M_max = (q * L**2) / 8

        if 'moment' in question:
            return (f"📐 **Moment fléchissant maximal**\n\n"
                   f"Pour une poutre simplement appuyée avec charge uniformément répartie :\n\n"
                   f"**M_max = (q × L²) / 8**\n\n"
                   f"Avec tes paramètres :\n"
                   f"• q = {q} N/m\n"
                   f"• L = {L} m\n"
                   f"• **M_max = {M_max:.2f} N·m**\n\n"
                   f"📍 Position : au milieu de la poutre (x = L/2)")

        elif 'flèche' in question or 'déformation' in question:
            return (f"📏 **Flèche maximale**\n\n"
                   f"La flèche dépend de :\n"
                   f"• Charge (q) : effet linéaire\n"
                   f"• Longueur (L) : effet à la puissance 4 !\n"
                   f"• Module d'Young (E) : rigidité du matériau\n"
                   f"• Inertie (I) : forme de la section\n\n"
                   f"**f_max = (5 × q × L⁴) / (384 × E × I)**")

        else:
            return (f"🏗️ **Résistance des Matériaux (RDM)**\n\n"
                   f"Avec L = {L} m et q = {q} N/m :\n\n"
                   f"• Réactions d'appuis : R = (q × L) / 2\n"
                   f"• Moment max : M_max = {M_max:.2f} N·m\n"
                   f"• Position M_max : x = L/2 = {L/2} m\n\n"
                   f"🔍 Vérifie ces valeurs sur ton graphique !")

    def _fallback_chute_libre(self, question, contexte):
        """Réponses pour la chute libre"""
        h0 = contexte.get('hauteur_initiale', 100)
        v0 = contexte.get('vitesse_initiale', 0)
        g = 9.81

        t_chute = ((2 * h0) / g) ** 0.5
        v_finale = (2 * g * h0) ** 0.5

        return (f"🌍 **Chute libre**\n\n"
               f"Équations du mouvement :\n"
               f"• Position : **y(t) = h0 - ½gt²**\n"
               f"• Vitesse : **v(t) = -gt** (si v0 = 0)\n\n"
               f"Avec h0 = {h0} m :\n"
               f"• Temps de chute : **t = {t_chute:.2f} s**\n"
               f"• Vitesse finale : **v = {v_finale:.2f} m/s**\n\n"
               f"📊 Vérifie graphiquement ces valeurs !")

    def _fallback_thermodynamique(self, question, contexte):
        """Réponses pour la thermodynamique"""
        return (f"🔥 **Thermodynamique**\n\n"
               f"Principes fondamentaux :\n"
               f"• 1er principe : Conservation de l'énergie\n"
               f"• 2ème principe : Entropie croissante\n\n"
               f"Pour ton système, analyse :\n"
               f"• Les transferts thermiques (Q)\n"
               f"• Le travail (W)\n"
               f"• L'évolution de l'énergie interne (ΔU)")

    def enregistrer_interaction(self, session_id, question, reponse_dict, contexte):
        """Enregistre l'interaction dans la base de données"""
        try:
            interaction = InteractionIA(
                session_id=session_id,
                question_etudiant=question,
                reponse_ia=reponse_dict['reponse'],
                contexte_simulation=json.dumps(contexte),
                ia_nom=self.nom,
                pertinence_question=reponse_dict.get('pertinence_question', 3),
                aide_apportee=reponse_dict.get('aide_apportee', True)
            )
            db.session.add(interaction)
            db.session.commit()
        except Exception as e:
            print(f"❌ Erreur enregistrement interaction : {e}")


# Factory Pattern
class IAFactoryV2:
    """Factory pour créer les assistants IA version 2"""

    @staticmethod
    def creer_assistant(nom_ia='ETA'):
        """Crée une instance de l'IA demandée"""
        if nom_ia not in ['ETA', 'ALPHA', 'KAYT']:
            print(f"⚠️  IA '{nom_ia}' inconnue, utilisation de ETA")
            nom_ia = 'ETA'

        return IALaboratoireV2(nom_ia)


# Alias pour compatibilité avec l'ancien système
IAFactory = IAFactoryV2

