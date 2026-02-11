"""
Service d'IA pour la validation automatique des inscriptions avec Gemini
Créé par : Ing. KOISSI-ZO Tonyi Constantin
Date : 11 Février 2026
"""

import os
from datetime import datetime, timedelta
try:
    import google.generativeai as genai
    GEMINI_DISPONIBLE = True
except ImportError:
    GEMINI_DISPONIBLE = False


class ValidationIA:
    """IA pour valider automatiquement les inscriptions d'étudiants"""

    MOYENNE_ELIMINATOIRE = 12.0  # Moyenne minimale pour être accepté

    def __init__(self):
        """Initialiser l'IA avec la clé API Gemini"""
        self.ia_activee = False

        if GEMINI_DISPONIBLE:
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key and api_key.strip():
                try:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-pro')
                    self.ia_activee = True
                except Exception as e:
                    print(f"⚠️  Erreur configuration Gemini : {e}")

    def evaluer_inscription(self, etudiant):
        """
        Évalue une inscription d'étudiant avec l'IA Gemini

        Args:
            etudiant: Instance du modèle Etudiant

        Returns:
            dict: {
                'decision': 'accepte' ou 'refuse',
                'motif': 'Raison détaillée',
                'score': Note sur 100,
                'recommandations': Liste de recommandations
            }
        """
        # Récupérer les données de l'étudiant
        moyenne_bac = etudiant.moyenne_bac or 0
        moyenne_licence = etudiant.moyenne_licence or 0
        filiere = etudiant.filiere_objet.nom_filiere if etudiant.filiere_objet else "Non spécifiée"
        cycle = etudiant.filiere_objet.cycle if etudiant.filiere_objet else "Licence"

        # ⚠️ IMPORTANT : Tous les étudiants commencent TOUJOURS en 1ère année
        # Quelle que soit la filière (Licence ou Master)
        moyenne_pertinente = moyenne_licence if cycle == "Master" else moyenne_bac
        annee_inscription = 1  # TOUJOURS 1ère année au début

        # Décision basique sans IA
        if not self.ia_activee:
            return self._evaluer_sans_ia(etudiant, moyenne_pertinente, cycle)

        # Évaluation avec IA Gemini
        return self._evaluer_avec_gemini(etudiant, moyenne_pertinente, filiere, cycle)

    def _evaluer_sans_ia(self, etudiant, moyenne, cycle):
        """Évaluation basique sans IA (fallback)"""
        decision = "accepte" if moyenne >= self.MOYENNE_ELIMINATOIRE else "refuse"

        if decision == "accepte":
            motif = f"Moyenne de {moyenne}/20 conforme aux critères d'admission (≥ {self.MOYENNE_ELIMINATOIRE}/20)"
            recommandations = [
                "Inscription validée selon les critères académiques standards",
                "Poursuivre les démarches administratives"
            ]
            score = min(100, int((moyenne / 20) * 100))
        else:
            motif = f"Moyenne de {moyenne}/20 inférieure au seuil requis ({self.MOYENNE_ELIMINATOIRE}/20)"
            recommandations = [
                "Renforcer les connaissances fondamentales",
                "Envisager une mise à niveau avant réinscription"
            ]
            score = int((moyenne / 20) * 100)

        return {
            'decision': decision,
            'motif': motif,
            'score': score,
            'recommandations': recommandations,
            'methode': 'basique'
        }

    def _evaluer_avec_gemini(self, etudiant, moyenne, filiere, cycle):
        """Évaluation intelligente avec Gemini"""

        # Préparer le prompt pour Gemini
        prompt = f"""Tu es un assistant d'aide à la décision pour une école polytechnique.

DOSSIER À ÉVALUER :
- Nom : {etudiant.nom} {etudiant.prenom}
- Filière demandée : {filiere} ({cycle})
- Moyenne {"Licence" if cycle == "Master" else "BAC"} : {moyenne}/20
- Nationalité : {etudiant.nationalite or "Non spécifiée"}
- Âge : {self._calculer_age(etudiant.date_naissance)} ans

CRITÈRES D'ADMISSION :
- Moyenne éliminatoire : {self.MOYENNE_ELIMINATOIRE}/20
- La décision finale doit être "ACCEPTÉ" ou "REFUSÉ"

MISSION :
1. Évaluer ce dossier selon les critères académiques
2. Donner une décision claire (ACCEPTÉ ou REFUSÉ)
3. Justifier en 2-3 phrases courtes
4. Donner un score sur 100
5. Proposer 2-3 recommandations

FORMAT DE RÉPONSE (RESPECTER EXACTEMENT) :
DÉCISION: [ACCEPTÉ ou REFUSÉ]
SCORE: [nombre entre 0 et 100]
MOTIF: [Justification en 2-3 phrases]
RECOMMANDATIONS:
- [Recommandation 1]
- [Recommandation 2]
- [Recommandation 3]

⚠️  IMPORTANT : Sois objectif et base-toi uniquement sur la moyenne par rapport au seuil de {self.MOYENNE_ELIMINATOIRE}/20.
"""

        try:
            # Appeler Gemini
            response = self.model.generate_content(prompt)
            texte_reponse = response.text

            # Parser la réponse
            resultat = self._parser_reponse_gemini(texte_reponse, moyenne)
            resultat['methode'] = 'gemini'
            return resultat

        except Exception as e:
            print(f"⚠️  Erreur Gemini, fallback sur évaluation basique : {e}")
            return self._evaluer_sans_ia(etudiant, moyenne, cycle)

    def _parser_reponse_gemini(self, texte, moyenne):
        """Parse la réponse de Gemini"""
        lignes = texte.split('\n')

        decision = "refuse"
        score = int((moyenne / 20) * 100)
        motif = "Évaluation automatique en cours"
        recommandations = []

        for ligne in lignes:
            ligne = ligne.strip()

            if ligne.startswith("DÉCISION:") or ligne.startswith("DECISION:"):
                if "ACCEPTÉ" in ligne.upper() or "ACCEPTE" in ligne.upper():
                    decision = "accepte"
                elif "REFUSÉ" in ligne.upper() or "REFUSE" in ligne.upper():
                    decision = "refuse"

            elif ligne.startswith("SCORE:"):
                try:
                    score = int(ligne.split(":")[1].strip())
                except:
                    pass

            elif ligne.startswith("MOTIF:"):
                motif = ligne.split(":", 1)[1].strip()

            elif ligne.startswith("-") and "RECOMMANDATIONS" not in ligne:
                rec = ligne.lstrip("- ").strip()
                if rec:
                    recommandations.append(rec)

        # Validation finale : forcer le refus si moyenne < seuil
        if moyenne < self.MOYENNE_ELIMINATOIRE:
            decision = "refuse"

        return {
            'decision': decision,
            'motif': motif,
            'score': score,
            'recommandations': recommandations[:3]  # Max 3 recommandations
        }

    def _calculer_age(self, date_naissance):
        """Calcule l'âge à partir de la date de naissance"""
        if not date_naissance:
            return "N/A"

        aujourd_hui = datetime.now()
        age = aujourd_hui.year - date_naissance.year

        # Ajuster si l'anniversaire n'est pas encore passé cette année
        if (aujourd_hui.month, aujourd_hui.day) < (date_naissance.month, date_naissance.day):
            age -= 1

        return age

    @staticmethod
    def programmer_validation_automatique(etudiant, delai_minutes=30):
        """
        Programme une validation automatique après un délai

        Args:
            etudiant: Instance Etudiant
            delai_minutes: Délai en minutes (défaut 30)

        Returns:
            datetime: Date/heure de validation prévue
        """
        date_validation = datetime.now() + timedelta(minutes=delai_minutes)

        # TODO: Implémenter avec Celery ou APScheduler pour la validation différée
        # Pour l'instant, on retourne juste la date prévue

        return date_validation

