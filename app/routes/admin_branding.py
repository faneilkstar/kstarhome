"""
Administration du branding de l'école
"""

import os
import base64
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime

from app import db
from app.models import ConfigurationEcole, Departement, Sceau, Enseignant, departement_sceaux
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

    return render_template('admin/branding.html', config=config, branding_service=service)


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


# ============================================================
# GÉNÉRATEUR DE SCEAUX / CACHETS
# ============================================================
@branding_bp.route('/sceaux')
@login_required
@directeur_required
def sceaux():
    """Page du générateur de sceaux Le Welt (6 formes)"""
    service = BrandingService()
    config = service.get_config()
    try:
        departements = Departement.query.filter_by(active=True).order_by(Departement.nom).all()
    except:
        departements = []
    # Liste des sceaux existants
    sceaux_existants = Sceau.query.filter_by(actif=True).order_by(Sceau.date_creation.desc()).all()
    return render_template('admin/sceaux.html', config=config, departements=departements,
                           sceaux_existants=sceaux_existants)


@branding_bp.route('/sceaux/liste')
@login_required
def liste_sceaux_json():
    """API JSON : liste des sceaux disponibles pour l'utilisateur courant"""
    sceaux_list = []
    if current_user.role == 'DIRECTEUR':
        all_sceaux = Sceau.query.filter_by(actif=True).all()
    elif current_user.role == 'ENSEIGNANT':
        ens = current_user.enseignant_profile
        if ens:
            dept = Departement.query.filter_by(chef_id=ens.id).first()
            if dept:
                all_sceaux = list(dept.sceaux_autorises) + list(Sceau.query.filter_by(type_entite='ecole', actif=True).all())
            else:
                all_sceaux = list(Sceau.query.filter_by(type_entite='ecole', actif=True).all())
        else:
            all_sceaux = []
    else:
        all_sceaux = list(Sceau.query.filter_by(type_entite='ecole', actif=True).all())

    seen = set()
    for s in all_sceaux:
        if s.id not in seen:
            seen.add(s.id)
            sceaux_list.append({
                'id': s.id,
                'nom': s.nom,
                'type_forme': s.type_forme,
                'type_entite': s.type_entite,
                'image_path': s.image_path,
                'nom_auto': s.nom_auto
            })
    return jsonify(sceaux_list)


@branding_bp.route('/sceaux/sauvegarder', methods=['POST'])
@login_required
@directeur_required
def sauvegarder_sceau():
    """Sauvegarder un sceau généré (PNG base64) comme cachet officiel"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Données manquantes'}), 400

    image_data = data.get('image')  # base64 PNG
    type_sceau = data.get('type', 'ecole')  # ecole, departement, directeur, chef_departement
    type_forme = data.get('type_forme', 'circular')
    dept_id = data.get('departement_id')
    nom_sceau = data.get('nom', '')
    svg_data_str = data.get('svg_data', '')

    if not image_data:
        return jsonify({'error': 'Image manquante'}), 400

    # Décoder le base64
    if ',' in image_data:
        image_data = image_data.split(',')[1]

    try:
        image_bytes = base64.b64decode(image_data)
    except Exception:
        return jsonify({'error': 'Image invalide'}), 400

    # Sauvegarder le fichier
    upload_dir = os.path.join(current_app.root_path, 'static', 'branding', 'sceaux')
    os.makedirs(upload_dir, exist_ok=True)

    ts = int(datetime.now().timestamp())
    filename = f"sceau_{type_sceau}_{type_forme}_{ts}.png"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(image_bytes)

    relative_path = f"branding/sceaux/{filename}"

    # Auto-remplir le nom
    nom_auto = ''
    if type_sceau == 'departement' and dept_id:
        dept = Departement.query.get(dept_id)
        if dept and dept.chef:
            nom_auto = dept.chef.nom_complet
    elif type_sceau == 'directeur':
        config = ConfigurationEcole.query.first()
        if config:
            nom_auto = config.nom_directeur or ''

    # Créer le nom du sceau automatiquement
    if not nom_sceau:
        if type_sceau == 'ecole':
            nom_sceau = f"Cachet École ({type_forme})"
        elif type_sceau == 'departement' and dept_id:
            dept = Departement.query.get(dept_id)
            nom_sceau = f"Cachet {dept.nom if dept else 'Département'} ({type_forme})"
        elif type_sceau == 'directeur':
            nom_sceau = f"Cachet Directeur ({type_forme})"
        elif type_sceau == 'chef_departement':
            nom_sceau = f"Cachet Chef Département ({type_forme})"

    # Enregistrer en base
    sceau = Sceau(
        nom=nom_sceau,
        type_forme=type_forme,
        type_entite=type_sceau,
        image_path=relative_path,
        svg_data=svg_data_str[:5000] if svg_data_str else None,
        nom_auto=nom_auto,
        departement_id=int(dept_id) if dept_id else None,
        cree_par_id=current_user.id,
        actif=True
    )
    db.session.add(sceau)

    # Compatibilité : mettre aussi à jour les anciens champs
    if type_sceau == 'ecole':
        config = ConfigurationEcole.query.first()
        if config:
            config.cachet_path = relative_path
    elif type_sceau == 'departement' and dept_id:
        dept = Departement.query.get(dept_id)
        if dept:
            dept.cachet_path = relative_path
    elif type_sceau == 'directeur':
        config = ConfigurationEcole.query.first()
        if config:
            config.signature_directeur_path = relative_path

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Sceau "{nom_sceau}" enregistré avec succès !',
        'sceau_id': sceau.id,
        'path': relative_path
    })


@branding_bp.route('/sceaux/supprimer/<int:sceau_id>', methods=['POST'])
@login_required
@directeur_required
def supprimer_sceau(sceau_id):
    """Supprimer (désactiver) un sceau"""
    sceau = Sceau.query.get_or_404(sceau_id)
    sceau.actif = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Sceau supprimé'})


# ============================================================
# DISTRIBUTION DES SCEAUX AUX DÉPARTEMENTS
# ============================================================
@branding_bp.route('/sceaux/distribution', methods=['GET', 'POST'])
@login_required
@directeur_required
def distribution_sceaux():
    """Page de distribution des sceaux aux départements"""
    departements = Departement.query.filter_by(active=True).order_by(Departement.nom).all()
    sceaux_all = Sceau.query.filter_by(actif=True).order_by(Sceau.date_creation.desc()).all()

    if request.method == 'POST':
        # Traiter les affectations
        for dept in departements:
            # Effacer les anciennes associations
            db.session.execute(
                departement_sceaux.delete().where(departement_sceaux.c.departement_id == dept.id)
            )
            # Ajouter les nouvelles
            sceaux_ids = request.form.getlist(f'sceaux_dept_{dept.id}')
            for sid in sceaux_ids:
                db.session.execute(
                    departement_sceaux.insert().values(departement_id=dept.id, sceau_id=int(sid))
                )
        db.session.commit()
        flash('Distribution des sceaux mise à jour avec succès !', 'success')
        return redirect(url_for('branding.distribution_sceaux'))

    return render_template('admin/sceaux_distribution.html',
                           departements=departements, sceaux=sceaux_all)


@branding_bp.route('/sceaux/chef-info/<int:dept_id>')
@login_required
def chef_info(dept_id):
    """API : infos du chef de département"""
    dept = Departement.query.get_or_404(dept_id)
    chef_nom = dept.chef.nom_complet if dept.chef else ''
    chef_grade = dept.chef.grade if dept.chef else ''
    return jsonify({
        'chef_nom': chef_nom,
        'chef_grade': chef_grade,
        'dept_nom': dept.nom,
        'dept_code': dept.code
    })
