"""
Routes pour les évaluations des enseignants
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.models import (
    Enseignant, Matiere, CampagneEvaluation,
    EvaluationEnseignant
)
from app.services.evaluation_service import EvaluationService

evaluations_bp = Blueprint('evaluations', __name__, url_prefix='/evaluations')


@evaluations_bp.route('/enseignants')
@login_required
def evaluer_enseignants():
    """Page pour évaluer les enseignants"""

    if current_user.role != 'ETUDIANT':
        flash('Accès réservé aux étudiants', 'danger')
        return redirect(url_for('main.index'))

    etudiant = current_user.etudiant_profile

    # Récupérer les enseignants de cet étudiant
    enseignants = []

    if etudiant.classe:
        for matiere in etudiant.classe.matieres:
            if matiere.enseignant:
                # Vérifier si peut évaluer
                peut_evaluer = EvaluationService.peut_evaluer(
                    etudiant.id,
                    matiere.enseignant.id
                )

                enseignants.append({
                    'enseignant': matiere.enseignant,
                    'matiere': matiere,
                    'peut_evaluer': peut_evaluer
                })

    # Campagne active
    campagne_active = CampagneEvaluation.query.filter_by(active=True).first()

    return render_template('evaluations/evaluer_enseignants.html',
                           enseignants=enseignants,
                           campagne=campagne_active)


@evaluations_bp.route('/enseignant/<int:enseignant_id>/evaluer', methods=['GET', 'POST'])
@login_required
def evaluer_enseignant(enseignant_id):
    """Formulaire d'évaluation d'un enseignant"""

    if current_user.role != 'ETUDIANT':
        flash('Accès réservé aux étudiants', 'danger')
        return redirect(url_for('main.index'))

    enseignant = Enseignant.query.get_or_404(enseignant_id)
    etudiant = current_user.etudiant_profile

    # Vérifier si peut évaluer
    if not EvaluationService.peut_evaluer(etudiant.id, enseignant.id):
        flash('Vous avez déjà évalué cet enseignant', 'warning')
        return redirect(url_for('evaluations.evaluer_enseignants'))

    # Trouver l'UE
    matiere = None
    if etudiant.classe:
        for m in etudiant.classe.matieres:
            if m.enseignant_id == enseignant.id:
                matiere = m
                break

    if request.method == 'POST':
        criteres = {
            'pedagogie': float(request.form.get('pedagogie', 0)),
            'clarte': float(request.form.get('clarte', 0)),
            'disponibilite': float(request.form.get('disponibilite', 0)),
            'ponctualite': float(request.form.get('ponctualite', 0)),
            'organisation': float(request.form.get('organisation', 0))
        }

        commentaires = {
            'points_forts': request.form.get('points_forts', ''),
            'points_amelioration': request.form.get('points_amelioration', ''),
            'commentaire_general': request.form.get('commentaire_general', '')
        }

        EvaluationService.soumettre_evaluation(
            etudiant.id,
            enseignant.id,
            matiere.id if matiere else None,
            criteres,
            commentaires
        )

        flash('Évaluation soumise avec succès ! Merci pour votre retour.', 'success')
        return redirect(url_for('evaluations.evaluer_enseignants'))

    return render_template('evaluations/formulaire_evaluation.html',
                           enseignant=enseignant,
                           matiere=matiere)


@evaluations_bp.route('/directeur/dashboard')
@login_required
def dashboard_directeur():
    """Dashboard des évaluations pour le directeur"""

    if current_user.role != 'DIRECTEUR':
        flash('Accès réservé au directeur', 'danger')
        return redirect(url_for('main.index'))

    # Statistiques globales
    stats = EvaluationService.get_statistiques_globales()

    # Tous les rapports
    rapports = RapportEvaluation.query.order_by(RapportEvaluation.note_moyenne_globale.desc()).all()

    return render_template('evaluations/dashboard_directeur.html',
                           stats=stats,
                           rapports=rapports)


@evaluations_bp.route('/directeur/rapport/<int:enseignant_id>')
@login_required
def voir_rapport(enseignant_id):
    """Voir le rapport détaillé d'un enseignant"""

    if current_user.role != 'DIRECTEUR':
        flash('Accès réservé au directeur', 'danger')
        return redirect(url_for('main.index'))

    enseignant = Enseignant.query.get_or_404(enseignant_id)

    # Générer ou récupérer le rapport
    rapport = EvaluationService.generer_rapport(enseignant.id)

    # Récupérer les évaluations individuelles (anonymisées)
    evaluations = EvaluationEnseignant.query.filter_by(
        enseignant_id=enseignant.id
    ).order_by(EvaluationEnseignant.date_evaluation.desc()).all()

    return render_template('evaluations/rapport_enseignant.html',
                           enseignant=enseignant,
                           rapport=rapport,
                           evaluations=evaluations)


@evaluations_bp.route('/enseignant/mon-rapport')
@login_required
def mon_rapport():
    """Rapport d'évaluation pour l'enseignant lui-même"""

    if current_user.role != 'ENSEIGNANT':
        flash('Accès réservé aux enseignants', 'danger')
        return redirect(url_for('main.index'))

    enseignant = current_user.enseignant_profile

    # Générer le rapport
    rapport = EvaluationService.generer_rapport(enseignant.id)

    if not rapport:
        flash('Aucune évaluation disponible pour le moment', 'info')
        return redirect(url_for('main.index'))

    return render_template('evaluations/mon_rapport_enseignant.html',
                           rapport=rapport)