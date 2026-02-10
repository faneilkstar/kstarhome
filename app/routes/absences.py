"""Routes pour la gestion des absences"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Etudiant, Enseignant, UE, Absence
from datetime import datetime, date

bp = Blueprint('absences', __name__, url_prefix='/absences')


def enseignant_required(f):
    """Décorateur pour vérifier que l'utilisateur est enseignant"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_enseignant():
            flash('Accès non autorisé', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


def directeur_required(f):
    """Décorateur pour vérifier que l'utilisateur est directeur"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_directeur():
            flash('Accès non autorisé', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/enseignant/gerer/<int:ue_id>', methods=['GET', 'POST'])
@enseignant_required
def gerer_absences_enseignant(ue_id):
    """Page de gestion des absences pour un enseignant"""

    enseignant = Enseignant.query.filter_by(user_id=current_user.id).first()
    ue = UE.query.get_or_404(ue_id)

    # Vérifier que l'enseignant a accès à cette UE
    if ue not in enseignant.ues:
        flash('Accès refusé à cette UE', 'danger')
        return redirect(url_for('enseignant.mes_ues'))

    if request.method == 'POST':
        # Saisir les absences
        date_absence_str = request.form.get('date_absence')
        etudiants_absents = request.form.getlist('etudiants_absents')

        if not date_absence_str:
            flash('Veuillez sélectionner une date', 'danger')
            return redirect(url_for('absences.gerer_absences_enseignant', ue_id=ue_id))

        try:
            date_absence = datetime.strptime(date_absence_str, '%Y-%m-%d').date()

            # Enregistrer les absences
            for etudiant_id in etudiants_absents:
                etudiant_id = int(etudiant_id)

                # Vérifier si l'absence existe déjà
                absence_existe = Absence.query.filter_by(
                    etudiant_id=etudiant_id,
                    ue_id=ue_id,
                    date_absence=date_absence
                ).first()

                if not absence_existe:
                    nouvelle_absence = Absence(
                        etudiant_id=etudiant_id,
                        ue_id=ue_id,
                        date_absence=date_absence,
                        justifiee=False,
                        saisi_par_id=current_user.id
                    )
                    db.session.add(nouvelle_absence)

            db.session.commit()
            flash(f'{len(etudiants_absents)} absence(s) enregistrée(s)', 'success')

        except ValueError:
            flash('Date invalide', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')

        return redirect(url_for('absences.gerer_absences_enseignant', ue_id=ue_id))

    # GET : Afficher le formulaire
    inscriptions = ue.inscriptions.filter_by(statut='validé').all()
    etudiants = [ins.etudiant for ins in inscriptions]

    # Récupérer les absences récentes
    absences_recentes = Absence.query.filter_by(ue_id=ue_id).order_by(
        Absence.date_absence.desc()
    ).limit(20).all()

    return render_template('enseignant/gerer_absences.html',
                           ue=ue,
                           etudiants=etudiants,
                           absences_recentes=absences_recentes)


@bp.route('/etudiant/mes-absences')
@login_required
def mes_absences_etudiant():
    """Page des absences pour un étudiant"""

    if not current_user.is_etudiant():
        flash('Accès refusé', 'danger')
        return redirect(url_for('auth.login'))

    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first()

    # Récupérer toutes les absences
    absences = Absence.query.filter_by(etudiant_id=etudiant.id).order_by(
        Absence.date_absence.desc()
    ).all()

    # Compter par UE
    absences_par_ue = {}
    for absence in absences:
        ue_code = absence.ue.code_ue
        if ue_code not in absences_par_ue:
            absences_par_ue[ue_code] = {
                'ue': absence.ue,
                'total': 0,
                'justifiees': 0,
                'non_justifiees': 0
            }

        absences_par_ue[ue_code]['total'] += 1
        if absence.justifiee:
            absences_par_ue[ue_code]['justifiees'] += 1
        else:
            absences_par_ue[ue_code]['non_justifiees'] += 1

    # Total général
    total_absences = len(absences)
    total_justifiees = sum(1 for a in absences if a.justifiee)
    total_non_justifiees = total_absences - total_justifiees

    return render_template('etudiant/mes_absences.html',
                           absences=absences,
                           absences_par_ue=absences_par_ue,
                           total_absences=total_absences,
                           total_justifiees=total_justifiees,
                           total_non_justifiees=total_non_justifiees)


@bp.route('/directeur/toutes')
@directeur_required
def toutes_absences_directeur():
    """Vue directeur : toutes les absences"""

    # Filtres
    classe_id = request.args.get('classe_id', type=int)
    ue_id = request.args.get('ue_id', type=int)
    justifiee = request.args.get('justifiee')

    query = Absence.query

    if classe_id:
        query = query.join(Etudiant).filter(Etudiant.classe_id == classe_id)

    if ue_id:
        query = query.filter_by(ue_id=ue_id)

    if justifiee == 'oui':
        query = query.filter_by(justifiee=True)
    elif justifiee == 'non':
        query = query.filter_by(justifiee=False)

    absences = query.order_by(Absence.date_absence.desc()).limit(100).all()

    # Listes pour les filtres
    from app.models import Classe
    classes = Classe.query.filter_by(active=True).all()
    ues = UE.query.all()

    return render_template('directeur/absences.html',
                           absences=absences,
                           classes=classes,
                           ues=ues,
                           classe_id=classe_id,
                           ue_id=ue_id,
                           justifiee=justifiee)


@bp.route('/justifier/<int:absence_id>', methods=['POST'])
@directeur_required
def justifier_absence(absence_id):
    """Justifier une absence (directeur uniquement)"""

    absence = Absence.query.get_or_404(absence_id)
    motif = request.form.get('motif', '')

    absence.justifiee = True
    absence.motif = motif

    db.session.commit()

    flash('Absence justifiée', 'success')
    return redirect(url_for('absences.toutes_absences_directeur'))


@bp.route('/supprimer/<int:absence_id>', methods=['POST'])
@directeur_required
def supprimer_absence(absence_id):
    """Supprimer une absence (directeur uniquement)"""

    absence = Absence.query.get_or_404(absence_id)

    db.session.delete(absence)
    db.session.commit()

    flash('Absence supprimée', 'success')
    return redirect(url_for('absences.toutes_absences_directeur'))