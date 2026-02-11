"""
Dashboard analytics temps réel pour enseignants
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta

from app import db
from app.models import SessionTP, TP, MesureSimulation, InteractionIA, Etudiant

analytics_bp = Blueprint('analytics_labo', __name__, url_prefix='/analytics-labo')


def enseignant_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ENSEIGNANT':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@analytics_bp.route('/dashboard')
@login_required
@enseignant_required
def dashboard():
    """Dashboard analytics principal pour enseignant"""
    enseignant = current_user.enseignant_profile

    # TPs de cet enseignant
    mes_tps = TP.query.filter_by(enseignant_id=enseignant.id).all()
    tp_ids = [tp.id for tp in mes_tps]

    # Statistiques globales
    total_sessions = SessionTP.query.filter(SessionTP.tp_id.in_(tp_ids)).count()
    sessions_actives = SessionTP.query.filter(
        SessionTP.tp_id.in_(tp_ids),
        SessionTP.statut == 'en_cours'
    ).count()

    total_mesures = db.session.query(func.sum(SessionTP.nb_mesures)).filter(
        SessionTP.tp_id.in_(tp_ids)
    ).scalar() or 0

    # Sessions des 7 derniers jours
    sept_jours = datetime.utcnow() - timedelta(days=7)
    sessions_recentes = SessionTP.query.filter(
        SessionTP.tp_id.in_(tp_ids),
        SessionTP.date_debut >= sept_jours
    ).count()

    return render_template('analytics_labo/dashboard.html',
                           mes_tps=mes_tps,
                           total_sessions=total_sessions,
                           sessions_actives=sessions_actives,
                           total_mesures=total_mesures,
                           sessions_recentes=sessions_recentes)


@analytics_bp.route('/api/stats-temps-reel')
@login_required
@enseignant_required
def stats_temps_reel():
    """API pour statistiques temps réel (AJAX)"""
    enseignant = current_user.enseignant_profile
    mes_tps = TP.query.filter_by(enseignant_id=enseignant.id).all()
    tp_ids = [tp.id for tp in mes_tps]

    # Sessions actives en ce moment
    sessions_actives = SessionTP.query.filter(
        SessionTP.tp_id.in_(tp_ids),
        SessionTP.statut == 'en_cours'
    ).all()

    actives_data = []
    for session in sessions_actives:
        duree = (datetime.utcnow() - session.date_debut).total_seconds() / 60
        actives_data.append({
            'etudiant': session.etudiant.get_nom_complet(),
            'tp': session.tp.titre,
            'duree_minutes': int(duree),
            'nb_mesures': session.nb_mesures or 0
        })

    # Activité des 24h
    hier = datetime.utcnow() - timedelta(hours=24)
    activite_24h = db.session.query(
        func.strftime('%H', SessionTP.date_debut).label('heure'),
        func.count(SessionTP.id).label('count')
    ).filter(
        SessionTP.tp_id.in_(tp_ids),
        SessionTP.date_debut >= hier
    ).group_by('heure').all()

    activite_data = {h: c for h, c in activite_24h}

    # Progression par TP
    progression_tps = []
    for tp in mes_tps[:5]:  # Top 5
        total = SessionTP.query.filter_by(tp_id=tp.id).count()
        termines = SessionTP.query.filter_by(tp_id=tp.id, statut='terminé').count()

        progression_tps.append({
            'tp': tp.titre,
            'total': total,
            'termines': termines,
            'pourcentage': round(termines / total * 100, 1) if total > 0 else 0
        })

    return jsonify({
        'sessions_actives': actives_data,
        'activite_24h': activite_data,
        'progression_tps': progression_tps,
        'timestamp': datetime.utcnow().isoformat()
    })


@analytics_bp.route('/api/stats-par-etudiant/<int:tp_id>')
@login_required
@enseignant_required
def stats_par_etudiant(tp_id):
    """Statistiques détaillées par étudiant pour un TP"""
    tp = TP.query.get_or_404(tp_id)

    # Vérifier que c'est bien le TP de cet enseignant
    enseignant = current_user.enseignant_profile
    if tp.enseignant_id != enseignant.id:
        return jsonify({'error': 'Non autorisé'}), 403

    sessions = SessionTP.query.filter_by(tp_id=tp.id).all()

    etudiants_stats = []
    for session in sessions:
        etudiants_stats.append({
            'nom': session.etudiant.get_nom_complet(),
            'classe': session.etudiant.classe.nom_classe if session.etudiant.classe else '-',
            'statut': session.statut,
            'duree': session.duree_minutes or 0,
            'mesures': session.nb_mesures or 0,
            'note_ia': session.note_ia,
            'note_finale': session.note_finale,
            'date': session.date_debut.strftime('%d/%m/%Y %H:%M')
        })

    return jsonify({
        'tp': tp.titre,
        'etudiants': etudiants_stats,
        'total': len(etudiants_stats)
    })