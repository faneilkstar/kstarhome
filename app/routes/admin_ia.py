"""
Administration et monitoring de l'IA
"""

from flask import Blueprint, render_template, jsonify, send_file
from flask_login import login_required, current_user
from app.services.ia_training import IATrainingService

admin_ia_bp = Blueprint('admin_ia', __name__, url_prefix='/admin-ia')


def directeur_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'DIRECTEUR':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@admin_ia_bp.route('/dashboard')
@login_required
@directeur_required
def dashboard():
    """Dashboard de monitoring de l'IA"""
    service = IATrainingService()
    stats = service.analyser_qualite_reponses()

    return render_template('admin_ia/dashboard.html', stats=stats)


@admin_ia_bp.route('/exporter-dataset/<format>')
@login_required
@directeur_required
def exporter_dataset(format):
    """Exporte le dataset pour fine-tuning"""
    service = IATrainingService()
    filepath = service.exporter_dataset_finetuning(format=format)

    return send_file(filepath, as_attachment=True)


@admin_ia_bp.route('/api/stats-temps-reel')
@login_required
@directeur_required
def stats_temps_reel():
    """API pour stats temps réel"""
    service = IATrainingService()
    stats = service.analyser_qualite_reponses()

    return jsonify(stats)