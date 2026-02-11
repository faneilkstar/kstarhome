"""
Système d'entraînement et fine-tuning de l'IA
Améliore l'IA avec les données réelles du laboratoire
"""

import json
import os
from datetime import datetime, timedelta
from app import db
from app.models import InteractionIA, SessionTP, TP, Etudiant


class IATrainingService:
    """Service d'entraînement de l'IA"""

    def __init__(self):
        self.training_data_dir = 'data/ia_training'
        os.makedirs(self.training_data_dir, exist_ok=True)

    def collecter_donnees_entrainement(self, jours=30):
        """
        Collecte les données d'interactions pour l'entraînement

        Args:
            jours: Nombre de jours d'historique à collecter

        Returns:
            list: Données formatées pour l'entraînement
        """
        date_limite = datetime.utcnow() - timedelta(days=jours)

        # Récupérer toutes les interactions de qualité
        interactions = InteractionIA.query.filter(
            InteractionIA.timestamp >= date_limite,
            InteractionIA.pertinence_question >= 3  # Questions pertinentes seulement
        ).all()

        training_data = []

        for interaction in interactions:
            session = interaction.session_tp
            if not session:
                continue

            # Contexte enrichi
            contexte = {
                'type_simulation': session.tp.type_simulation,
                'ia_nom': interaction.ia_nom,
                'parametres_simulation': json.loads(
                    interaction.contexte_simulation) if interaction.contexte_simulation else {},
                'niveau_etudiant': self._estimer_niveau(session.etudiant),
                'phase_tp': self._determiner_phase(session)
            }

            # Format pour fine-tuning
            training_sample = {
                'context': json.dumps(contexte, ensure_ascii=False),
                'question': interaction.question_etudiant,
                'reponse': interaction.reponse_ia,
                'qualite': interaction.pertinence_question,
                'aide_effective': interaction.aide_apportee,
                'timestamp': interaction.timestamp.isoformat()
            }

            training_data.append(training_sample)

        return training_data

    def exporter_dataset_finetuning(self, format='jsonl'):
        """
        Exporte les données au format pour fine-tuning

        Args:
            format: 'jsonl' (OpenAI), 'csv', ou 'json'

        Returns:
            str: Chemin du fichier exporté
        """
        training_data = self.collecter_donnees_entrainement(jours=90)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format == 'jsonl':
            # Format OpenAI/Gemini fine-tuning
            filepath = os.path.join(self.training_data_dir, f'training_data_{timestamp}.jsonl')

            with open(filepath, 'w', encoding='utf-8') as f:
                for sample in training_data:
                    # Format ChatGPT fine-tuning
                    formatted = {
                        'messages': [
                            {
                                'role': 'system',
                                'content': f"Tu es {sample['context']}"
                            },
                            {
                                'role': 'user',
                                'content': sample['question']
                            },
                            {
                                'role': 'assistant',
                                'content': sample['reponse']
                            }
                        ]
                    }
                    f.write(json.dumps(formatted, ensure_ascii=False) + '\n')

        elif format == 'csv':
            import csv
            filepath = os.path.join(self.training_data_dir, f'training_data_{timestamp}.csv')

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['context', 'question', 'reponse', 'qualite'])
                writer.writeheader()
                writer.writerows(training_data)

        else:  # JSON
            filepath = os.path.join(self.training_data_dir, f'training_data_{timestamp}.json')

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Dataset exporté : {filepath} ({len(training_data)} exemples)")
        return filepath

    def analyser_qualite_reponses(self):
        """
        Analyse la qualité des réponses de l'IA

        Returns:
            dict: Statistiques et recommandations
        """
        # Interactions des 30 derniers jours
        date_limite = datetime.utcnow() - timedelta(days=30)
        interactions = InteractionIA.query.filter(
            InteractionIA.timestamp >= date_limite
        ).all()

        if not interactions:
            return {'erreur': 'Pas assez de données'}

        # Calculs statistiques
        total = len(interactions)
        avec_aide = sum(1 for i in interactions if i.aide_apportee)
        pertinentes = sum(1 for i in interactions if i.pertinence_question and i.pertinence_question >= 4)

        # Par type d'IA
        stats_par_ia = {}
        for ia_nom in ['ETA', 'ALPHA', 'KAYT']:
            interactions_ia = [i for i in interactions if i.ia_nom == ia_nom]
            if interactions_ia:
                stats_par_ia[ia_nom] = {
                    'total': len(interactions_ia),
                    'pertinence_moyenne': sum(i.pertinence_question or 0 for i in interactions_ia) / len(
                        interactions_ia),
                    'taux_aide': sum(1 for i in interactions_ia if i.aide_apportee) / len(interactions_ia) * 100
                }

        # Mots-clés les plus fréquents dans les questions
        from collections import Counter
        all_words = []
        for i in interactions:
            words = i.question_etudiant.lower().split()
            all_words.extend([w for w in words if len(w) > 4])

        top_keywords = Counter(all_words).most_common(20)

        # Recommandations
        recommandations = []

        if avec_aide / total < 0.6:
            recommandations.append("❌ Taux d'aide faible : améliorer la pertinence des réponses")

        if pertinentes / total < 0.4:
            recommandations.append("⚠️ Beaucoup de questions peu pertinentes : guider les étudiants")

        for ia_nom, stats in stats_par_ia.items():
            if stats['pertinence_moyenne'] < 3:
                recommandations.append(f"🔧 {ia_nom} : pertinence faible, nécessite fine-tuning")

        return {
            'total_interactions': total,
            'taux_aide': round(avec_aide / total * 100, 2),
            'taux_pertinence': round(pertinentes / total * 100, 2),
            'stats_par_ia': stats_par_ia,
            'top_keywords': top_keywords,
            'recommandations': recommandations
        }

    def generer_prompt_systeme_optimise(self, ia_nom):
        """
        Génère un prompt système optimisé basé sur l'analyse des données

        Args:
            ia_nom: 'ETA', 'ALPHA', ou 'KAYT'

        Returns:
            str: Prompt système optimisé
        """
        # Analyser les interactions passées
        interactions = InteractionIA.query.filter_by(ia_nom=ia_nom).limit(1000).all()

        # Identifier les thèmes récurrents
        themes = self._identifier_themes(interactions)

        # Construire le prompt
        if ia_nom == 'ETA':
            domaine = "Génie Civil"
            exemples_types = themes.get('exemples', [
                "Comment calculer le moment fléchissant ?",
                "Pourquoi ma poutre fléchit autant ?",
                "Quelle est la contrainte maximale ?"
            ])
        elif ia_nom == 'ALPHA':
            domaine = "Mathématiques, Informatique, Logistique"
            exemples_types = themes.get('exemples', [
                "Comment calculer la transformée de Fourier ?",
                "Quel est le point de réapprovisionnement optimal ?",
                "Comment fonctionne l'algorithme de Dijkstra ?"
            ])
        else:  # KAYT
            domaine = "Génie Électrique"
            exemples_types = themes.get('exemples', [
                "Pourquoi mon ondulation est élevée ?",
                "Comment réduire le ripple ?",
                "Quelle valeur de condensateur choisir ?"
            ])

        prompt_optimise = f"""
Tu es {ia_nom}, assistant IA pédagogique expert en {domaine}.

📚 EXPERTISE ACQUISE :
À partir de {len(interactions)} interactions avec des étudiants, tu as appris à :
- Détecter les incompréhensions courantes
- Adapter ton niveau de réponse
- Poser les bonnes questions de guidage

🎯 QUESTIONS FRÉQUENTES QUE TU MAÎTRISES :
{chr(10).join(['- ' + q for q in exemples_types])}

✅ TON APPROCHE PÉDAGOGIQUE :
1. Comprendre le niveau de l'étudiant
2. Identifier la vraie question derrière la question
3. Donner des indices progressifs (JAMAIS la réponse directe)
4. Utiliser des analogies concrètes
5. Encourager l'expérimentation

❌ CE QUE TU NE FAIS JAMAIS :
- Rédiger les conclusions
- Donner les réponses toutes faites
- Faire les calculs complets
- Valider sans vérifier la compréhension

💡 EXEMPLES DE TES MEILLEURES RÉPONSES :
{self._generer_exemples_reponses(interactions)}

Reste toujours bienveillant, socratique et pédagogique ! 🚀
"""

        return prompt_optimise

    def _estimer_niveau(self, etudiant):
        """Estime le niveau de l'étudiant"""
        sessions = SessionTP.query.filter_by(etudiant_id=etudiant.id).all()

        if not sessions:
            return 'debutant'

        notes = [s.note_finale or s.note_ia for s in sessions if s.note_finale or s.note_ia]

        if not notes:
            return 'debutant'

        moyenne = sum(notes) / len(notes)

        if moyenne >= 16:
            return 'avance'
        elif moyenne >= 12:
            return 'intermediaire'
        else:
            return 'debutant'

    def _determiner_phase(self, session):
        """Détermine la phase du TP (début, milieu, fin)"""
        if not session.date_debut:
            return 'debut'

        duree_ecoulee = (datetime.utcnow() - session.date_debut).total_seconds() / 60

        if duree_ecoulee < 15:
            return 'debut'
        elif duree_ecoulee < 45:
            return 'milieu'
        else:
            return 'fin'

    def _identifier_themes(self, interactions):
        """Identifie les thèmes récurrents dans les questions"""
        from collections import Counter

        questions = [i.question_etudiant.lower() for i in interactions[:100]]

        # Mots-clés fréquents
        all_words = []
        for q in questions:
            all_words.extend(q.split())

        top_words = [w for w, _ in Counter(all_words).most_common(10) if len(w) > 4]

        return {
            'mots_cles': top_words,
            'exemples': questions[:5]
        }

    def _generer_exemples_reponses(self, interactions):
        """Génère des exemples de bonnes réponses"""
        # Prendre les meilleures interactions (pertinence >= 4)
        bonnes_interactions = [i for i in interactions if i.pertinence_question and i.pertinence_question >= 4][:3]

        exemples = []
        for i in bonnes_interactions:
            exemples.append(f"""
Q: "{i.question_etudiant}"
R: "{i.reponse_ia[:150]}..."
""")

        return '\n'.join(exemples) if exemples else "Aucun exemple disponible encore."