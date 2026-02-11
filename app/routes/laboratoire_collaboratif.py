"""
Routes pour le mode collaboratif du laboratoire
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import TP, SessionCollaborative, ParticipantCollaboratif, Etudiant
from datetime import datetime
import random
import string

collab_bp = Blueprint('labo_collab', __name__, url_prefix='/labo-collab')


def etudiant_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ETUDIANT':
            flash('Accès réservé aux étudiants', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


def generer_code_acces():
    """Génère un code d'accès unique de 6 caractères"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        existe = SessionCollaborative.query.filter_by(code_acces=code).first()
        if not existe:
            return code


@collab_bp.route('/creer-session/<int:tp_id>', methods=['GET', 'POST'])
@login_required
@etudiant_required
def creer_session(tp_id):
    """Créer une session collaborative"""
    tp = TP.query.get_or_404(tp_id)
    etudiant = current_user.etudiant_profile

    if request.method == 'POST':
        nom_session = request.form.get('nom_session', f"Session de {etudiant.prenom}")
        max_participants = int(request.form.get('max_participants', 4))
        partage_mesures = 'partage_mesures' in request.form

        # Créer la session
        session_collab = SessionCollaborative(
            tp_id=tp.id,
            createur_id=etudiant.id,
            nom_session=nom_session,
            code_acces=generer_code_acces(),
            max_participants=max_participants,
            partage_mesures=partage_mesures,
            statut='ouverte'
        )

        db.session.add(session_collab)
        db.session.flush()  # Pour obtenir l'ID

        # Ajouter le créateur comme participant
        participant = ParticipantCollaboratif(
            session_collab_id=session_collab.id,
            etudiant_id=etudiant.id,
            role='createur'
        )

        db.session.add(participant)
        db.session.commit()

        flash(f'Session créée ! Code d\'accès : {session_collab.code_acces}', 'success')
        return redirect(url_for('labo_collab.salle_collaborative', session_id=session_collab.id))

    return render_template('laboratoire/creer_session_collaborative.html', tp=tp)


@collab_bp.route('/rejoindre', methods=['GET', 'POST'])
@login_required
@etudiant_required
def rejoindre_session():
    """Rejoindre une session collaborative via un code"""

    if request.method == 'POST':
        code_acces = request.form.get('code_acces', '').strip().upper()

        session_collab = SessionCollaborative.query.filter_by(code_acces=code_acces).first()

        if not session_collab:
            flash('Code d\'accès invalide', 'danger')
            return redirect(url_for('labo_collab.rejoindre_session'))

        if session_collab.statut == 'terminee':
            flash('Cette session est déjà terminée', 'warning')
            return redirect(url_for('labo_collab.rejoindre_session'))

        # Vérifier le nombre de participants
        nb_participants = ParticipantCollaboratif.query.filter_by(
            session_collab_id=session_collab.id,
            actif=True
        ).count()

        if nb_participants >= session_collab.max_participants:
            flash('Session complète', 'warning')
            return redirect(url_for('labo_collab.rejoindre_session'))

        etudiant = current_user.etudiant_profile

        # Vérifier si déjà participant
        deja_inscrit = ParticipantCollaboratif.query.filter_by(
            session_collab_id=session_collab.id,
            etudiant_id=etudiant.id
        ).first()

        if deja_inscrit:
            flash('Vous êtes déjà dans cette session', 'info')
            return redirect(url_for('labo_collab.salle_collaborative', session_id=session_collab.id))

        # Ajouter le participant
        participant = ParticipantCollaboratif(
            session_collab_id=session_collab.id,
            etudiant_id=etudiant.id,
            role='participant'
        )

        db.session.add(participant)
        db.session.commit()

        flash(f'Vous avez rejoint "{session_collab.nom_session}" !', 'success')
        return redirect(url_for('labo_collab.salle_collaborative', session_id=session_collab.id))

    return render_template('laboratoire/rejoindre_session.html')


@collab_bp.route('/salle/<int:session_id>')
@login_required
@etudiant_required
def salle_collaborative(session_id):
    """Salle de TP collaborative en temps réel"""
    session_collab = SessionCollaborative.query.get_or_404(session_id)
    etudiant = current_user.etudiant_profile

    # Vérifier que l'étudiant est participant
    participant = ParticipantCollaboratif.query.filter_by(
        session_collab_id=session_id,
        etudiant_id=etudiant.id
    ).first()

    if not participant:
        flash('Vous n\'êtes pas participant de cette session', 'danger')
        return redirect(url_for('laboratoire.hub_etudiant'))

    # Liste des participants
    participants = ParticipantCollaboratif.query.filter_by(
        session_collab_id=session_id,
        actif=True
    ).all()

    return render_template('laboratoire/salle_collaborative.html',
                           session_collab=session_collab,
                           participants=participants,
                           est_createur=(participant.role == 'createur'))


@collab_bp.route('/api/sync-parametres', methods=['POST'])
@login_required
@etudiant_required
def sync_parametres():
    """Synchronise les paramètres entre participants (WebSocket simulé)"""
    data = request.json
    session_id = data.get('session_id')
    parametres = data.get('parametres')

    session_collab = SessionCollaborative.query.get_or_404(session_id)

    # Mettre à jour les données partagées
    import json
    session_collab.donnees_partagees = json.dumps(parametres)
    db.session.commit()

    return jsonify({'success': True})


@collab_bp.route('/api/get-parametres/<int:session_id>')
@login_required
@etudiant_required
def get_parametres(session_id):
    """Récupère les paramètres synchronisés"""
    session_collab = SessionCollaborative.query.get_or_404(session_id)

    import json
    donnees = json.loads(session_collab.donnees_partagees) if session_collab.donnees_partagees else {}

    # Liste des participants actifs
    participants = ParticipantCollaboratif.query.filter_by(
        session_collab_id=session_id,
        actif=True
    ).all()

    participants_data = [{
        'nom': p.etudiant.get_nom_complet(),
        'role': p.role,
        'mesures': p.nb_mesures_personnelles
    } for p in participants]

    return jsonify({
        'parametres': donnees,
        'participants': participants_data,
        'statut': session_collab.statut
    })