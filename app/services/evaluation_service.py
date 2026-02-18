"""
Service de gestion des évaluations des enseignants
"""

from app import db
from app.models import (
    EvaluationEnseignant, CampagneEvaluation, RapportEvaluation,
    Enseignant, Etudiant, UE
)
from sqlalchemy import func
from datetime import datetime


class EvaluationService:
    """Gestion des évaluations"""

    @staticmethod
    def creer_campagne(titre, date_debut, date_fin, semestre_id=None):
        """Crée une nouvelle campagne d'évaluation"""
        campagne = CampagneEvaluation(
            titre=titre,
            date_debut=date_debut,
            date_fin=date_fin,
            semestre_id=semestre_id,
            active=True
        )

        db.session.add(campagne)
        db.session.commit()

        return campagne

    @staticmethod
    def peut_evaluer(etudiant_id, enseignant_id, campagne_id=None):
        """Vérifie si un étudiant peut évaluer un enseignant"""

        # Vérifier si déjà évalué dans cette campagne
        query = EvaluationEnseignant.query.filter_by(
            etudiant_id=etudiant_id,
            enseignant_id=enseignant_id
        )

        if campagne_id:
            # Vérifier pour la campagne spécifique
            campagne = CampagneEvaluation.query.get(campagne_id)
            if not campagne or not campagne.active:
                return False

            # Vérifier si déjà évalué durant la campagne
            evaluation_existante = query.filter(
                EvaluationEnseignant.date_evaluation >= campagne.date_debut,
                EvaluationEnseignant.date_evaluation <= campagne.date_fin
            ).first()

            if evaluation_existante:
                return False

        return True

    @staticmethod
    def soumettre_evaluation(etudiant_id, enseignant_id, matiere_id, criteres, commentaires):
        """Soumet une évaluation"""

        evaluation = EvaluationEnseignant(
            etudiant_id=etudiant_id,
            enseignant_id=enseignant_id,
            matiere_id=matiere_id,
            pedagogie=criteres.get('pedagogie'),
            clarte=criteres.get('clarte'),
            disponibilite=criteres.get('disponibilite'),
            ponctualite=criteres.get('ponctualite'),
            organisation=criteres.get('organisation'),
            points_forts=commentaires.get('points_forts'),
            points_amelioration=commentaires.get('points_amelioration'),
            commentaire_general=commentaires.get('commentaire_general'),
            anonyme=True
        )

        evaluation.calculer_note_globale()

        db.session.add(evaluation)
        db.session.commit()

        return evaluation

    @staticmethod
    def generer_rapport(enseignant_id, campagne_id=None):
        """Génère un rapport d'évaluation pour un enseignant"""

        # Récupérer les évaluations
        query = EvaluationEnseignant.query.filter_by(enseignant_id=enseignant_id)

        if campagne_id:
            campagne = CampagneEvaluation.query.get(campagne_id)
            query = query.filter(
                EvaluationEnseignant.date_evaluation >= campagne.date_debut,
                EvaluationEnseignant.date_evaluation <= campagne.date_fin
            )

        evaluations = query.all()

        if not evaluations:
            return None

        # Calculer les moyennes
        nb_eval = len(evaluations)

        moyennes = {
            'note_moyenne_globale': sum(e.note_globale for e in evaluations) / nb_eval,
            'note_moyenne_pedagogie': sum(e.pedagogie for e in evaluations if e.pedagogie) / nb_eval,
            'note_moyenne_clarte': sum(e.clarte for e in evaluations if e.clarte) / nb_eval,
            'note_moyenne_disponibilite': sum(e.disponibilite for e in evaluations if e.disponibilite) / nb_eval,
            'note_moyenne_ponctualite': sum(e.ponctualite for e in evaluations if e.ponctualite) / nb_eval,
            'note_moyenne_organisation': sum(e.organisation for e in evaluations if e.organisation) / nb_eval,
        }

        # Créer ou mettre à jour le rapport
        rapport = RapportEvaluation.query.filter_by(
            enseignant_id=enseignant_id,
            campagne_id=campagne_id
        ).first()

        if not rapport:
            rapport = RapportEvaluation(
                enseignant_id=enseignant_id,
                campagne_id=campagne_id
            )
            db.session.add(rapport)

        rapport.nb_evaluations = nb_eval
        for key, value in moyennes.items():
            setattr(rapport, key, value)

        rapport.date_generation = datetime.utcnow()

        db.session.commit()

        return rapport

    @staticmethod
    def get_statistiques_globales(campagne_id=None):
        """Récupère les statistiques globales des évaluations"""

        query = EvaluationEnseignant.query

        if campagne_id:
            campagne = CampagneEvaluation.query.get(campagne_id)
            query = query.filter(
                EvaluationEnseignant.date_evaluation >= campagne.date_debut,
                EvaluationEnseignant.date_evaluation <= campagne.date_fin
            )

        total_evaluations = query.count()

        if total_evaluations == 0:
            return None

        # Moyennes globales
        moyennes = {
            'total_evaluations': total_evaluations,
            'note_moyenne_globale': db.session.query(func.avg(EvaluationEnseignant.note_globale)).scalar(),
            'note_moyenne_pedagogie': db.session.query(func.avg(EvaluationEnseignant.pedagogie)).scalar(),
            'note_moyenne_clarte': db.session.query(func.avg(EvaluationEnseignant.clarte)).scalar(),
            'note_moyenne_disponibilite': db.session.query(func.avg(EvaluationEnseignant.disponibilite)).scalar(),
            'note_moyenne_ponctualite': db.session.query(func.avg(EvaluationEnseignant.ponctualite)).scalar(),
            'note_moyenne_organisation': db.session.query(func.avg(EvaluationEnseignant.organisation)).scalar(),
        }

        # Top 5 enseignants
        top_enseignants = db.session.query(
            Enseignant.id,
            Enseignant.nom,
            Enseignant.prenom,
            func.avg(EvaluationEnseignant.note_globale).label('moyenne')
        ).join(EvaluationEnseignant).group_by(Enseignant.id).order_by(
            func.avg(EvaluationEnseignant.note_globale).desc()).limit(5).all()

        moyennes['top_enseignants'] = [
            {
                'nom': f"{e.nom} {e.prenom}",
                'moyenne': round(e.moyenne, 2)
            }
            for e in top_enseignants
        ]

        return moyennes