"""
Gestion des vidéos explicatives
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import VideoExplicative, VueVideo, TP

videos_bp = Blueprint('videos_labo', __name__, url_prefix='/videos-labo')


@videos_bp.route('/bibliotheque')
@login_required
def bibliotheque():
    """Bibliothèque de toutes les vidéos"""

    # Vidéos par type de simulation
    videos_par_type = {}

    types_sim = db.session.query(VideoExplicative.type_simulation).distinct().all()

    for (type_sim,) in types_sim:
        videos = VideoExplicative.query.filter_by(type_simulation=type_sim).all()
        videos_par_type[type_sim] = videos

    return render_template('videos_labo/bibliotheque.html',
                           videos_par_type=videos_par_type)


@videos_bp.route('/voir/<int:video_id>')
@login_required
def voir_video(video_id):
    """Page de visionnage d'une vidéo"""
    video = VideoExplicative.query.get_or_404(video_id)

    # Incrémenter le compteur de vues
    video.nb_vues += 1

    # Enregistrer la vue pour cet étudiant
    if current_user.role == 'ETUDIANT':
        vue = VueVideo(
            video_id=video.id,
            etudiant_id=current_user.etudiant_profile.id
        )
        db.session.add(vue)

    db.session.commit()

    # Vidéos similaires
    videos_similaires = VideoExplicative.query.filter(
        VideoExplicative.type_simulation == video.type_simulation,
        VideoExplicative.id != video.id
    ).limit(3).all()

    return render_template('videos_labo/voir_video.html',
                           video=video,
                           videos_similaires=videos_similaires)


@videos_bp.route('/api/progression', methods=['POST'])
@login_required
def enregistrer_progression():
    """Enregistre la progression de visionnage"""
    data = request.json
    video_id = data.get('video_id')
    pourcentage = data.get('pourcentage', 0)

    if current_user.role == 'ETUDIANT':
        vue = VueVideo.query.filter_by(
            video_id=video_id,
            etudiant_id=current_user.etudiant_profile.id
        ).order_by(VueVideo.date_vue.desc()).first()

        if vue:
            vue.pourcentage_visionne = max(vue.pourcentage_visionne, pourcentage)
            db.session.commit()

    return jsonify({'success': True})