"""
Routes pour la gestion des Départements
Architecture V2
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Departement, Enseignant, Filiere, UE
from functools import wraps

bp = Blueprint('departements', __name__, url_prefix='/directeur/departements')


def directeur_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'DIRECTEUR':
            flash('Accès refusé. Vous devez être directeur.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@login_required
@directeur_required
def liste_departements():
    """Liste tous les départements"""
    departements = Departement.query.order_by(Departement.code).all()
    return render_template('directeur/departements/liste.html', departements=departements)


@bp.route('/nouveau', methods=['GET', 'POST'])
@login_required
@directeur_required
def creer_departement():
    """Créer un nouveau département"""
    if request.method == 'POST':
        nom = request.form.get('nom')
        code = request.form.get('code').upper()
        description = request.form.get('description')
        chef_id = request.form.get('chef_id')

        # Validation
        if Departement.query.filter_by(code=code).first():
            flash(f'Le code {code} est déjà utilisé.', 'danger')
            return redirect(url_for('departements.creer_departement'))

        # Créer le département
        dept = Departement(
            nom=nom,
            code=code,
            description=description,
            chef_id=chef_id if chef_id else None
        )

        db.session.add(dept)
        db.session.commit()

        flash(f'✅ Département {code} créé avec succès !', 'success')
        return redirect(url_for('departements.liste_departements'))

    # GET
    enseignants = Enseignant.query.filter_by(actif=True).order_by(Enseignant.nom).all()
    return render_template('directeur/departements/creer.html', enseignants=enseignants)


@bp.route('/<int:id>')
@login_required
@directeur_required
def detail_departement(id):
    """Afficher les détails d'un département"""
    dept = Departement.query.get_or_404(id)

    # Statistiques
    filieres = dept.filieres.filter_by(active=True).all()

    # UE par catégorie
    ues_fondamentales = dept.ues.filter_by(categorie='fondamentale', active=True).all()
    ues_specialite = dept.ues.filter_by(categorie='specialite', active=True).all()
    ues_transversales = dept.ues.filter_by(categorie='transversale', active=True).all()
    ues_libres = dept.ues.filter_by(categorie='libre', active=True).all()

    return render_template('directeur/departements/detail.html',
                         departement=dept,
                         filieres=filieres,
                         ues_fondamentales=ues_fondamentales,
                         ues_specialite=ues_specialite,
                         ues_transversales=ues_transversales,
                         ues_libres=ues_libres)


@bp.route('/<int:id>/assigner-chef', methods=['POST'])
@login_required
@directeur_required
def assigner_chef(id):
    """Assigner un chef de département"""
    dept = Departement.query.get_or_404(id)
    chef_id = request.form.get('chef_id')

    if chef_id:
        enseignant = Enseignant.query.get(chef_id)
        if not enseignant:
            flash('Enseignant introuvable.', 'danger')
            return redirect(url_for('departements.detail_departement', id=id))

        dept.chef_id = chef_id
        db.session.commit()

        flash(f'✅ {enseignant.nom_complet} nommé chef du département {dept.code}', 'success')
    else:
        dept.chef_id = None
        db.session.commit()
        flash(f'Chef de département retiré pour {dept.code}', 'info')

    return redirect(url_for('departements.detail_departement', id=id))


@bp.route('/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
@directeur_required
def modifier_departement(id):
    """Modifier un département"""
    dept = Departement.query.get_or_404(id)

    if request.method == 'POST':
        dept.nom = request.form.get('nom')
        dept.description = request.form.get('description')

        # Vérifier si le code change
        nouveau_code = request.form.get('code').upper()
        if nouveau_code != dept.code:
            if Departement.query.filter_by(code=nouveau_code).first():
                flash(f'Le code {nouveau_code} est déjà utilisé.', 'danger')
                return redirect(url_for('departements.modifier_departement', id=id))
            dept.code = nouveau_code

        db.session.commit()
        flash(f'✅ Département {dept.code} modifié avec succès !', 'success')
        return redirect(url_for('departements.detail_departement', id=id))

    enseignants = Enseignant.query.filter_by(actif=True).order_by(Enseignant.nom).all()
    return render_template('directeur/departements/modifier.html',
                         departement=dept,
                         enseignants=enseignants)


@bp.route('/<int:id>/desactiver', methods=['POST'])
@login_required
@directeur_required
def desactiver_departement(id):
    """Désactiver un département"""
    dept = Departement.query.get_or_404(id)
    dept.active = not dept.active
    db.session.commit()

    statut = "activé" if dept.active else "désactivé"
    flash(f'Département {dept.code} {statut}', 'info')
    return redirect(url_for('departements.liste_departements'))

