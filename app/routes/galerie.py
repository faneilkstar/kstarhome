"""
Routes pour la galerie d'images du site
"""
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from app import db
from app.models import ImageSite
galerie_bp = Blueprint('galerie', __name__, url_prefix='/galerie')
CATEGORIES = [
    ('partenariat', 'Partenariats', 'fas fa-handshake', '#0d6efd'),
    ('campus', 'Campus & Infrastructures', 'fas fa-building', '#198754'),
    ('identite', "Identite de l ecole", 'fas fa-university', '#DAA520'),
    ('evenement', 'Evenements', 'fas fa-calendar-star', '#6f42c1'),
    ('general', 'General', 'fas fa-images', '#6c757d'),
]
EXTENSIONS_AUTORISEES = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
def _extension_ok(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONS_AUTORISEES
@galerie_bp.route('/')
def index():
    cat_filtre = request.args.get('categorie', 'all')
    if cat_filtre and cat_filtre != 'all':
        images = ImageSite.query.filter_by(visible=True, categorie=cat_filtre).order_by(ImageSite.ordre, ImageSite.date_ajout.desc()).all()
    else:
        images = ImageSite.query.filter_by(visible=True).order_by(ImageSite.ordre, ImageSite.date_ajout.desc()).all()
    return render_template('galerie/index.html', images=images, categories=CATEGORIES, cat_filtre=cat_filtre)
@galerie_bp.route('/gestion')
@login_required
def gestion():
    if current_user.role != 'DIRECTEUR':
        flash('Acces reserve au directeur.', 'danger')
        return redirect(url_for('galerie.index'))
    images = ImageSite.query.order_by(ImageSite.categorie, ImageSite.ordre, ImageSite.date_ajout.desc()).all()
    return render_template('galerie/gestion.html', images=images, categories=CATEGORIES)
@galerie_bp.route('/ajouter', methods=['POST'])
@login_required
def ajouter():
    if current_user.role != 'DIRECTEUR':
        flash('Acces reserve au directeur.', 'danger')
        return redirect(url_for('galerie.index'))
    titre = request.form.get('titre', '').strip()
    description = request.form.get('description', '').strip()
    categorie = request.form.get('categorie', 'general')
    fichier = request.files.get('image')
    if not titre:
        flash('Le titre est obligatoire.', 'warning')
        return redirect(url_for('galerie.gestion'))
    if not fichier or fichier.filename == '':
        flash('Veuillez selectionner une image.', 'warning')
        return redirect(url_for('galerie.gestion'))
    if not _extension_ok(fichier.filename):
        flash('Format non autorise. Utilisez PNG, JPG, GIF, WEBP ou SVG.', 'danger')
        return redirect(url_for('galerie.gestion'))
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'galerie')
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(fichier.filename)
    base, ext = os.path.splitext(filename)
    filename = f"{base}_{int(datetime.now().timestamp())}{ext}"
    fichier.save(os.path.join(upload_dir, filename))
    image = ImageSite(titre=titre, description=description, fichier=f"uploads/galerie/{filename}", categorie=categorie, auteur_id=current_user.id)
    db.session.add(image)
    db.session.commit()
    flash(f'Image ajoutee avec succes !', 'success')
    return redirect(url_for('galerie.gestion'))
@galerie_bp.route('/supprimer/<int:image_id>', methods=['POST'])
@login_required
def supprimer(image_id):
    if current_user.role != 'DIRECTEUR':
        flash('Acces reserve au directeur.', 'danger')
        return redirect(url_for('galerie.index'))
    image = ImageSite.query.get_or_404(image_id)
    filepath = os.path.join(current_app.root_path, 'static', image.fichier)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(image)
    db.session.commit()
    flash('Image supprimee.', 'success')
    return redirect(url_for('galerie.gestion'))
@galerie_bp.route('/toggle/<int:image_id>', methods=['POST'])
@login_required
def toggle_visibilite(image_id):
    if current_user.role != 'DIRECTEUR':
        return redirect(url_for('galerie.index'))
    image = ImageSite.query.get_or_404(image_id)
    image.visible = not image.visible
    db.session.commit()
    flash(f'Visibilite changee.', 'info')
    return redirect(url_for('galerie.gestion'))
