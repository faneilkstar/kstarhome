"""
Administration du branding de l'école
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import ConfigurationEcole
from app.services.branding_service import BrandingService

branding_bp = Blueprint('branding', __name__, url_prefix='/admin/branding')


def directeur_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'DIRECTEUR':
            flash('Accès réservé au directeur', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@branding_bp.route('/')
@login_required
@directeur_required
def index():
    """Page de configuration du branding"""
    service = BrandingService()
    config = service.get_config()

    return render_template('admin/branding.html', config=config)


@branding_bp.route('/update', methods=['POST'])
@login_required
@directeur_required
def update():
    """Mise à jour de la configuration"""
    service = BrandingService()

    data = {
        'nom_ecole': request.form.get('nom_ecole'),
        'nom_court': request.form.get('nom_court'),
        'slogan': request.form.get('slogan'),
        'adresse': request.form.get('adresse'),
        'ville': request.form.get('ville'),
        'code_postal': request.form.get('code_postal'),
        'pays': request.form.get('pays'),
        'telephone': request.form.get('telephone'),
        'email': request.form.get('email'),
        'site_web': request.form.get('site_web'),
        'couleur_primaire': request.form.get('couleur_primaire'),
        'couleur_secondaire': request.form.get('couleur_secondaire'),
        'couleur_accent': request.form.get('couleur_accent'),
        'numero_agrement': request.form.get('numero_agrement'),
        'numero_registre': request.form.get('numero_registre'),
        'annee_creation': int(request.form.get('annee_creation', 2024)),
        'nom_directeur': request.form.get('nom_directeur'),
        'titre_directeur': request.form.get('titre_directeur')
    }

    service.update_config(data)

    flash('Configuration mise à jour avec succès !', 'success')
    return redirect(url_for('branding.index'))


@branding_bp.route('/upload-logo', methods=['POST'])
@login_required
@directeur_required
def upload_logo():
    """Upload d'un logo"""
    if 'logo' not in request.files:
        return jsonify({'error': 'Pas de fichier'}), 400

    file = request.files['logo']
    type_logo = request.form.get('type', 'principal')

    if file.filename == '':
        return jsonify({'error': 'Pas de fichier sélectionné'}), 400

    service = BrandingService()
    filepath = service.upload_logo(file, type=type_logo)

    return jsonify({
        'success': True,
        'filepath': filepath,
        'message': f'Logo {type_logo} uploadé avec succès'
    })


@branding_bp.route('/preview-css')
@login_required
@directeur_required
def preview_css():
    """Prévisualisation du CSS personnalisé"""
    service = BrandingService()
    css = service.get_css_variables()

    return css, 200, {'Content-Type': 'text/css'}