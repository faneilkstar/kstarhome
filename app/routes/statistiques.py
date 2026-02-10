"""Routes pour les statistiques avancées"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Etudiant, Enseignant, UE, Note, Classe
from sqlalchemy import func
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from functools import wraps
from app import db


bp = Blueprint('statistiques', __name__, url_prefix='/statistiques')


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


@bp.route('/globales')
@directeur_required
def statistiques_globales():
    """Page de statistiques globales avec graphiques"""

    # Statistiques générales
    total_etudiants = Etudiant.query.filter_by(statut_inscription='accepté').count()
    total_enseignants = Enseignant.query.filter_by(actif=True).count()
    total_ues = UE.query.count()
    total_classes = Classe.query.filter_by(active=True).count()

    # Répartition par cycle
    licence = Etudiant.query.join(Classe).filter(
        Classe.cycle == 'Licence',
        Etudiant.statut_inscription == 'accepté'
    ).count()

    master = Etudiant.query.join(Classe).filter(
        Classe.cycle == 'Master',
        Etudiant.statut_inscription == 'accepté'
    ).count()

    # Taux de réussite global
    notes_toutes = Note.query.filter(Note.note.isnot(None)).all()
    if notes_toutes:
        notes_validees = sum(1 for n in notes_toutes if n.note >= 10)
        taux_reussite = round((notes_validees / len(notes_toutes) * 100), 2)
    else:
        taux_reussite = 0

    # Moyennes par classe
    classes = Classe.query.filter_by(active=True).all()
    moyennes_classes = []

    for classe in classes:
        etudiants = classe.etudiants.filter_by(statut_inscription='accepté').all()
        if etudiants:
            moyennes = [e.get_moyenne_generale() for e in etudiants if e.get_moyenne_generale()]
            if moyennes:
                moy = round(sum(moyennes) / len(moyennes), 2)
                moyennes_classes.append({
                    'nom': classe.nom_classe,
                    'moyenne': moy,
                    'effectif': len(etudiants)
                })

    # Top 10 étudiants
    etudiants_tous = Etudiant.query.filter_by(statut_inscription='accepté').all()
    top_etudiants = []

    for etudiant in etudiants_tous:
        moy = etudiant.get_moyenne_generale()
        if moy:
            top_etudiants.append({
                'nom': etudiant.get_nom_complet(),
                'classe': etudiant.classe.nom_classe if etudiant.classe else '-',
                'moyenne': moy
            })

    top_etudiants = sorted(top_etudiants, key=lambda x: x['moyenne'], reverse=True)[:10]

    # Répartition des notes
    distribution_notes = {
        'excellent': 0,  # >= 16
        'bien': 0,  # 14-16
        'assez_bien': 0,  # 12-14
        'passable': 0,  # 10-12
        'ajourne': 0  # < 10
    }

    for note in notes_toutes:
        if note.note >= 16:
            distribution_notes['excellent'] += 1
        elif note.note >= 14:
            distribution_notes['bien'] += 1
        elif note.note >= 12:
            distribution_notes['assez_bien'] += 1
        elif note.note >= 10:
            distribution_notes['passable'] += 1
        else:
            distribution_notes['ajourne'] += 1

    return render_template('directeur/statistiques.html',
                           total_etudiants=total_etudiants,
                           total_enseignants=total_enseignants,
                           total_ues=total_ues,
                           total_classes=total_classes,
                           licence=licence,
                           master=master,
                           taux_reussite=taux_reussite,
                           moyennes_classes=moyennes_classes,
                           top_etudiants=top_etudiants,
                           distribution_notes=distribution_notes)


@bp.route('/classe/<int:classe_id>')
@directeur_required
def statistiques_classe(classe_id):
    """Statistiques détaillées d'une classe"""

    classe = Classe.query.get_or_404(classe_id)
    etudiants = classe.etudiants.filter_by(statut_inscription='accepté').all()

    # Calculer les moyennes
    moyennes = []
    for etudiant in etudiants:
        moy = etudiant.get_moyenne_generale()
        if moy:
            moyennes.append({
                'etudiant': etudiant.get_nom_complet(),
                'moyenne': moy
            })

    moyennes = sorted(moyennes, key=lambda x: x['moyenne'], reverse=True)

    # Moyenne de la classe
    if moyennes:
        moyenne_classe = round(sum([m['moyenne'] for m in moyennes]) / len(moyennes), 2)
    else:
        moyenne_classe = None

    # Taux de réussite de la classe
    notes_classe = Note.query.join(Etudiant).filter(
        Etudiant.classe_id == classe_id,
        Note.note.isnot(None)
    ).all()

    if notes_classe:
        notes_validees = sum(1 for n in notes_classe if n.note >= 10)
        taux_reussite_classe = round((notes_validees / len(notes_classe) * 100), 2)
    else:
        taux_reussite_classe = 0

    return render_template('directeur/statistiques_classe.html',
                           classe=classe,
                           etudiants=etudiants,
                           moyennes=moyennes,
                           moyenne_classe=moyenne_classe,
                           taux_reussite=taux_reussite_classe)


@bp.route('/ue/<int:ue_id>')
@directeur_required
def statistiques_ue(ue_id):
    """Statistiques détaillées d'une UE"""

    ue = UE.query.get_or_404(ue_id)
    notes = ue.notes.filter(Note.note.isnot(None)).all()

    if notes:
        # Moyenne de l'UE
        moyenne_ue = round(sum([n.note for n in notes]) / len(notes), 2)

        # Note min et max
        note_min = min([n.note for n in notes])
        note_max = max([n.note for n in notes])

        # Taux de réussite
        notes_validees = sum(1 for n in notes if n.note >= 10)
        taux_reussite = round((notes_validees / len(notes) * 100), 2)

        # Distribution
        distribution = []
        for note in notes:
            distribution.append({
                'etudiant': note.etudiant.get_nom_complet(),
                'note': note.note,
                'valide': note.est_valide()
            })

        distribution = sorted(distribution, key=lambda x: x['note'], reverse=True)
    else:
        moyenne_ue = None
        note_min = None
        note_max = None
        taux_reussite = 0
        distribution = []

    return render_template('directeur/statistiques_ue.html',
                           ue=ue,
                           moyenne_ue=moyenne_ue,
                           note_min=note_min,
                           note_max=note_max,
                           taux_reussite=taux_reussite,
                           distribution=distribution)


@bp.route('/api/data-graphique')
@directeur_required
def api_data_graphique():
    """API pour récupérer les données pour les graphiques dynamiques"""

    # Données pour graphique ligne : évolution des inscriptions
    inscriptions_par_mois = db.session.query(
        func.strftime('%Y-%m', Etudiant.date_inscription).label('mois'),
        func.count(Etudiant.id).label('total')
    ).group_by('mois').order_by('mois').all()

    data = {
        'inscriptions': {
            'mois': [i[0] for i in inscriptions_par_mois],
            'totaux': [i[1] for i in inscriptions_par_mois]
        }
    }

    return jsonify(data)