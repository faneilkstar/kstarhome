"""
Service d'IA pour générer des rapports et statistiques pour les enseignants
Utilise Google Gemini pour l'analyse avancée
Créé par : Ing. KOISSI-ZO Tonyi Constantin
Date : 11 Février 2026
"""

import os
from datetime import datetime
import numpy as np
from scipy import stats as scipy_stats
try:
    import google.generativeai as genai
    GEMINI_DISPONIBLE = True
except ImportError:
    GEMINI_DISPONIBLE = False


class RapportIA:
    """Génère des rapports détaillés avec analyse IA pour les enseignants"""

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

    def analyser_cours(self, ue, notes, absences, inscriptions):
        """
        Analyse complète d'un cours avec statistiques descriptives et inférentielles

        Args:
            ue: Instance de l'UE
            notes: Liste des notes des étudiants
            absences: Liste des absences
            inscriptions: Liste des inscriptions UE

        Returns:
            dict: Rapport complet avec statistiques et analyse IA
        """
        # STATISTIQUES DESCRIPTIVES
        stats_desc = self._calculer_stats_descriptives(notes)

        # STATISTIQUES INFÉRENTIELLES
        stats_inf = self._calculer_stats_inferentielles(notes, absences)

        # ANALYSE AVEC IA GEMINI
        analyse_ia = self._generer_analyse_ia(ue, stats_desc, stats_inf, absences, inscriptions)

        return {
            'descriptives': stats_desc,
            'inferentielles': stats_inf,
            'analyse_ia': analyse_ia,
            'recommandations': analyse_ia.get('recommandations', []),
            'points_forts': analyse_ia.get('points_forts', []),
            'axes_amelioration': analyse_ia.get('axes_amelioration', [])
        }

    def analyser_tp(self, tp, sessions):
        """
        Analyse les résultats d'un TP virtuel

        Args:
            tp: Instance du TP
            sessions: Liste des sessions terminées

        Returns:
            dict: Rapport d'analyse du TP
        """
        if not sessions:
            return {
                'nb_sessions': 0,
                'message': 'Aucune session terminée pour ce TP'
            }

        # Statistiques des sessions
        notes_ia = [s.note_ia for s in sessions if s.note_ia is not None]
        durees = [s.duree_minutes for s in sessions if s.duree_minutes]
        nb_mesures = [s.nb_mesures for s in sessions if s.nb_mesures]

        stats_tp = {
            'nb_sessions': len(sessions),
            'taux_reussite': len([n for n in notes_ia if n >= 10]) / len(notes_ia) * 100 if notes_ia else 0,
            'note_moyenne': np.mean(notes_ia) if notes_ia else 0,
            'note_mediane': np.median(notes_ia) if notes_ia else 0,
            'note_min': min(notes_ia) if notes_ia else 0,
            'note_max': max(notes_ia) if notes_ia else 0,
            'duree_moyenne': np.mean(durees) if durees else 0,
            'nb_mesures_moyen': np.mean(nb_mesures) if nb_mesures else 0
        }

        # Analyse IA
        analyse_ia_tp = self._generer_analyse_ia_tp(tp, stats_tp, sessions)

        return {
            **stats_tp,
            'analyse_ia': analyse_ia_tp,
            'recommandations': analyse_ia_tp.get('recommandations', [])
        }

    def _calculer_stats_descriptives(self, notes):
        """Calcule les statistiques descriptives de base"""
        valeurs_notes = [n.note for n in notes if n.note is not None]

        if not valeurs_notes:
            return {
                'nb_notes': 0,
                'moyenne': 0,
                'mediane': 0,
                'mode': 0,
                'ecart_type': 0,
                'variance': 0,
                'min': 0,
                'max': 0,
                'etendue': 0,
                'q1': 0,
                'q3': 0,
                'iqr': 0,
                'taux_reussite': 0
            }

        # Calculs statistiques
        moyenne = np.mean(valeurs_notes)
        mediane = np.median(valeurs_notes)
        ecart_type = np.std(valeurs_notes, ddof=1) if len(valeurs_notes) > 1 else 0
        variance = np.var(valeurs_notes, ddof=1) if len(valeurs_notes) > 1 else 0

        # Quartiles
        q1 = np.percentile(valeurs_notes, 25)
        q3 = np.percentile(valeurs_notes, 75)
        iqr = q3 - q1

        # Taux de réussite
        nb_reussis = len([n for n in valeurs_notes if n >= 10])
        taux_reussite = (nb_reussis / len(valeurs_notes)) * 100

        return {
            'nb_notes': len(valeurs_notes),
            'moyenne': round(moyenne, 2),
            'mediane': round(mediane, 2),
            'ecart_type': round(ecart_type, 2),
            'variance': round(variance, 2),
            'min': min(valeurs_notes),
            'max': max(valeurs_notes),
            'etendue': max(valeurs_notes) - min(valeurs_notes),
            'q1': round(q1, 2),
            'q3': round(q3, 2),
            'iqr': round(iqr, 2),
            'taux_reussite': round(taux_reussite, 2),
            'nb_reussis': nb_reussis,
            'nb_ajournes': len(valeurs_notes) - nb_reussis
        }

    def _calculer_stats_inferentielles(self, notes, absences):
        """Calcule les statistiques inférentielles avancées"""
        valeurs_notes = [n.note for n in notes if n.note is not None]

        if len(valeurs_notes) < 2:
            return {'correlation_absences_notes': None, 'message': 'Données insuffisantes'}

        # Corrélation absences-notes
        nb_absences_par_etudiant = {}
        for absence in absences:
            if absence.etudiant_id not in nb_absences_par_etudiant:
                nb_absences_par_etudiant[absence.etudiant_id] = 0
            nb_absences_par_etudiant[absence.etudiant_id] += 1

        # Associer notes et absences
        notes_avec_absences = []
        absences_associees = []

        for note in notes:
            if note.note is not None:
                notes_avec_absences.append(note.note)
                absences_associees.append(nb_absences_par_etudiant.get(note.etudiant_id, 0))

        correlation = None
        p_value = None
        interpretation = "Non calculable"

        if len(notes_avec_absences) >= 3 and any(absences_associees):
            try:
                correlation, p_value = scipy_stats.pearsonr(notes_avec_absences, absences_associees)

                # Interprétation
                if p_value < 0.05:
                    if correlation < -0.5:
                        interpretation = "Forte corrélation négative : les absences impactent significativement les notes"
                    elif correlation < -0.3:
                        interpretation = "Corrélation négative modérée : les absences ont un impact sur les notes"
                    elif correlation < 0:
                        interpretation = "Faible corrélation négative : peu d'impact des absences"
                    else:
                        interpretation = "Pas de corrélation significative"
                else:
                    interpretation = "Corrélation non significative statistiquement (p > 0.05)"
            except:
                interpretation = "Erreur de calcul"

        # Test de normalité (Shapiro-Wilk)
        normalite = None
        normalite_p = None
        if len(valeurs_notes) >= 3:
            try:
                normalite, normalite_p = scipy_stats.shapiro(valeurs_notes)
                normalite_interpretation = "Distribution normale" if normalite_p > 0.05 else "Distribution non normale"
            except:
                normalite_interpretation = "Non testable"
        else:
            normalite_interpretation = "Données insuffisantes"

        return {
            'correlation_absences_notes': round(correlation, 3) if correlation else None,
            'p_value': round(p_value, 4) if p_value else None,
            'interpretation_correlation': interpretation,
            'test_normalite_p': round(normalite_p, 4) if normalite_p else None,
            'normalite_interpretation': normalite_interpretation
        }

    def _generer_analyse_ia(self, ue, stats_desc, stats_inf, absences, inscriptions):
        """Génère une analyse détaillée avec Gemini"""

        if not self.ia_activee:
            return self._analyse_sans_ia(stats_desc, stats_inf)

        # Préparer le prompt pour Gemini
        prompt = f"""Tu es un assistant pédagogique expert pour un enseignant d'école polytechnique.

COURS À ANALYSER :
- UE : {ue.intitule}
- Code : {ue.code_ue}
- Crédits : {ue.credits}
- Coefficient : {ue.coefficient}

STATISTIQUES DESCRIPTIVES :
- Nombre d'étudiants : {stats_desc['nb_notes']}
- Moyenne : {stats_desc['moyenne']}/20
- Médiane : {stats_desc['mediane']}/20
- Écart-type : {stats_desc['ecart_type']}
- Note min : {stats_desc['min']}/20
- Note max : {stats_desc['max']}/20
- Taux de réussite : {stats_desc['taux_reussite']}%
- Réussis : {stats_desc['nb_reussis']}
- Ajournés : {stats_desc['nb_ajournes']}

STATISTIQUES INFÉRENTIELLES :
- Corrélation absences-notes : {stats_inf.get('correlation_absences_notes', 'N/A')}
- Interprétation : {stats_inf.get('interpretation_correlation', 'N/A')}
- Test de normalité : {stats_inf.get('normalite_interpretation', 'N/A')}

NOMBRE D'ABSENCES : {len(absences)}

MISSION :
1. Analyser les performances globales du cours
2. Identifier les POINTS FORTS (3-4 éléments)
3. Identifier les AXES D'AMÉLIORATION (3-4 éléments)
4. Donner des RECOMMANDATIONS CONCRÈTES (4-5 actions)
5. Expliquer POURQUOI les étudiants ont réussi ou échoué

FORMAT DE RÉPONSE (RESPECTER EXACTEMENT) :
SYNTHÈSE: [Résumé en 2-3 phrases de la situation globale]

POINTS FORTS:
- [Point fort 1]
- [Point fort 2]
- [Point fort 3]

AXES D'AMÉLIORATION:
- [Axe 1]
- [Axe 2]
- [Axe 3]

RECOMMANDATIONS:
- [Recommandation 1]
- [Recommandation 2]
- [Recommandation 3]
- [Recommandation 4]

POURQUOI CES RÉSULTATS:
[Explication détaillée des facteurs ayant conduit à ces résultats - 3-4 phrases]

⚠️ Sois CONSTRUCTIF et PÉDAGOGIQUE dans ton analyse.
"""

        try:
            response = self.model.generate_content(prompt)
            return self._parser_analyse_ia(response.text)
        except Exception as e:
            print(f"⚠️  Erreur Gemini : {e}")
            return self._analyse_sans_ia(stats_desc, stats_inf)

    def _generer_analyse_ia_tp(self, tp, stats_tp, sessions):
        """Génère une analyse détaillée pour un TP virtuel"""

        if not self.ia_activee:
            return {
                'synthese': f"TP {tp.titre} : {stats_tp['nb_sessions']} sessions, moyenne {stats_tp['note_moyenne']:.2f}/20",
                'recommandations': ["Activer Gemini pour une analyse approfondie"]
            }

        prompt = f"""Tu es un assistant pédagogique expert pour analyser les TPs virtuels.

TP À ANALYSER :
- Titre : {tp.titre}
- Type : {tp.type_simulation}
- IA assistant : {tp.ia_nom}

STATISTIQUES :
- Nombre de sessions : {stats_tp['nb_sessions']}
- Taux de réussite : {stats_tp['taux_reussite']:.1f}%
- Note moyenne : {stats_tp['note_moyenne']:.2f}/20
- Note médiane : {stats_tp['note_mediane']:.2f}/20
- Note min : {stats_tp['note_min']}/20
- Note max : {stats_tp['note_max']}/20
- Durée moyenne : {stats_tp['duree_moyenne']:.1f} minutes
- Nombre de mesures moyen : {stats_tp['nb_mesures_moyen']:.1f}

MISSION :
1. Analyser les performances au TP
2. Identifier ce qui a bien fonctionné
3. Identifier les difficultés des étudiants
4. Donner des recommandations pour améliorer le TP

FORMAT DE RÉPONSE (RESPECTER EXACTEMENT) :
SYNTHÈSE: [Résumé en 2 phrases]

POINTS POSITIFS:
- [Point 1]
- [Point 2]
- [Point 3]

DIFFICULTÉS OBSERVÉES:
- [Difficulté 1]
- [Difficulté 2]

RECOMMANDATIONS:
- [Recommandation 1]
- [Recommandation 2]
- [Recommandation 3]
"""

        try:
            response = self.model.generate_content(prompt)
            return self._parser_analyse_ia_tp(response.text)
        except Exception as e:
            print(f"⚠️  Erreur Gemini : {e}")
            return {
                'synthese': f"TP {tp.titre} : {stats_tp['nb_sessions']} sessions",
                'recommandations': ["Erreur IA, analyse manuelle requise"]
            }

    def _parser_analyse_ia(self, texte):
        """Parse la réponse de Gemini pour l'analyse de cours"""
        lignes = texte.split('\n')

        resultat = {
            'synthese': '',
            'points_forts': [],
            'axes_amelioration': [],
            'recommandations': [],
            'pourquoi': ''
        }

        section_actuelle = None

        for ligne in lignes:
            ligne = ligne.strip()

            if ligne.startswith("SYNTHÈSE:") or ligne.startswith("SYNTHESE:"):
                resultat['synthese'] = ligne.split(":", 1)[1].strip()

            elif ligne.startswith("POINTS FORTS:"):
                section_actuelle = 'points_forts'
            elif ligne.startswith("AXES D'AMÉLIORATION:") or ligne.startswith("AXES D'AMELIORATION:"):
                section_actuelle = 'axes_amelioration'
            elif ligne.startswith("RECOMMANDATIONS:"):
                section_actuelle = 'recommandations'
            elif ligne.startswith("POURQUOI CES RÉSULTATS:") or ligne.startswith("POURQUOI CES RESULTATS:"):
                section_actuelle = 'pourquoi'

            elif ligne.startswith("-") and section_actuelle in ['points_forts', 'axes_amelioration', 'recommandations']:
                item = ligne.lstrip("- ").strip()
                if item:
                    resultat[section_actuelle].append(item)

            elif section_actuelle == 'pourquoi' and ligne and not ligne.startswith("-"):
                resultat['pourquoi'] += ligne + " "

        return resultat

    def _parser_analyse_ia_tp(self, texte):
        """Parse la réponse de Gemini pour l'analyse de TP"""
        lignes = texte.split('\n')

        resultat = {
            'synthese': '',
            'points_positifs': [],
            'difficultes': [],
            'recommandations': []
        }

        section_actuelle = None

        for ligne in lignes:
            ligne = ligne.strip()

            if ligne.startswith("SYNTHÈSE:") or ligne.startswith("SYNTHESE:"):
                resultat['synthese'] = ligne.split(":", 1)[1].strip()

            elif ligne.startswith("POINTS POSITIFS:"):
                section_actuelle = 'points_positifs'
            elif ligne.startswith("DIFFICULTÉS OBSERVÉES:") or ligne.startswith("DIFFICULTES OBSERVEES:"):
                section_actuelle = 'difficultes'
            elif ligne.startswith("RECOMMANDATIONS:"):
                section_actuelle = 'recommandations'

            elif ligne.startswith("-") and section_actuelle:
                item = ligne.lstrip("- ").strip()
                if item:
                    resultat[section_actuelle].append(item)

        return resultat

    def _analyse_sans_ia(self, stats_desc, stats_inf):
        """Analyse basique sans IA (fallback)"""
        synthese = f"Cours avec {stats_desc['nb_notes']} étudiants, moyenne {stats_desc['moyenne']}/20, taux de réussite {stats_desc['taux_reussite']:.1f}%"

        points_forts = []
        axes_amelioration = []

        # Analyse automatique
        if stats_desc['taux_reussite'] >= 80:
            points_forts.append("Excellent taux de réussite, objectifs pédagogiques atteints")
        elif stats_desc['taux_reussite'] >= 60:
            points_forts.append("Bon taux de réussite global")
        else:
            axes_amelioration.append("Taux de réussite faible, revoir la pédagogie ou le contenu")

        if stats_desc['ecart_type'] < 3:
            points_forts.append("Groupe homogène (faible écart-type)")
        elif stats_desc['ecart_type'] > 5:
            axes_amelioration.append("Groupe hétérogène, prévoir du soutien pour les plus faibles")

        if stats_desc['moyenne'] >= 12:
            points_forts.append("Bonne moyenne générale")
        elif stats_desc['moyenne'] < 10:
            axes_amelioration.append("Moyenne faible, revoir les méthodes d'enseignement")

        # Corrélation absences
        if stats_inf.get('correlation_absences_notes'):
            corr = stats_inf['correlation_absences_notes']
            if corr < -0.5:
                axes_amelioration.append("Forte corrélation absences-notes : renforcer la présence obligatoire")

        return {
            'synthese': synthese,
            'points_forts': points_forts,
            'axes_amelioration': axes_amelioration,
            'recommandations': [
                "Analyser les copies des étudiants en échec",
                "Organiser des séances de soutien si nécessaire",
                "Vérifier l'adéquation du cours avec le niveau"
            ],
            'pourquoi': "Analyse automatique basique. Activer Gemini pour une analyse approfondie."
        }

    def generer_rapport_pdf(self, ue, rapport, enseignant):
        """
        Génère un rapport PDF détaillé avec graphiques
        À implémenter avec ReportLab
        """
        # TODO: Implémenter avec ReportLab
        pass

