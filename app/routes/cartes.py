"""
Routes pour les cartes d'étudiant
"""

from flask import Blueprint, render_template, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime

from app.models import Etudiant, User
from app.services.carte_etudiant_service import CarteEtudiantService

cartes_bp = Blueprint('cartes', __name__, url_prefix='/cartes')


@cartes_bp.route('/ma-carte')
@login_required
def ma_carte():
    """Afficher/générer ma carte d'étudiant"""

    if current_user.role != 'ETUDIANT':
        flash('Accès réservé aux étudiants', 'danger')
        return redirect(url_for('main.index'))

    etudiant = current_user.etudiant_profile

    # Générer la carte
    service = CarteEtudiantService()
    carte_path = service.generer_carte_complete(etudiant)

    # Récupérer le directeur
    directeur = User.query.filter_by(role='DIRECTEUR').first()
    directeur_nom = f"{directeur.username}" if directeur else "Direction"

    return render_template('cartes/ma_carte.html',
                           carte_path=carte_path,
                           etudiant=etudiant,
                           date_emission=datetime.now().strftime('%d/%m/%Y'),
                           directeur=directeur_nom)


@cartes_bp.route('/telecharger/<int:etudiant_id>')
@login_required
def telecharger_carte(etudiant_id):
    """Télécharger la carte d'un étudiant"""

    etudiant = Etudiant.query.get_or_404(etudiant_id)

    # Vérifier les permissions
    if current_user.role == 'ETUDIANT' and current_user.etudiant_profile.id != etudiant.id:
        flash('Non autorisé', 'danger')
        return redirect(url_for('main.index'))

    service = CarteEtudiantService()
    carte_path = service.generer_carte_complete(etudiant)

    return send_file(carte_path, as_attachment=True, download_name=f"carte_{etudiant.matricule}.png")


@cartes_bp.route('/generer-toutes')
@login_required
def generer_toutes():
    """Générer les cartes de tous les étudiants (admin)"""

    if current_user.role not in ['DIRECTEUR', 'ADMIN']:
        flash('Non autorisé', 'danger')
        return redirect(url_for('main.index'))

    etudiants = Etudiant.query.all()
    service = CarteEtudiantService()

    generated = []
    for etudiant in etudiants:
        try:
            carte_path = service.generer_carte_complete(etudiant)
            generated.append({
                'etudiant': etudiant,
                'path': carte_path
            })
        except Exception as e:
            print(f"Erreur génération carte {etudiant.matricule}: {e}")

    flash(f'{len(generated)} cartes générées avec succès !', 'success')

    return render_template('cartes/batch_generation.html', cartes=generated)