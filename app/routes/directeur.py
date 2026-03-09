# =========================================================
# 1. BIBLIOTHÈQUES PYTHON STANDARD
# =========================================================
import os
import io
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash

# Imports nécessaires
from app.models import Deliberation, Note, Etudiant, Classe
from sqlalchemy import func



# =========================================================
# 2. FLASK & EXTENSIONS
# =========================================================
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, send_file, jsonify, current_app
)
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError

# =========================================================
# 3. GRAPHIQUES & IMAGES (Matplotlib)
# =========================================================
import matplotlib
matplotlib.use('Agg') # IMPORTANT : À laisser avant l'import de pyplot
import matplotlib.pyplot as plt

# =========================================================
# 4. GÉNÉRATION PDF (ReportLab)
# =========================================================
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# =========================================================
# 5. MODÈLES & BASE DE DONNÉES
# =========================================================
from app import db
from app.models import (
    User, Etudiant, Enseignant, Filiere, Classe, UE, Note,
    InscriptionUE, Statistique, Annonce, Document, Diplome, Departement
)

# =========================================================
# 6. UTILITAIRES (Excel, etc.)
# =========================================================
# (Assure-toi que ce fichier existe bien, sinon commente ces lignes)
try:
    from app.utils.excel_generator import export_etudiants_excel, export_statistiques_excel
except ImportError:
    pass # On ignore si le fichier n'existe pas encore

# =========================================================
# DÉFINITION DU BLUEPRINT
# =========================================================
bp = Blueprint('directeur', __name__, url_prefix='/directeur')


# =========================================================================
# DÉCORATEUR DE SÉCURITÉ
# =========================================================================
# =========================================================================
# DÉCORATEUR DE SÉCURITÉ (CORRIGÉ)
# =========================================================================
def directeur_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # ERREUR ÉTAIT ICI : J'ai enlevé les () après is_directeur
        if not current_user.is_directeur:
            flash('Accès réservé à la Direction.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


# =========================================================================
# DASHBOARD (Optimisé pour la performance)
# =========================================================================
@bp.route('/dashboard')
@directeur_required
def dashboard():
    # OPTIMISATION : On utilise .count() au lieu de charger toute la liste
    # C'est beaucoup plus rapide quand il y a beaucoup de données.
    nb_etudiants = Etudiant.query.count()
    nb_enseignants = Enseignant.query.filter_by(actif=True).count()
    nb_ues = UE.query.count()
    nb_filieres = Filiere.query.count()
    nb_departements = Departement.query.filter_by(active=True).count()  # NOUVEAU

    # On charge uniquement les listes nécessaires pour l'affichage (limitées)
    classes_recentes = Classe.query.filter_by(active=True).order_by(Classe.id.desc()).limit(5).all()

    # Pour les graphiques ou listes complètes, on passe les objets
    filieres = Filiere.query.all()

    return render_template('directeur/dashboard.html',
                           etudiants=Etudiant.query.all(),  # Gardé pour compatibilité template existant
                           enseignants=Enseignant.query.all(),
                           ues=UE.query.all(),
                           filieres=filieres,
                           classes=Classe.query.all(),
                           classes_recentes=classes_recentes,
                           # Stats rapides
                           nb_etudiants=nb_etudiants,
                           nb_enseignants=nb_enseignants,
                           nb_ues=nb_ues,
                           nb_filieres=nb_filieres,
                           nb_departements=nb_departements)  # NOUVEAU

# ÉTAPE 1 : Créer le compte utilisateur


# =========================================================================
# GESTION DÉPARTEMENTS (NOUVEAU - Architecture V2)
# =========================================================================
@bp.route('/departements')
@directeur_required
def liste_departements():
    """Liste de tous les départements"""
    departements = Departement.query.order_by(Departement.nom).all()
    return render_template('directeur/liste_departements.html', departements=departements)


@bp.route('/departement/ajouter', methods=['GET', 'POST'])
@directeur_required
def ajouter_departement():
    """Créer un nouveau département"""
    if request.method == 'POST':
        nom = request.form.get('nom').strip()
        code = request.form.get('code').strip().upper()
        description = request.form.get('description', '').strip()

        # Validation
        if not nom or not code:
            flash("Le nom et le code sont obligatoires.", "warning")
            return redirect(url_for('directeur.ajouter_departement'))
        
        # Vérification doublon
        if Departement.query.filter_by(code=code).first():
            flash(f"Un département avec le code {code} existe déjà.", "warning")
            return redirect(url_for('directeur.ajouter_departement'))
        
        try:
            departement = Departement(
                nom=nom,
                code=code,
                description=description,
                chef_id=None,  # Le chef sera assigné plus tard
                active=True
            )
            db.session.add(departement)
            db.session.commit()
            
            flash(f"Département {nom} créé avec succès! Vous pouvez maintenant assigner un chef.", "success")
            return redirect(url_for('directeur.detail_departement', dept_id=departement.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la création : {str(e)}", "danger")
    
    # GET : Afficher le formulaire
    return render_template('directeur/ajouter_departement.html')


@bp.route('/departement/<int:dept_id>')
@directeur_required
def detail_departement(dept_id):
    """Détails d'un département"""
    departement = Departement.query.get_or_404(dept_id)
    return render_template('directeur/detail_departement.html', departement=departement)


@bp.route('/departement/<int:dept_id>/modifier', methods=['GET', 'POST'])
@directeur_required
def modifier_departement(dept_id):
    """Modifier un département existant"""
    departement = Departement.query.get_or_404(dept_id)
    
    if request.method == 'POST':
        departement.nom = request.form.get('nom').strip()
        departement.code = request.form.get('code').strip().upper()
        departement.description = request.form.get('description', '').strip()

        try:
            db.session.commit()
            flash(f"Département {departement.nom} modifié avec succès!", "success")
            return redirect(url_for('directeur.detail_departement', dept_id=dept_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {str(e)}", "danger")
    
    return render_template('directeur/modifier_departement.html', departement=departement)


@bp.route('/departement/<int:dept_id>/assigner-chef', methods=['GET', 'POST'])
@directeur_required
def assigner_chef_departement(dept_id):
    """Assigner ou changer le chef d'un département"""
    departement = Departement.query.get_or_404(dept_id)

    if request.method == 'POST':
        chef_id = request.form.get('chef_id')
        ancien_chef = departement.chef

        if chef_id:
            nouveau_chef = Enseignant.query.get_or_404(int(chef_id))
            departement.chef_id = int(chef_id)

            try:
                db.session.commit()

                # Message différent selon si c'est une première assignation ou un changement
                if ancien_chef:
                    flash(f"Chef de département changé : {ancien_chef.nom} → {nouveau_chef.nom} {nouveau_chef.prenom}", "success")
                else:
                    flash(f"{nouveau_chef.nom} {nouveau_chef.prenom} a été nommé(e) chef du département {departement.nom}", "success")

                return redirect(url_for('directeur.detail_departement', dept_id=dept_id))
            except Exception as e:
                db.session.rollback()
                flash(f"Erreur : {str(e)}", "danger")
        else:
            # Retirer le chef actuel
            if ancien_chef:
                departement.chef_id = None
                db.session.commit()
                flash(f"{ancien_chef.nom} {ancien_chef.prenom} n'est plus chef de département.", "info")
                return redirect(url_for('directeur.detail_departement', dept_id=dept_id))
            else:
                flash("Aucun enseignant sélectionné.", "warning")

    # Liste des enseignants disponibles
    enseignants = Enseignant.query.filter_by(actif=True).order_by(Enseignant.nom).all()
    return render_template('directeur/assigner_chef_departement.html',
                         departement=departement,
                         enseignants=enseignants)


# =========================================================================
# GESTION FILIÈRES & CLASSES
# =========================================================================
@bp.route('/filieres')
@directeur_required
def liste_filieres():
    filieres = Filiere.query.order_by(Filiere.nom_filiere).all()
    return render_template('directeur/liste_filieres.html', filieres=filieres)


@bp.route('/filiere/ajouter', methods=['GET', 'POST'])
@directeur_required
def ajouter_filiere():
    if request.method == 'POST':
        nom = request.form.get('nom_filiere').strip().upper()
        code = request.form.get('code_filiere', '').strip().upper()
        cycle = request.form.get('cycle')
        departement_id = request.form.get('departement_id')
        type_diplome = request.form.get('type_diplome', 'fondamental')
        description = request.form.get('description', '').strip()

        if not departement_id:
            flash("Vous devez sélectionner un département.", "warning")
            departements = Departement.query.filter_by(active=True).all()
            return render_template('directeur/ajouter_filiere.html', departements=departements)

        # Préfixe type diplôme : F = fondamental, P = professionnel
        type_prefixe = 'F' if type_diplome == 'fondamental' else 'P'

        # Génération code filière : initiales + F/P + année courte
        # Ex: GEC + F = GECF → code filière GECF25
        if not code:
            initiales = "".join([word[0] for word in nom.split() if word])[:3].upper()
            code = f"{initiales}{type_prefixe}{str(datetime.now().year)[-2:]}"

        # Vérification doublon : même nom + même type_diplome dans le même département
        doublon = Filiere.query.filter_by(
            nom_filiere=nom,
            departement_id=int(departement_id),
            type_diplome=type_diplome
        ).first()
        if doublon:
            flash(f"Une filière '{nom}' ({type_diplome}) existe déjà dans ce département.", "warning")
            departements = Departement.query.filter_by(active=True).all()
            return render_template('directeur/ajouter_filiere.html', departements=departements)

        try:
            filiere = Filiere(
                nom_filiere=nom,
                code_filiere=code,
                cycle=cycle,
                departement_id=int(departement_id),
                type_diplome=type_diplome,
                description=description,
                active=True
            )
            db.session.add(filiere)
            db.session.flush()

            # Génération automatique des classes avec préfixe LF/LP/MF/MP
            # LF = Licence Fondamentale, LP = Licence Professionnelle, etc.
            cycle_prefixes = {
                'Licence': 'L',
                'Master':  'M',
                'Doctorat': 'D'
            }
            classes_config = {
                'Licence': [(1,), (2,), (3,)],
                'Master':  [(1,), (2,)],
                'Doctorat': [(1,), (2,), (3,)]
            }
            cp = cycle_prefixes.get(cycle, 'N')  # ex: 'L'
            # Préfixe classe : LF (Licence Fond.) ou LP (Licence Pro.)
            classe_prefixe = f"{cp}{type_prefixe}"  # ex: LF, LP, MF, MP

            if cycle in classes_config:
                for (annee,) in classes_config[cycle]:
                    # nom_classe : ex "LF1 GEC" ou "LP2 INF"
                    nom_classe  = f"{classe_prefixe}{annee} {code}"
                    code_classe = f"{classe_prefixe}{annee}{code}"
                    # Garantir unicité
                    suffix = 0
                    base_code = code_classe
                    while Classe.query.filter_by(code_classe=code_classe).first():
                        suffix += 1
                        code_classe = f"{base_code}-{suffix}"

                    nouvelle_classe = Classe(
                        nom_classe=nom_classe,
                        code_classe=code_classe,
                        cycle=cycle,
                        annee=annee,
                        filiere_id=filiere.id,
                        active=True
                    )
                    db.session.add(nouvelle_classe)

            db.session.commit()
            type_label_fr = 'Fondamentale' if type_diplome == 'fondamental' else 'Professionnelle'
            flash(f"✅ Filière {nom} ({type_label_fr}) créée avec classes {classe_prefixe}1/{classe_prefixe}2…", "success")
            return redirect(url_for('directeur.liste_filieres'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur technique : {str(e)}", "danger")

    departements = Departement.query.filter_by(active=True).all()
    return render_template('directeur/ajouter_filiere.html', departements=departements)


@bp.route('/filiere/<int:filiere_id>')
@directeur_required
def detail_filiere(filiere_id):
    filiere = Filiere.query.get_or_404(filiere_id)
    return render_template('directeur/detail_filiere.html', filiere=filiere)


@bp.route('/filiere/<int:filiere_id>/supprimer', methods=['POST'])
@directeur_required
def supprimer_filiere(filiere_id):
    """Supprimer une filière et ses classes associées"""
    filiere = Filiere.query.get_or_404(filiere_id)
    nom = filiere.nom_filiere
    dept_id = filiere.departement_id

    try:
        # Vérifier s'il y a des étudiants dans les classes de cette filière
        from app.models import Etudiant
        nb_etudiants = 0
        for classe in filiere.classes:
            nb_etudiants += Etudiant.query.filter_by(classe_id=classe.id).count()

        if nb_etudiants > 0:
            flash(f"Impossible de supprimer la filière {nom} : {nb_etudiants} étudiant(s) inscrit(s).", "danger")
            return redirect(url_for('directeur.detail_filiere', filiere_id=filiere_id))

        # Supprimer les classes de la filière (si pas d'étudiants)
        for classe in filiere.classes.all():
            # Détacher les UE liées (many-to-many)
            classe.ues = []
            db.session.delete(classe)

        db.session.delete(filiere)
        db.session.commit()
        flash(f"✅ Filière « {nom} » supprimée avec succès.", "success")

        # Rediriger vers le département si existe, sinon vers la liste
        if dept_id:
            return redirect(url_for('directeur.detail_departement', dept_id=dept_id))
        return redirect(url_for('directeur.liste_filieres'))

    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression : {str(e)}", "danger")
        return redirect(url_for('directeur.detail_filiere', filiere_id=filiere_id))


@bp.route('/filiere/<int:filiere_id>/creer-variante', methods=['POST'])
@directeur_required
def creer_variante_filiere(filiere_id):
    """Créer la version LF ou LP d'une filière existante (extension)"""
    filiere_source = Filiere.query.get_or_404(filiere_id)

    # Déterminer le type opposé
    type_oppose = 'professionnel' if filiere_source.type_diplome == 'fondamental' else 'fondamental'
    type_prefixe = 'P' if type_oppose == 'professionnel' else 'F'

    # Vérifier que la variante n'existe pas déjà
    doublon = Filiere.query.filter_by(
        nom_filiere=filiere_source.nom_filiere,
        departement_id=filiere_source.departement_id,
        type_diplome=type_oppose
    ).first()
    if doublon:
        label = 'Professionnelle' if type_oppose == 'professionnel' else 'Fondamentale'
        flash(f"La version {label} de {filiere_source.nom_filiere} existe déjà.", "warning")
        return redirect(url_for('directeur.detail_filiere', filiere_id=filiere_id))

    try:
        # Générer le code filière pour la variante
        base_code = filiere_source.code_filiere or ''
        # Remplacer F↔P dans le code
        if 'F' in base_code:
            new_code = base_code.replace('F', 'P', 1) if type_oppose == 'professionnel' else base_code
        elif 'P' in base_code:
            new_code = base_code.replace('P', 'F', 1) if type_oppose == 'fondamental' else base_code
        else:
            initiales = "".join([w[0] for w in filiere_source.nom_filiere.split() if w])[:3].upper()
            new_code = f"{initiales}{type_prefixe}{str(datetime.now().year)[-2:]}"

        # Vérifier unicité code
        if Filiere.query.filter_by(code_filiere=new_code).first():
            new_code = f"{new_code}{type_prefixe}"

        # Créer la variante
        nouvelle_filiere = Filiere(
            nom_filiere=filiere_source.nom_filiere,
            code_filiere=new_code,
            cycle=filiere_source.cycle,
            departement_id=filiere_source.departement_id,
            type_diplome=type_oppose,
            description=filiere_source.description,
            active=True
        )
        db.session.add(nouvelle_filiere)
        db.session.flush()

        # Générer automatiquement les classes (LP1, LP2... ou LF1, LF2...)
        cycle_prefixes = {'Licence': 'L', 'Master': 'M', 'Doctorat': 'D'}
        classes_config = {'Licence': [1, 2, 3], 'Master': [1, 2], 'Doctorat': [1, 2, 3]}
        cp = cycle_prefixes.get(filiere_source.cycle, 'N')
        classe_prefixe = f"{cp}{type_prefixe}"

        if filiere_source.cycle in classes_config:
            for annee in classes_config[filiere_source.cycle]:
                nom_classe = f"{classe_prefixe}{annee} {new_code}"
                code_classe = f"{classe_prefixe}{annee}{new_code}"
                suffix = 0
                base = code_classe
                while Classe.query.filter_by(code_classe=code_classe).first():
                    suffix += 1
                    code_classe = f"{base}-{suffix}"
                db.session.add(Classe(
                    nom_classe=nom_classe,
                    code_classe=code_classe,
                    cycle=filiere_source.cycle,
                    annee=annee,
                    filiere_id=nouvelle_filiere.id,
                    active=True
                ))

        db.session.commit()
        label = 'Professionnelle (LP)' if type_oppose == 'professionnel' else 'Fondamentale (LF)'
        flash(f"✅ Version {label} de {filiere_source.nom_filiere} créée avec succès !", "success")
        return redirect(url_for('directeur.detail_filiere', filiere_id=nouvelle_filiere.id))

    except Exception as e:
        db.session.rollback()
        flash(f"Erreur : {str(e)}", "danger")
        return redirect(url_for('directeur.detail_filiere', filiere_id=filiere_id))


# =========================================================================
# CLASSES ASSEMBLÉES (Tronc Commun Départemental)
# =========================================================================
@bp.route('/departement/<int:dept_id>/classe-assemblee/creer', methods=['GET', 'POST'])
@directeur_required
def creer_classe_assemblee(dept_id):
    """Créer une classe assemblée (tronc commun départemental)"""
    departement = Departement.query.get_or_404(dept_id)

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        type_diplome = request.form.get('type_diplome', 'fondamental')
        annee = int(request.form.get('annee', 1) or 1)
        semestres = request.form.get('semestres', 'S1-S2')

        # ============================================
        # VÉRIFICATION ANTI-DOUBLON
        # ============================================
        doublon = Classe.query.filter_by(
            departement_source_id=dept_id,
            est_assemblee=True,
            type_diplome_assemblee=type_diplome,
            annee=annee,
            semestres_assemblee=semestres,
            active=True
        ).first()
        if doublon:
            flash(f"⚠️ Cette classe assemblée existe déjà : {doublon.nom_classe} ({doublon.code_classe}). Pas de doublon autorisé.", "warning")
            return redirect(url_for('directeur.creer_classe_assemblee', dept_id=dept_id))

        if not nom:
            # Générer automatiquement le nom
            type_label = 'LF' if type_diplome == 'fondamental' else 'LP'
            nom = f"{departement.nom} {type_label}{annee} ({semestres})"

        # Générer le code
        type_label = 'LF' if type_diplome == 'fondamental' else 'LP'
        code = f"TC-{departement.code}-{type_label}{annee}"
        suffix = 0
        base_code = code
        while Classe.query.filter_by(code_classe=code).first():
            suffix += 1
            code = f"{base_code}-{suffix}"

        # On a besoin d'une filière "hôte" → prendre la première du département du même type
        filiere_hote = Filiere.query.filter_by(
            departement_id=dept_id,
            type_diplome=type_diplome,
            active=True
        ).first()

        if not filiere_hote:
            flash(f"Aucune filière {type_diplome} dans ce département. Créez-en une d'abord.", "warning")
            return redirect(url_for('directeur.detail_departement', dept_id=dept_id))

        try:
            classe_assemblee = Classe(
                nom_classe=nom,
                code_classe=code,
                cycle=filiere_hote.cycle or 'Licence',
                annee=annee,
                filiere_id=filiere_hote.id,
                active=True,
                est_assemblee=True,
                departement_source_id=dept_id,
                type_diplome_assemblee=type_diplome,
                semestres_assemblee=semestres
            )
            db.session.add(classe_assemblee)
            db.session.commit()

            flash(f"✅ Classe assemblée '{nom}' créée ! Elle apparaît maintenant dans 'Ajouter UE'.", "success")
            return redirect(url_for('directeur.detail_departement', dept_id=dept_id))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {str(e)}", "danger")

    # GET
    filieres = Filiere.query.filter_by(departement_id=dept_id, active=True).all()
    classes_existantes = Classe.query.filter_by(
        departement_source_id=dept_id, est_assemblee=True
    ).all()
    return render_template('directeur/creer_classe_assemblee.html',
                         departement=departement,
                         filieres=filieres,
                         classes_existantes=classes_existantes)


@bp.route('/classe-assemblee/<int:classe_id>/supprimer', methods=['POST'])
@directeur_required
def supprimer_classe_assemblee(classe_id):
    """Supprimer une classe assemblée"""
    classe = Classe.query.get_or_404(classe_id)
    if not classe.est_assemblee:
        flash("Cette classe n'est pas une classe assemblée.", "danger")
        return redirect(request.referrer or url_for('directeur.liste_classes'))

    dept_id = classe.departement_source_id
    try:
        db.session.delete(classe)
        db.session.commit()
        flash("Classe assemblée supprimée.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur : {str(e)}", "danger")

    return redirect(url_for('directeur.detail_departement', dept_id=dept_id))


@bp.route('/classes')
@directeur_required
def liste_classes():
    classes = Classe.query.order_by(Classe.nom_classe).all()
    return render_template('directeur/liste_classes.html', classes=classes)


@bp.route('/classe/<int:classe_id>')
@directeur_required
def detail_classe(classe_id):
    classe = Classe.query.get_or_404(classe_id)
    # Pour les classes assemblées : unifier les étudiants de toutes les classes composantes
    if classe.est_assemblee:
        etudiants = classe.get_etudiants_assembles()
    else:
        etudiants = Etudiant.query.filter_by(classe_id=classe.id, statut_inscription='accepté').all()
    return render_template('directeur/detail_classe.html', classe=classe, etudiants=etudiants)


# =========================================================================
# GESTION ENSEIGNANTS
# =========================================================================
@bp.route('/enseignants')
@directeur_required
def liste_enseignants():
    enseignants = Enseignant.query.order_by(Enseignant.nom).all()
    # Exclure les UE composites mères — seuls les EC/sous-UE sont affectables
    toutes_les_ues = UE.query.filter(db.or_(UE.nature != 'composite', UE.nature == None)).all()
    return render_template('directeur/enseignants.html', enseignants=enseignants, toutes_les_ues=toutes_les_ues)


@bp.route('/enseignant/ajouter', methods=['GET', 'POST'])
@directeur_required
def ajouter_enseignant():
    if request.method == 'POST':
        # 1. Récupération propre des données
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        nom = request.form.get('nom', '')
        prenom = request.form.get('prenom', '')
        grade = request.form.get('grade')
        specialite = request.form.get('specialite')

        # Nouveaux champs
        date_naissance_str = request.form.get('date_naissance')
        sexe = request.form.get('sexe')
        telephone = request.form.get('telephone')
        adresse = request.form.get('adresse')

        # 2. Sécurité : Vérifier si le pseudo existe déjà
        if User.query.filter_by(username=username).first():
            flash("Cet identifiant est déjà utilisé !", "danger")
            return redirect(url_for('directeur.ajouter_enseignant'))

        try:
            # Conversion de la date
            from datetime import datetime
            date_naissance = None
            if date_naissance_str:
                date_naissance = datetime.strptime(date_naissance_str, '%Y-%m-%d').date()

            # ÉTAPE 1 : Créer le compte User
            new_user = User(
                username=username,
                email=email,
                role='ENSEIGNANT'
            )
            # On passe le mot de passe en CLAIR, le setter du modèle s'occupe du hash
            new_user.password = password

            db.session.add(new_user)
            db.session.flush()  # On valide l'ID pour l'étape suivante

            # ÉTAPE 2 : Créer le profil Enseignant rattaché
            new_enseignant = Enseignant(
                user_id=new_user.id,  # LE LIEN SACRÉ
                nom=nom.upper(),
                prenom=prenom.title(),
                date_naissance=date_naissance,
                sexe=sexe,
                telephone=telephone,
                adresse=adresse,
                grade=grade,
                specialite=specialite,
                date_embauche=datetime.utcnow().date(),
                mot_de_passe_initial=password  # Stocker le mot de passe en clair pour le PDF
            )
            db.session.add(new_enseignant)

            # ÉTAPE 3 : On valide la transaction complète
            db.session.commit()

            flash(f"L'enseignant {nom} a été créé et lié avec succès !", "success")
            return redirect(url_for('directeur.liste_enseignants'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur technique : {str(e)}", "danger")
            return redirect(url_for('directeur.ajouter_enseignant'))

    return render_template('directeur/ajouter_enseignant.html')
@bp.route('/enseignant/<int:enseignant_id>')
@directeur_required
def detail_enseignant(enseignant_id):
    """Affiche le profil complet d'un enseignant spécifique"""
    # 1. On cherche l'enseignant ou on affiche une erreur 404
    enseignant = Enseignant.query.get_or_404(enseignant_id)

    # 2. On récupère les UE qui lui sont attribuées
    # Grâce à ta table Many-to-Many, c'est très simple :
    ues_attribuees = enseignant.ues

    return render_template('directeur/detail_enseignant.html',
                           enseignant=enseignant,
                           ues=ues_attribuees)
# =========================================================================
# AFFECTATIONS (RELATION MANY-TO-MANY)
# =========================================================================

# =========================================================================
# GESTION UE & AFFECTATIONS
# =========================================================================
@bp.route('/ues')
@directeur_required
def liste_ues():
    # Ne charger que les UE de premier niveau (pas les EC/sous-UE qui ont un parent_id)
    ues = UE.query.filter(UE.parent_id.is_(None)).order_by(UE.code_ue).all()
    classes = Classe.query.filter_by(active=True).all()  # Pour les filtres éventuels
    return render_template('directeur/liste_ues.html', ues=ues, classes=classes)


@bp.route('/affectations-ues')
@directeur_required
def page_attribuer_ue():
    """Page pour attribuer les UE aux enseignants"""
    # Exclure les UE composites mères — seuls les EC sont affectables
    ues = UE.query.filter(db.or_(UE.nature != 'composite', UE.nature == None)).all()
    enseignants = Enseignant.query.filter_by(actif=True).all()
    etudiants = Etudiant.query.all()
    filieres = Filiere.query.all()
    return render_template('directeur/attribuer_ue.html',
                           ues=ues,
                           enseignants=enseignants,
                           etudiants=etudiants,
                           filieres=filieres)


@bp.route('/ue/ajouter', methods=['GET', 'POST'])
@directeur_required
def ajouter_ue():
    """Créer une nouvelle UE et l'attribuer à des classes (cochage par filière)"""

    def _render_form():
        departements = Departement.query.filter_by(active=True).all()
        # Filieres groupées par type_diplome pour les 2 tableaux
        filieres_fond = Filiere.query.filter_by(active=True, type_diplome='fondamental').order_by(Filiere.nom_filiere).all()
        filieres_pro  = Filiere.query.filter_by(active=True, type_diplome='professionnel').order_by(Filiere.nom_filiere).all()
        # Classes assemblées (tronc commun départemental) — groupées par type
        classes_assemblees_fond = Classe.query.filter_by(
            est_assemblee=True, active=True, type_diplome_assemblee='fondamental'
        ).order_by(Classe.annee).all()
        classes_assemblees_pro = Classe.query.filter_by(
            est_assemblee=True, active=True, type_diplome_assemblee='professionnel'
        ).order_by(Classe.annee).all()
        # Pré-sélection d'une classe (venant du bouton "Créer UE" d'un tronc commun)
        preselect_classe_id = request.args.get('classe_id', type=int)
        return render_template('directeur/ajouter_ue_v2.html',
                               departements=departements,
                               filieres_fond=filieres_fond,
                               filieres_pro=filieres_pro,
                               classes_assemblees_fond=classes_assemblees_fond,
                               classes_assemblees_pro=classes_assemblees_pro,
                               preselect_classe_id=preselect_classe_id)

    if request.method == 'POST':
        code_ue      = request.form.get('code_ue', '').strip().upper()
        nom_ue       = request.form.get('nom_ue', '').strip()
        semestre     = request.form.get('semestre', 'S1')
        categorie    = request.form.get('categorie', 'fondamentale')
        nature       = request.form.get('nature', 'simple')
        type_affectation = request.form.get('type_affectation', 'specifique')
        credits      = int(request.form.get('credits', 3) or 3)
        description  = request.form.get('description', '').strip()

        # Classes cochées (attribution aux classes, pas aux filières)
        classes_ids = request.form.getlist('classes_ids[]')

        if not code_ue or not nom_ue:
            flash("Le code et le nom sont obligatoires.", "warning")
            return _render_form()

        # UE libre : pas de classe obligatoire
        if categorie != 'libre' and not classes_ids and type_affectation != 'libre':
            flash("Sélectionnez au moins une classe.", "warning")
            return _render_form()

        # Spécifique = 1 seule classe
        if type_affectation == 'specifique' and len(classes_ids) > 1:
            flash("Mode Spécifique : une seule classe autorisée.", "warning")
            return _render_form()

        # Tronc commun = au moins 2 classes
        if type_affectation == 'tronc_commun' and len(classes_ids) < 2:
            flash("Tronc Commun : sélectionnez au moins 2 classes.", "warning")
            return _render_form()

        try:
            heures      = credits * 12
            coefficient = float(credits)

            if nature == 'simple':
                ue = UE(
                    code_ue=code_ue,
                    nom_ue=nom_ue,
                    intitule=nom_ue,
                    credits=credits,
                    coefficient=coefficient,
                    heures=heures,
                    semestre=semestre,
                    categorie=categorie,
                    nature='simple',
                    type_structure='ue_simple',
                    type_affectation=type_affectation,
                    est_ouverte_a_tous=(categorie == 'libre'),
                    classe_id=int(classes_ids[0]) if classes_ids and type_affectation == 'specifique' else None,
                    description=description,
                    active=True
                )
                db.session.add(ue)
                db.session.flush()

                # Lier aux classes (many-to-many)
                for cid in classes_ids:
                    classe = Classe.query.get(int(cid))
                    if classe:
                        ue.classes.append(classe)

                db.session.commit()
                flash(f"✅ UE {code_ue} créée et attribuée à {len(classes_ids)} classe(s).", "success")

            elif nature == 'composite':
                nom_final     = request.form.get('nom_composite_final', nom_ue).strip() or nom_ue
                sous_ues_count = int(request.form.get('sous_ues_count', 2) or 2)

                sous_ues_data = []
                for i in range(1, sous_ues_count + 1):
                    nom_s     = request.form.get(f'sous_ue_{i}_nom', '').strip()
                    credits_s = request.form.get(f'sous_ue_{i}_credits', '')
                    if nom_s and credits_s:
                        sous_ues_data.append({'nom': nom_s, 'credits': int(credits_s), 'ordre': i})

                if len(sous_ues_data) < 2:
                    flash("UE Composite : au moins 2 éléments constitutifs requis.", "warning")
                    return _render_form()

                credits_total = sum(s['credits'] for s in sous_ues_data)

                # UE mère
                ue_mere = UE(
                    code_ue=code_ue,
                    nom_ue=nom_final,
                    intitule=nom_final,
                    credits=credits_total,
                    coefficient=float(credits_total),
                    heures=credits_total * 12,
                    semestre=semestre,
                    categorie=categorie,
                    nature='composite',
                    type_structure='ue_composite',
                    type_affectation=type_affectation,
                    est_ouverte_a_tous=(categorie == 'libre'),
                    classe_id=int(classes_ids[0]) if classes_ids and type_affectation == 'specifique' else None,
                    description=description,
                    active=True
                )
                db.session.add(ue_mere)
                db.session.flush()

                for cid in classes_ids:
                    classe = Classe.query.get(int(cid))
                    if classe:
                        ue_mere.classes.append(classe)

                # Sous-UE (EC)
                for s in sous_ues_data:
                    ue_fille = UE(
                        code_ue=f"{s['ordre']}{code_ue}",
                        nom_ue=s['nom'],
                        intitule=s['nom'],
                        credits=s['credits'],
                        coefficient=float(s['credits']),
                        heures=s['credits'] * 12,
                        semestre=semestre,
                        categorie=categorie,
                        nature='simple',
                        type_structure='element_constitutif',
                        type_affectation=type_affectation,
                        parent_id=ue_mere.id,
                        ordre=s['ordre'],
                        active=True
                    )
                    db.session.add(ue_fille)
                    db.session.flush()
                    for cid in classes_ids:
                        classe = Classe.query.get(int(cid))
                        if classe:
                            ue_fille.classes.append(classe)

                db.session.commit()
                flash(f"✅ UE Composite {code_ue} créée ({len(sous_ues_data)} EC, {credits_total} crédits) pour {len(classes_ids)} classe(s).", "success")

            return redirect(url_for('directeur.liste_ues'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {str(e)}", "danger")
            import traceback; traceback.print_exc()

    return _render_form()


@bp.route('/ue/<int:ue_id>')
@directeur_required
def detail_ue(ue_id):
    ue = UE.query.get_or_404(ue_id)
    enseignants = Enseignant.query.filter_by(actif=True).all()
    notes_valides = [n.note for n in ue.notes if n.note is not None]
    moyenne = round(sum(notes_valides) / len(notes_valides), 2) if notes_valides else None
    return render_template('directeur/detail_ue.html', ue=ue, enseignants=enseignants, moyenne_ue=moyenne)


@bp.route('/ue/<int:ue_id>/affecter/<int:enseignant_id>', methods=['POST'])
@directeur_required
def affecter_ue_a_prof(ue_id, enseignant_id):

    """Affecte un enseignant à une UE depuis la page de détail de l'UE"""
    ue = UE.query.get_or_404(ue_id)
    enseignant = Enseignant.query.get_or_404(enseignant_id)

    try:
        # Vérifier si l'affectation existe déjà
        if enseignant in ue.enseignants:
            flash(f"{enseignant.nom_complet} est déjà affecté(e) à cette UE.", "info")
        else:
            # Ajouter l'enseignant à l'UE
            ue.enseignants.append(enseignant)
            db.session.commit()
            flash(f"✅ {enseignant.nom_complet} a été affecté(e) à l'UE {ue.intitule}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'affectation : {str(e)}", "danger")

    return redirect(url_for('directeur.detail_ue', ue_id=ue.id))


@bp.route('/ue/supprimer/<int:ue_id>', methods=['POST'])
@directeur_required
def supprimer_ue(ue_id):
    ue = UE.query.get_or_404(ue_id)
    try:
        db.session.delete(ue)
        db.session.commit()
        flash("UE supprimée.", "info")
    except IntegrityError:
        db.session.rollback()
        flash("Impossible de supprimer cette UE car elle contient des notes ou des inscriptions.", "danger")

    return redirect(url_for('directeur.liste_ues'))


@bp.route('/affectations')
@directeur_required
def affectations():
    # Exclure les UE composites mères — seuls les EC/sous-UE sont affectables
    ues = UE.query.filter(db.or_(UE.nature != 'composite', UE.nature == None)).all()
    enseignants = Enseignant.query.filter_by(actif=True).all()
    return render_template('directeur/affectations.html', ues=ues, enseignants=enseignants)


# NOUVELLE ROUTE : Affectation simplifiée avec checkboxes
@bp.route('/affectations-simplifiees')
@directeur_required
def affectations_simplifiees():
    """Page d'affectation simplifiée avec checkboxes"""
    # Exclure les UE composites mères — seuls les EC/sous-UE sont affectables
    ues = UE.query.filter(db.or_(UE.nature != 'composite', UE.nature == None)).order_by(UE.code_ue).all()
    enseignants = Enseignant.query.filter_by(actif=True).order_by(Enseignant.nom).all()

    # Calculer les UE non affectées (sans aucun enseignant)
    # INCLURE les UE Tronc Commun sans prof
    ues_non_affectees = [ue for ue in ues if len(ue.enseignants) == 0]

    # Séparer les troncs communs des autres
    troncs_communs_non_affectes = [ue for ue in ues_non_affectees if ue.type_affectation == 'tronc_commun']
    ue_filles_non_affectees = [ue for ue in ues_non_affectees if ue.type_affectation != 'tronc_commun']

    return render_template('directeur/affecter_ues_enseignants.html',
                         ues=ues,
                         enseignants=enseignants,
                         ues_non_affectees=ues_non_affectees,
                         troncs_communs_non_affectes=troncs_communs_non_affectes,
                         ue_filles_non_affectees=ue_filles_non_affectees)


@bp.route('/enseignant/<int:enseignant_id>/affecter-ues', methods=['POST'])
@directeur_required
def affecter_ues_a_enseignant(enseignant_id):
    """Met à jour les affectations UE pour un enseignant"""
    enseignant = Enseignant.query.get_or_404(enseignant_id)

    # Récupérer les UE cochées
    ues_ids = request.form.getlist('ues_ids')
    ues_ids = [int(ue_id) for ue_id in ues_ids]

    try:
        # Supprimer toutes les affectations actuelles
        enseignant.ues.clear()

        # Ajouter les nouvelles affectations
        for ue_id in ues_ids:
            ue = UE.query.get(ue_id)
            if ue:
                enseignant.ues.append(ue)

        db.session.commit()

        nb_ues = len(ues_ids)
        flash(f"✅ Affectations mises à jour pour {enseignant.nom} {enseignant.prenom} : {nb_ues} UE(s)", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"❌ Erreur lors de la mise à jour : {str(e)}", "danger")

    return redirect(url_for('directeur.affectations_simplifiees'))


@bp.route('/affectations/creer', methods=['POST'])
@directeur_required
def creer_affectation():
    ens_id = request.form.get('enseignant_id')
    ue_id = request.form.get('ue_id')

    ens = Enseignant.query.get_or_404(ens_id)
    ue = UE.query.get_or_404(ue_id)

    # Sécurité : On vérifie que l'UE appartient bien à une classe
    if not ue.classe_id:
        flash(f"Erreur : L'UE {ue.intitule} n'est rattachée à aucune classe.", "danger")
        return redirect(url_for('directeur.affectations'))

    if ens not in ue.enseignants:
        ue.enseignants.append(ens)
        db.session.commit()
        # Message plus précis pour le Directeur
        flash(f"Affectation réussie : {ens.nom} enseignera {ue.intitule} en {ue.classe.nom_classe}.", "success")
    else:
        flash("Cette affectation existe déjà.", "info")

    return redirect(url_for('directeur.affectations'))


@bp.route('/affectation/supprimer/<int:ue_id>/<int:ens_id>')
@directeur_required
def supprimer_affectation(ue_id, ens_id):
    ue = UE.query.get_or_404(ue_id)
    ens = Enseignant.query.get_or_404(ens_id)

    if ens in ue.enseignants:
        ue.enseignants.remove(ens)
        db.session.commit()
        flash("Affectation supprimée.", "info")

    return redirect(request.referrer or url_for('directeur.affectations'))


@bp.route('/attribuer_ue/<int:ue_id>', methods=['POST'])
@directeur_required
def attribuer_ue(ue_id):
    """Attribuer une UE à un enseignant via un formulaire simple"""
    ue = UE.query.get_or_404(ue_id)
    enseignant_id = request.form.get('enseignant_id')

    if not enseignant_id:
        flash("Veuillez sélectionner un enseignant.", "warning")
        return redirect(url_for('directeur.affectations'))

    try:
        enseignant = Enseignant.query.get_or_404(enseignant_id)

        # Vérifier que l'affectation n'existe pas déjà
        if enseignant not in ue.enseignants:
            ue.enseignants.append(enseignant)
            db.session.commit()
            flash(f"✓ {enseignant.nom} a été attribué à {ue.intitule}.", "success")
        else:
            flash("Cet enseignant est déjà attribué à cette UE.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur : {str(e)}", "danger")

    return redirect(url_for('directeur.affectations'))


# =========================================================================
# GESTION ÉTUDIANTS (VALIDATION & INSCRIPTION)
# =========================================================================
@bp.route('/etudiants')
@directeur_required
def liste_etudiants():
    statut = request.args.get('statut', 'tous')
    query = Etudiant.query
    if statut != 'tous':
        query = query.filter_by(statut_inscription=statut)

    etudiants = query.order_by(Etudiant.nom).all()
    classes = Classe.query.filter_by(active=True).all()

    return render_template('directeur/etudiants.html',
                           etudiants=etudiants,
                           classes=classes,
                           statut_filtre=statut)


@bp.route('/etudiant/<int:etudiant_id>')
@directeur_required
def detail_etudiant(etudiant_id):
    from app.models import Etudiant, InscriptionUE, Note

    etudiant = Etudiant.query.get_or_404(etudiant_id)

    # 1. Récupérer les inscriptions aux UEs pour cet étudiant
    inscriptions = InscriptionUE.query.filter_by(etudiant_id=etudiant.id).all()

    # 2. Calculer le total des crédits validés (UE avec note >= 10)
    notes = Note.query.filter_by(etudiant_id=etudiant.id).all()

    total_credits = 0
    somme_notes = 0
    nb_notes = 0

    for n in notes:
        if n.note is not None:
            somme_notes += n.note
            nb_notes += 1
            if n.note >= 10:
                # On récupère les crédits via la relation avec l'UE
                total_credits += n.ue.credits if n.ue else 0

    # 3. Calcul de la moyenne générale
    moyenne_gen = somme_notes / nb_notes if nb_notes > 0 else None

    # ON ENVOIE TOUT AU TEMPLATE (C'est ici que 'credits' est défini)
    return render_template('directeur/detail_etudiant.html',
                           etudiant=etudiant,
                           inscriptions=inscriptions,
                           notes=notes,
                           credits=total_credits,  # La variable manquante
                           moyenne=moyenne_gen)  # La variable pour le header

@bp.route('/etudiant/<int:etudiant_id>/valider', methods=['POST'])
@directeur_required
def valider_etudiant(etudiant_id):
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    classe_id = request.form.get('classe_id')

    if not classe_id:
        flash("Veuillez affecter une classe pour valider l'inscription.", "warning")
        return redirect(url_for('directeur.liste_etudiants', statut='en_attente'))

    try:
        classe = Classe.query.get(classe_id)

        # 1. GÉNÉRATION DU MATRICULE DÉFINITIF (Ex: ETU-2026-0042)
        annee_actuelle = datetime.now().year
        # zfill(4) permet d'avoir 0042 au lieu de 42 pour un look plus pro
        etudiant.matricule = f"ETU-{annee_actuelle}-{str(etudiant.id).zfill(4)}"

        # 2. MISE À JOUR DU STATUT ET DE LA CLASSE
        etudiant.classe_id = int(classe_id)
        etudiant.statut_inscription = 'accepté'
        etudiant.date_validation = datetime.utcnow()

        # 3. INSCRIPTION AUTOMATIQUE AUX UE DE LA CLASSE
        # On inscrit l'étudiant à toutes les UE rattachées à sa nouvelle classe
        for ue in classe.ues:
            # On vérifie si l'inscription n'existe pas déjà (sécurité)
            if not InscriptionUE.query.filter_by(etudiant_id=etudiant.id, ue_id=ue.id).first():
                nouvelle_ins = InscriptionUE(
                    etudiant_id=etudiant.id,
                    ue_id=ue.id,
                    annee_academique=f"{annee_actuelle}-{annee_actuelle + 1}",
                    statut='validé'
                )
                db.session.add(nouvelle_ins)

        db.session.commit()
        flash(f"Succès ! {etudiant.prenom} a reçu le matricule {etudiant.matricule}.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la validation : {str(e)}", "danger")

    return redirect(url_for('directeur.liste_etudiants'))


@bp.route('/valider-inscriptions-auto', methods=['POST'])
@directeur_required
def valider_inscriptions_auto():
    """Valide automatiquement les inscriptions avec l'IA Gemini"""
    from app.services.validation_ia import ValidationIA

    # Récupérer tous les étudiants en attente
    etudiants_attente = Etudiant.query.filter_by(statut_inscription='en_attente').all()

    if not etudiants_attente:
        flash("Aucune inscription en attente.", "info")
        return redirect(url_for('directeur.liste_etudiants'))

    ia = ValidationIA()
    acceptes = 0
    refuses = 0

    for etudiant in etudiants_attente:
        # Évaluer avec l'IA
        resultat = ia.evaluer_inscription(etudiant)

        # Stocker l'évaluation
        etudiant.evaluation_ia = str(resultat)

        if resultat['decision'] == 'accepte':
            # Trouver une classe de la filière
            classe = Classe.query.filter_by(filiere_id=etudiant.filiere_id, active=True).first()

            if classe:
                # Générer le matricule
                annee_actuelle = datetime.now().year
                etudiant.matricule = f"ETU-{annee_actuelle}-{str(etudiant.id).zfill(4)}"

                # Valider
                etudiant.classe_id = classe.id
                etudiant.statut_inscription = 'accepté'
                etudiant.date_validation = datetime.utcnow()

                # Inscrire aux UEs de la classe
                for ue in classe.ues:
                    if not InscriptionUE.query.filter_by(etudiant_id=etudiant.id, ue_id=ue.id).first():
                        nouvelle_ins = InscriptionUE(
                            etudiant_id=etudiant.id,
                            ue_id=ue.id,
                            annee_academique=Config.ANNEE_ACADEMIQUE_ACTUELLE,
                            statut='validé'
                        )
                        db.session.add(nouvelle_ins)

                acceptes += 1
        else:
            # Refuser
            etudiant.statut_inscription = 'refusé'
            refuses += 1

    db.session.commit()

    flash(f"✅ Validation automatique terminée ! {acceptes} accepté(s), {refuses} refusé(s) (moyenne < 12/20)", "success")
    return redirect(url_for('directeur.liste_etudiants'))


@bp.route('/statistiques/export')
@directeur_required
def export_statistiques_file():
    """Génère un fichier Excel des statistiques"""
    # Recalcul des données pour l'export
    stats_data = {
        'total_etudiants': Etudiant.query.filter_by(statut_inscription='accepté').count(),
        'total_enseignants': Enseignant.query.filter_by(actif=True).count(),
        'total_ues': UE.query.count(),
        'total_classes': Classe.query.count(),
        'moyennes_classes': []  # À implémenter si besoin
    }

    filename = export_statistiques_excel(stats_data)
    return send_file(filename, as_attachment=True, download_name="rapport_statistique.xlsx")


# =========================================================================
# ANNONCES & GUIDE D'ORIENTATION
# =========================================================================
@bp.route('/annonces')
@directeur_required
def liste_annonces():
    """Liste de toutes les annonces/articles"""
    annonces = Annonce.query.order_by(Annonce.date_publication.desc()).all()
    return render_template('directeur/liste_annonces.html', annonces=annonces)


@bp.route('/annonce/publier', methods=['GET', 'POST'])
@directeur_required
def publier_annonce():
    """Publier une annonce, un article ou un guide d'orientation"""
    if request.method == 'POST':
        titre = request.form.get('titre', '').strip()
        contenu = request.form.get('contenu', '').strip()
        categorie = request.form.get('categorie', 'article')
        visible_public = request.form.get('visible_public') == 'on'
        visible_etudiants = request.form.get('visible_etudiants') == 'on'
        visible_enseignants = request.form.get('visible_enseignants') == 'on'

        if not titre or not contenu:
            flash("Le titre et le contenu sont obligatoires.", "warning")
            return render_template('directeur/publier_annonce.html')

        # Upload fichier joint (PDF, DOC, etc.)
        fichier_path = None
        fichier = request.files.get('fichier_joint')
        if fichier and fichier.filename:
            from werkzeug.utils import secure_filename
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'annonces')
            os.makedirs(upload_dir, exist_ok=True)
            filename = secure_filename(fichier.filename)
            # Ajouter timestamp pour unicité
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{int(datetime.now().timestamp())}{ext}"
            fichier.save(os.path.join(upload_dir, filename))
            fichier_path = f"uploads/annonces/{filename}"

        try:
            annonce = Annonce(
                titre=titre,
                contenu=contenu,
                categorie=categorie,
                visible_public=visible_public,
                visible_etudiants=visible_etudiants,
                visible_enseignants=visible_enseignants,
                fichier_joint=fichier_path,
                auteur_id=current_user.id
            )
            db.session.add(annonce)
            db.session.commit()

            type_label = {'article': 'Article', 'guide': 'Guide d\'orientation', 'actualite': 'Actualité'}.get(categorie, 'Publication')
            flash(f"✅ {type_label} « {titre} » publié avec succès !", "success")
            return redirect(url_for('directeur.liste_annonces'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {str(e)}", "danger")

    return render_template('directeur/publier_annonce.html')


@bp.route('/annonce/<int:annonce_id>/supprimer', methods=['POST'])
@directeur_required
def supprimer_annonce(annonce_id):
    """Supprimer une annonce"""
    annonce = Annonce.query.get_or_404(annonce_id)
    titre = annonce.titre
    # Supprimer le fichier joint si existe
    if annonce.fichier_joint:
        filepath = os.path.join(current_app.root_path, 'static', annonce.fichier_joint)
        if os.path.exists(filepath):
            os.remove(filepath)
    db.session.delete(annonce)
    db.session.commit()
    flash(f"✅ « {titre} » supprimé.", "success")
    return redirect(url_for('directeur.liste_annonces'))

@bp.route('/ue/modifier/<int:ue_id>', methods=['GET', 'POST'])
@directeur_required
def modifier_ue(ue_id):
    ue = UE.query.get_or_404(ue_id)
    classes = Classe.query.filter_by(active=True).all()

    if request.method == 'POST':
        try:
            ue.code_ue = request.form.get('code_ue').upper()
            ue.intitule = request.form.get('intitule')
            ue.credits = int(request.form.get('credits'))
            ue.coefficient = int(request.form.get('coefficient'))
            ue.heures = int(request.form.get('heures'))
            ue.classe_id = int(request.form.get('classe_id'))

            db.session.commit()
            flash("L'UE a été modifiée avec succès.", "success")
            return redirect(url_for('directeur.liste_ues'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la modification : {str(e)}", "danger")

    return render_template('directeur/modifier_ue.html', ue=ue, classes=classes)

@bp.route('/etudiants/export')
@directeur_required
def export_etudiants():
    # SÉCURITÉ : Vérifier si le dossier existe, sinon le créer
    export_path = os.path.join(current_app.root_path, 'static', 'exports')
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    etudiants = Etudiant.query.all()
    try:
        filename = export_etudiants_excel(etudiants)
        return send_file(filename, as_attachment=True, download_name=f"liste_etudiants_{datetime.now().strftime('%d_%m_%Y')}.xlsx")
    except Exception as e:
        flash(f"Erreur lors de la génération du fichier : {str(e)}", "danger")
        return redirect(url_for('directeur.statistiques'))


@bp.route('/enseignant/<int:enseignant_id>/imprimer')
@directeur_required
def imprimer_fiche_enseignant(enseignant_id):
    enseignant = Enseignant.query.get_or_404(enseignant_id)
    user = User.query.get(enseignant.user_id)

    # Utiliser le mot de passe réel stocké lors de la création
    # Si pas disponible (anciens comptes), générer un par défaut
    password_display = enseignant.mot_de_passe_initial or f"{enseignant.prenom.lower()}{enseignant.nom[:4].lower()}2026"

    date_edition = datetime.now().strftime('%d/%m/%Y')

    # Récupérer la config pour le cachet
    from app.models import ConfigurationEcole
    config = ConfigurationEcole.query.first()

    return render_template('directeur/fiche_enseignant_print.html',
                           enseignant=enseignant, user=user,
                           password=password_display, date_edition=date_edition,
                           config=config)

# =========================================================
# 2. GESTION DES DIPLÔMES
# =========================================================
@bp.route('/gestion-diplomes')
@directeur_required
def gestion_diplomes():
    # On récupère les étudiants qui n'ont pas encore leur diplôme généré
    # Et qui ont une moyenne >= 10 (Logique métier)
    etudiants = Etudiant.query.all()
    diplomables = []

    for e in etudiants:
        # Calcul moyenne
        notes = [n.note for n in e.notes if n.note is not None]
        moyenne = sum(notes) / len(notes) if notes else 0

        # Si moyenne ok, on l'ajoute à la liste
        if moyenne >= 10:
            diplome_existe = Diplome.query.filter_by(etudiant_id=e.id).first()
            diplomables.append({
                'etudiant': e,
                'moyenne': round(moyenne, 2),
                'deja_delivre': diplome_existe is not None
            })

    return render_template('directeur/diplomes.html', diplomables=diplomables)


@bp.route('/generer-diplome/<int:etudiant_id>')
@directeur_required
def generer_diplome(etudiant_id):
    etudiant = Etudiant.query.get_or_404(etudiant_id)

    # Import des styles élégants
    from app.utils.pdf_styles import PolytechColors, format_date

    # 1. Enregistrer le diplôme en base si pas fait
    diplome = Diplome.query.filter_by(etudiant_id=etudiant.id).first()
    if not diplome:
        num_serie = f"DIP-2026-{etudiant.id:04d}"

        # Calcul mention
        notes = [n.note for n in etudiant.notes if n.note is not None]
        moy = sum(notes) / len(notes) if notes else 0
        mention = "Passable"
        if moy >= 12: mention = "Assez Bien"
        if moy >= 14: mention = "Bien"
        if moy >= 16: mention = "Très Bien"

        diplome = Diplome(etudiant_id=etudiant.id, numero_serie=num_serie, mention=mention)
        db.session.add(diplome)
        db.session.commit()

    # 2. Génération du PDF (Format Paysage) - Version Élégante
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    # === FOND ET BORDURES ORNEMENTALES ===

    # Fond très léger bleu
    c.setFillColor(colors.HexColor('#f8fafc'))
    c.rect(0, 0, width, height, stroke=0, fill=1)

    # Triple cadre ornemental élégant
    # Cadre externe - Or
    c.setStrokeColor(PolytechColors.GOLD)
    c.setLineWidth(8)
    c.rect(25, 25, width - 50, height - 50, stroke=1, fill=0)

    # Cadre moyen - Bleu foncé
    c.setStrokeColor(PolytechColors.BLUE_DARK)
    c.setLineWidth(3)
    c.rect(35, 35, width - 70, height - 70, stroke=1, fill=0)

    # Cadre interne - Or fin
    c.setStrokeColor(PolytechColors.GOLD_LIGHT)
    c.setLineWidth(1.5)
    c.rect(42, 42, width - 84, height - 84, stroke=1, fill=0)

    # Motifs décoratifs dans les coins
    corner_size = 30
    for x, y in [(50, height-50), (width-50, height-50), (50, 50), (width-50, 50)]:
        c.setFillColor(PolytechColors.GOLD_LIGHT)
        c.setFillAlpha(0.3)
        c.circle(x, y, corner_size, stroke=0, fill=1)
        c.setFillAlpha(1)

    # === EN-TÊTE INSTITUTIONNEL ===

    # Logo stylisé (étoile académique)
    c.setFillColor(PolytechColors.BLUE_DARK)
    star_y = height - 70
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(width / 2, star_y, "⭐")

    # Nom de l'institution
    c.setFont("Times-Bold", 38)
    c.setFillColor(PolytechColors.BLUE_DARK)
    c.drawCentredString(width / 2, height - 120, "POLYTECH ACADEMY")

    # Sous-titre institution
    c.setFont("Helvetica", 13)
    c.setFillColor(PolytechColors.GRAY_DARK)
    c.drawCentredString(width / 2, height - 145, "INSTITUT POLYTECHNIQUE DE HAUTE TECHNOLOGIE")

    # Devise dorée
    c.setFont("Times-Italic", 11)
    c.setFillColor(PolytechColors.GOLD)
    c.drawCentredString(width / 2, height - 165, "Excellence • Innovation • Avenir")

    # Ligne de séparation élégante
    c.setStrokeColor(PolytechColors.GOLD)
    c.setLineWidth(2)
    c.line(width/2 - 200, height - 180, width/2 + 200, height - 180)

    # === TYPE DE DOCUMENT ===

    c.setFont("Times-Bold", 42)
    c.setFillColor(PolytechColors.BLUE_DARK)
    c.drawCentredString(width / 2, height - 230, "DIPLÔME D'INGÉNIEUR")

    # Fond décoratif pour le diplôme
    c.setFillColor(PolytechColors.GOLD_LIGHT)
    c.setFillAlpha(0.1)
    c.roundRect(width/2 - 250, height - 250, 500, 50, 10, stroke=0, fill=1)
    c.setFillAlpha(1)

    # === FORMULE OFFICIELLE ===

    c.setFont("Times-Italic", 18)
    c.setFillColor(PolytechColors.GRAY_DARK)
    c.drawCentredString(width / 2, height - 280, "Le Directeur Général de l'Institut certifie que")

    # === NOM DU DIPLÔMÉ (élément central) ===

    # Fond coloré pour le nom
    c.setFillColor(PolytechColors.BLUE_DARK)
    c.setFillAlpha(0.05)
    c.roundRect(width/2 - 300, height - 345, 600, 55, 15, stroke=0, fill=1)
    c.setFillAlpha(1)

    # Nom complet en majuscules
    nom_complet = f"{etudiant.nom.upper()} {etudiant.prenom.upper()}"
    c.setFont("Helvetica-Bold", 34)
    c.setFillColor(PolytechColors.BLUE_DARK)
    c.drawCentredString(width / 2, height - 330, nom_complet)

    # === INFORMATIONS PERSONNELLES ===

    date_naissance_str = format_date(etudiant.date_naissance) if etudiant.date_naissance else "Non renseignée"
    filiere_nom = etudiant.filiere_objet.nom_filiere if etudiant.filiere_objet else "Génie Logiciel"

    c.setFont("Helvetica", 14)
    c.setFillColor(PolytechColors.GRAY_DARK)
    c.drawCentredString(width / 2, height - 370, f"Né(e) le {date_naissance_str}")

    # === DÉCLARATION ACADÉMIQUE ===

    c.setFont("Times-Roman", 16)
    c.setFillColor(PolytechColors.GRAY_DARK)
    c.drawCentredString(width / 2, height - 410,
                       "A satisfait à toutes les épreuves et validé l'ensemble des enseignements")
    c.drawCentredString(width / 2, height - 432,
                       "requis pour l'obtention du grade de")

    # === GRADE OBTENU (très mis en valeur) ===

    # Fond or pour le grade
    c.setFillColor(PolytechColors.GOLD)
    c.setFillAlpha(0.15)
    c.roundRect(width/2 - 280, height - 480, 560, 45, 12, stroke=0, fill=1)
    c.setFillAlpha(1)

    c.setFont("Times-Bold", 26)
    c.setFillColor(PolytechColors.BLUE_DARK)
    grade_text = f"INGÉNIEUR EN {filiere_nom.upper()}"
    c.drawCentredString(width / 2, height - 470, grade_text)

    # === MENTION ===

    # Encadré élégant pour la mention
    mention_colors = {
        "Très Bien": PolytechColors.SUCCESS,
        "Bien": PolytechColors.INFO,
        "Assez Bien": PolytechColors.WARNING,
        "Passable": PolytechColors.GRAY_DARK
    }
    mention_color = mention_colors.get(diplome.mention, PolytechColors.GRAY_DARK)

    c.setFillColor(mention_color)
    c.setFillAlpha(0.15)
    c.roundRect(width/2 - 150, height - 520, 300, 35, 10, stroke=0, fill=1)
    c.setFillAlpha(1)

    c.setFont("Times-Bold", 20)
    c.setFillColor(mention_color)
    c.drawCentredString(width / 2, height - 512, f"Mention : {diplome.mention.upper()}")

    # === PIED DE PAGE OFFICIEL ===

    y_footer = 75

    # Informations administratives à gauche
    c.setFont("Helvetica", 11)
    c.setFillColor(PolytechColors.GRAY_DARK)
    c.drawString(80, y_footer + 45, f"Fait à Lomé, le {datetime.now().strftime('%d/%m/%Y')}")
    c.drawString(80, y_footer + 25, f"N° d'enregistrement : {diplome.numero_serie}")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(PolytechColors.GRAY)
    c.drawString(80, y_footer + 5, "République Togolaise • Ministère de l'Enseignement Supérieur")

    # Signature à droite
    c.setFont("Times-Bold", 13)
    c.setFillColor(PolytechColors.BLUE_DARK)
    c.drawRightString(width - 80, y_footer + 45, "Le Directeur Général")

    c.setFont("Times-BoldItalic", 15)
    c.setFillColor(colors.black)
    c.drawRightString(width - 80, y_footer + 15, "Prof. Kstar de la KARTZ")

    # Ligne de signature
    c.setStrokeColor(PolytechColors.GRAY_LIGHT)
    c.setLineWidth(1)
    c.line(width - 220, y_footer + 10, width - 80, y_footer + 10)

    # === SCEAU OFFICIEL (Image réelle si disponible) ===

    sceau_x = 150
    sceau_y = 100

    from app.models import ConfigurationEcole as CfgEcole
    cfg = CfgEcole.query.first()
    cachet_drawn = False
    if cfg and cfg.cachet_path:
        try:
            cachet_img_path = os.path.join(current_app.root_path, 'static', cfg.cachet_path)
            if os.path.exists(cachet_img_path):
                c.drawImage(cachet_img_path, sceau_x - 100, sceau_y - 100, width=200, height=200,
                           preserveAspectRatio=True, mask='auto')
                cachet_drawn = True
        except:
            pass

    if not cachet_drawn:
        # Fallback : cercle dessiné
        c.setStrokeColor(PolytechColors.GOLD)
        c.setLineWidth(5)
        c.circle(sceau_x, sceau_y, 65, stroke=1, fill=0)
        c.setFillColor(PolytechColors.GOLD)
        c.setFillAlpha(0.2)
        c.circle(sceau_x, sceau_y, 60, stroke=0, fill=1)
        c.setFillAlpha(1)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(PolytechColors.GOLD)
        c.drawCentredString(sceau_x, sceau_y + 8, "SCEAU")
        c.drawCentredString(sceau_x, sceau_y - 5, "OFFICIEL")
        c.setFont("Helvetica", 7)
        c.drawCentredString(sceau_x, sceau_y - 15, "2026")
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(PolytechColors.GOLD)
        c.drawCentredString(sceau_x, sceau_y + 22, "★")

    # === FILIGRANE SÉCURISÉ ===

    c.setFont("Helvetica", 8)
    c.setFillColor(PolytechColors.GRAY_LIGHT)
    c.setFillAlpha(0.3)
    for i in range(5):
        for j in range(3):
            c.drawString(100 + i*150, 150 + j*150, "POLYTECH • AUTHENTIQUE")
    c.setFillAlpha(1)

    c.showPage()
    c.save()
    buffer.seek(0)

    filename = f"Diplome_{etudiant.nom}_{etudiant.prenom}_{datetime.now().strftime('%Y')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename)




@bp.route('/statistiques')
@directeur_required
def statistiques():
    # ==========================================
    # 1. CHIFFRES GLOBAUX (KPIs)
    # ==========================================
    total_etudiants = Etudiant.query.count()
    total_profs = Enseignant.query.count()
    total_classes = Classe.query.count()
    total_ues = UE.query.count()

    # Moyenne générale précise de l'école
    # On calcule la moyenne de TOUTES les notes valides en base
    result_avg = db.session.query(func.avg(Note.note)).scalar()
    moyenne_ecole = round(result_avg, 2) if result_avg else 0

    # ==========================================
    # 2. ANALYSE DÉTAILLÉE DES ÉTUDIANTS
    # ==========================================
    etudiants = Etudiant.query.all()
    admis = 0
    ajournes = 0
    liste_complete_etudiants = []

    for e in etudiants:
        # Récupération des notes existantes
        notes = [n.note for n in e.notes if n.note is not None]

        if notes:
            moy = sum(notes) / len(notes)
            statut = 'Admis' if moy >= 10 else 'Ajourné'
            if moy >= 10:
                admis += 1
            else:
                ajournes += 1
        else:
            moy = 0
            statut = 'Non évalué'
            ajournes += 1  # On compte les sans-notes comme ajournés pour les stats

        liste_complete_etudiants.append({
            'id': e.id,
            'nom_complet': f"{e.nom.upper()} {e.prenom.title()}",
            'classe': e.classe.nom_classe if e.classe else 'N/A',
            'moyenne': round(moy, 2),
            'statut': statut
        })

    # Calcul du taux de réussite global
    taux_reussite = (admis / total_etudiants * 100) if total_etudiants > 0 else 0

    # TRI DU CLASSEMENT GÉNÉRAL (Du meilleur au moins bon)
    liste_complete_etudiants.sort(key=lambda x: x['moyenne'], reverse=True)

    # On extrait quand même le Top/Flop pour l'affichage rapide (widgets)
    top_5_etudiants = liste_complete_etudiants[:5]
    flop_5_etudiants = liste_complete_etudiants[-5:] if len(liste_complete_etudiants) > 5 else []

    # ==========================================
    # 3. ANALYSE PAR CLASSE (Moyennes + BoxPlot)
    # ==========================================
    classes = Classe.query.all()
    data_classes_noms = []
    data_classes_moyennes = []
    meilleure_classe_nom = "Aucune"
    meilleure_classe_moy = -1

    for c in classes:
        # On calcule la moyenne de la classe via SQL pour la rapidité
        eleves_ids = [e.id for e in c.etudiants]
        val = 0
        if eleves_ids:
            avg_classe = db.session.query(func.avg(Note.note)) \
                .filter(Note.etudiant_id.in_(eleves_ids)).scalar()
            val = round(avg_classe, 2) if avg_classe else 0

        data_classes_noms.append(c.nom_classe)
        data_classes_moyennes.append(val)

        # Recherche de la meilleure classe
        if val > meilleure_classe_moy:
            meilleure_classe_moy = val
            meilleure_classe_nom = c.nom_classe

    # ==========================================
    # 4. PERFORMANCES PAR UE (AUDIT MATIÈRES)
    # ==========================================
    ues_stats = db.session.query(
        UE.code_ue,
        UE.intitule,
        func.avg(Note.note).label('avg_note')
    ).join(Note).group_by(UE.id).order_by(desc('avg_note')).all()

    top_ues = [{'code': u.code_ue, 'nom': u.intitule, 'moy': round(u.avg_note, 2)} for u in ues_stats[:5]]
    worst_ues = [{'code': u.code_ue, 'nom': u.intitule, 'moy': round(u.avg_note, 2)} for u in ues_stats[-5:]]

    # ==========================================
    # 5. GÉNÉRATION DE L'INTERPRÉTATION (IA-Style)
    # ==========================================
    interpretation_text = f"L'établissement affiche une moyenne globale de {moyenne_ecole}/20. "

    if moyenne_ecole >= 12:
        interpretation_text += "C'est une performance globale solide. "
    elif moyenne_ecole >= 10:
        interpretation_text += "Le niveau est correct mais fragile. "
    else:
        interpretation_text += "Le niveau global est critique et nécessite des mesures correctives. "

    interpretation_text += f"Le taux de réussite est de {round(taux_reussite, 1)}%. "
    interpretation_text += f"La classe moteur est {meilleure_classe_nom} ({meilleure_classe_moy}/20). "

    if worst_ues:
        interpretation_text += f"Une attention particulière doit être portée sur le module {worst_ues[-1]['nom']} qui enregistre les plus faibles résultats."

    # ==========================================
    # 6. RETOUR AU TEMPLATE
    # ==========================================
    return render_template('directeur/statistiques.html',
                           # KPIs
                           total_etudiants=total_etudiants,
                           total_profs=total_profs,
                           total_classes=total_classes,
                           total_ues=total_ues,

                           # Stats Globales
                           moyenne_ecole=moyenne_ecole,
                           taux_reussite=round(taux_reussite, 2),
                           admis=admis,
                           ajournes=ajournes,

                           # Listes
                           liste_complete_etudiants=liste_complete_etudiants,  # LA LISTE COMPLÈTE
                           top_5_etudiants=top_5_etudiants,
                           flop_5_etudiants=flop_5_etudiants,

                           # Données Graphiques JS
                           data_classes_noms=data_classes_noms,
                           data_classes_moyennes=data_classes_moyennes,
                           top_ues=top_ues,
                           worst_ues=worst_ues,

                           # Texte
                           interpretation=interpretation_text)

@bp.route('/telecharger-rapport-statistique')
@directeur_required
def telecharger_rapport_statistique():
    buffer = io.BytesIO()
    # Marges réduites pour faire tenir plus d'infos
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()

    # Styles personnalisés
    style_titre = ParagraphStyle('Titre', parent=styles['Heading1'], alignment=1, fontSize=22, spaceAfter=20,
                                 textColor=colors.darkblue)
    style_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=16, spaceBefore=15, spaceAfter=10,
                              textColor=colors.black, borderPadding=5, backColor=colors.lightgrey)
    style_h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=12, spaceBefore=10, textColor=colors.darkblue)
    style_normal = ParagraphStyle('Normal', parent=styles['BodyText'], fontSize=10, spaceAfter=5)
    style_interpretation = ParagraphStyle('Interpret', parent=styles['BodyText'], fontSize=10, spaceAfter=10,
                                          leftIndent=10, textColor=colors.darkslategray, fontName='Helvetica-Oblique')

    # --- 1. PRÉPARATION DES DONNÉES ---
    etudiants = Etudiant.query.all()
    classes = Classe.query.all()

    # Liste complète des moyennes étudiants
    data_etudiants = []
    for e in etudiants:
        notes = [n.note for n in e.notes if n.note is not None]
        moy = sum(notes) / len(notes) if notes else 0
        data_etudiants.append({
            'nom': f"{e.nom.upper()} {e.prenom}",
            'classe': e.classe.nom_classe if e.classe else "N/A",
            'moyenne': round(moy, 2),
            'statut': 'Admis' if moy >= 10 else 'Ajourné'
        })

    # Tri par mérite (du premier au dernier)
    data_etudiants.sort(key=lambda x: x['moyenne'], reverse=True)

    # Données par Classe
    stats_classes = []
    raw_notes_by_class = []  # Pour la boite à moustaches
    labels_classes = []

    for c in classes:
        eleves = [e for e in c.etudiants]
        notes_classe = []
        for e in eleves:
            notes_e = [n.note for n in e.notes if n.note is not None]
            if notes_e: notes_classe.append(sum(notes_e) / len(notes_e))

        moy_classe = sum(notes_classe) / len(notes_classe) if notes_classe else 0
        stats_classes.append({'nom': c.nom_classe, 'moyenne': round(moy_classe, 2), 'effectif': len(eleves)})

        # Données BoxPlot (on met des 0 si vide pour éviter crash)
        if notes_classe:
            raw_notes_by_class.append(notes_classe)
            labels_classes.append(c.nom_classe)
        else:
            raw_notes_by_class.append([0])
            labels_classes.append(c.nom_classe)

    # Tri des classes par performance
    stats_classes.sort(key=lambda x: x['moyenne'], reverse=True)
    meilleure_classe = stats_classes[0] if stats_classes else {'nom': 'Aucune', 'moyenne': 0}
    pire_classe = stats_classes[-1] if stats_classes else {'nom': 'Aucune', 'moyenne': 0}
    moyenne_globale = sum([d['moyenne'] for d in data_etudiants]) / len(data_etudiants) if data_etudiants else 0

    # --- 2. GÉNÉRATION DU PDF ---

    # TITRE
    elements.append(Paragraph(f"AUDIT ACADÉMIQUE COMPLET {datetime.now().year}", style_titre))
    elements.append(Paragraph(f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 10))

    # SECTION 1: INTERPRÉTATION AUTOMATIQUE (IA STYLE)
    elements.append(Paragraph("1. INTERPRÉTATION & SYNTHÈSE", style_h2))

    # Logique d'interprétation
    txt_intro = f"L'établissement compte {len(etudiants)} étudiants répartis dans {len(classes)} classes. La moyenne générale de l'école s'établit à <b>{moyenne_globale:.2f}/20</b>."

    if moyenne_globale >= 12:
        txt_intro += " C'est une performance globale satisfaisante."
    elif moyenne_globale >= 10:
        txt_intro += " Le niveau global est juste, des efforts sont nécessaires."
    else:
        txt_intro += " <font color='red'>ALERTE : Le niveau global est insuffisant.</font>"

    txt_classe = f"La classe la plus performante est <b>{meilleure_classe['nom']}</b> avec une moyenne de {meilleure_classe['moyenne']}/20. " \
                 f"À l'inverse, la classe <b>{pire_classe['nom']}</b> rencontre des difficultés ({pire_classe['moyenne']}/20)."

    elements.append(Paragraph(txt_intro, style_normal))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(txt_classe, style_normal))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(
        "<i>Note : La boîte à moustaches ci-dessous permet d'analyser l'hétérogénéité des niveaux au sein de chaque groupe.</i>",
        style_interpretation))

    elements.append(Spacer(1, 15))

    # SECTION 2: ANALYSE GRAPHIQUE
    elements.append(Paragraph("2. ANALYSE VISUELLE", style_h2))

    # A. BOÎTE À MOUSTACHES
    if raw_notes_by_class:
        plt.figure(figsize=(7, 3.5))
        # Style des boites
        box = plt.boxplot(raw_notes_by_class, labels=labels_classes, patch_artist=True, vert=True)

        # Couleurs
        colors_box = ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6']
        for patch, color in zip(box['boxes'], colors_box * 5):  # Repeat colors if needed
            patch.set_facecolor(color)

        plt.title("Dispersion des notes par Classe (Box Plot)")
        plt.ylabel("Notes / 20")
        plt.grid(axis='y', linestyle='--', alpha=0.5)

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', dpi=100)
        img_buf.seek(0)
        elements.append(Image(img_buf, width=480, height=240))
        plt.close()
        elements.append(Paragraph(
            "<b>Lecture :</b> La ligne rouge indique la médiane. La boîte colorée contient 50% des élèves. Plus la boîte est grande, plus le niveau est hétérogène.",
            style_interpretation))

    elements.append(Spacer(1, 10))

    # B. COMPARATIF MOYENNES CLASSES (Bar Chart)
    plt.figure(figsize=(7, 3))
    noms = [c['nom'] for c in stats_classes]
    vals = [c['moyenne'] for c in stats_classes]

    plt.bar(noms, vals, color='#34495e', width=0.5)
    plt.axhline(y=moyenne_globale, color='red', linestyle='--', label='Moyenne École')
    plt.ylim(0, 20)
    plt.title("Moyenne par Classe vs Moyenne École")
    plt.legend()

    img_buf2 = io.BytesIO()
    plt.savefig(img_buf2, format='png', dpi=100)
    img_buf2.seek(0)
    elements.append(Image(img_buf2, width=480, height=200))
    plt.close()

    elements.append(PageBreak())

    # SECTION 3: CLASSEMENT GÉNÉRAL
    elements.append(Paragraph(f"3. CLASSEMENT GÉNÉRAL DES {len(etudiants)} ÉTUDIANTS", style_h2))

    # Tableau Géant
    data_table = [['Rang', 'Nom & Prénom', 'Classe', 'Moyenne', 'Mention']]

    for i, e in enumerate(data_etudiants):
        # Calcul mention
        m = e['moyenne']
        mention = "Ajourné"
        color_row = colors.white

        if m >= 16:
            mention = "Très Bien"; color_row = colors.Color(0.8, 1, 0.8)  # Vert pâle
        elif m >= 14:
            mention = "Bien"; color_row = colors.Color(0.9, 1, 0.9)
        elif m >= 12:
            mention = "Assez Bien"
        elif m >= 10:
            mention = "Passable"
        elif m < 10:
            color_row = colors.Color(1, 0.9, 0.9)  # Rouge pâle

        data_table.append([str(i + 1), e['nom'], e['classe'], f"{e['moyenne']:.2f}", mention])

    # Configuration du tableau reportlab
    # colWidths pour bien répartir sur A4
    t = Table(data_table, colWidths=[40, 230, 100, 60, 100], repeatRows=1)

    style_table = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),  # En-tête bleu
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]

    # Appliquer les couleurs de fond conditionnelles (Vert pour TB, Rouge pour Echec)
    for i, e in enumerate(data_etudiants):
        bg_color = colors.white
        if e['moyenne'] >= 16:
            bg_color = colors.Color(0.85, 0.95, 0.85)
        elif e['moyenne'] < 10:
            bg_color = colors.Color(0.95, 0.85, 0.85)
        elif i % 2 == 1:
            bg_color = colors.whitesmoke  # Zebra simple pour le reste

        style_table.append(('BACKGROUND', (0, i + 1), (-1, i + 1), bg_color))

    t.setStyle(TableStyle(style_table))
    elements.append(t)

    # Construction finale
    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name=f"Audit_Academique_{datetime.now().strftime('%Y%m%d')}.pdf")


# Dans app/routes/directeur.py
from app.models import Examen  # + les autres imports


@bp.route('/examens')
@directeur_required
def liste_examens():
    # On trie par date la plus récente
    examens = Examen.query.order_by(Examen.date_examen.desc()).all()
    classes = Classe.query.filter_by(active=True).all()
    ues = UE.query.all()
    enseignants = Enseignant.query.filter_by(actif=True).all()

    return render_template('directeur/examens.html',
                           examens=examens,
                           classes=classes,
                           ues=ues,
                           enseignants=enseignants)


@bp.route('/examen/ajouter', methods=['POST'])
@directeur_required
def ajouter_examen():
    try:
        # Récupération des données
        ue_id = request.form.get('ue_id')
        classe_id = request.form.get('classe_id')
        date_str = request.form.get('date')
        heure_debut_str = request.form.get('heure_debut')
        heure_fin_str = request.form.get('heure_fin')
        salle = request.form.get('salle')
        surveillant_id = request.form.get('surveillant_id') or None

        # Conversion des dates/heures
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        debut_obj = datetime.strptime(heure_debut_str, '%H:%M').time()
        fin_obj = datetime.strptime(heure_fin_str, '%H:%M').time()

        nouvel_exam = Examen(
            ue_id=int(ue_id),
            classe_id=int(classe_id),
            date_examen=date_obj,
            heure_debut=debut_obj,
            heure_fin=fin_obj,
            salle=salle,
            surveillant_id=int(surveillant_id) if surveillant_id else None
        )

        db.session.add(nouvel_exam)
        db.session.commit()
        flash("Examen programmé avec succès !", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Erreur : {str(e)}", "danger")

    return redirect(url_for('directeur.liste_examens'))


@bp.route('/examen/supprimer/<int:exam_id>')
@directeur_required
def supprimer_examen(exam_id):
    exam = Examen.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    flash("Examen annulé.", "info")
    return redirect(url_for('directeur.liste_examens'))


# Dans app/routes/directeur.py
from app.models import Livre, Etagere
from werkzeug.utils import secure_filename
import os


@bp.route('/bibliotheque')
@directeur_required
def bibliotheque():
    etageres = Etagere.query.filter_by(active=True).order_by(Etagere.ordre).all()
    livres_sans_etagere = Livre.query.filter_by(etagere_id=None).order_by(Livre.date_ajout.desc()).all()
    total_livres = Livre.query.count()
    return render_template('directeur/bibliotheque.html',
                           etageres=etageres,
                           livres_sans_etagere=livres_sans_etagere,
                           total_livres=total_livres)


@bp.route('/bibliotheque/ajouter', methods=['POST'])
@directeur_required
def ajouter_livre():
    from app.services.ia_bibliotheque import BibliothequeIA

    try:
        titre = request.form.get('titre')
        auteur = request.form.get('auteur')
        categorie = request.form.get('categorie')
        description = request.form.get('description')
        etagere_id = request.form.get('etagere_id')

        # 🤖 TRI AUTOMATIQUE PAR IA si pas de catégorie sélectionnée
        if not categorie or categorie == "":
            biblio_ia = BibliothequeIA()
            categorie = biblio_ia.determiner_categorie(titre, auteur, description)
            if not description:
                description = biblio_ia.generer_description(titre, auteur, categorie)

        # Gestion des fichiers
        pdf = request.files.get('fichier_pdf')
        cover = request.files.get('image_couverture')

        if pdf and titre:
            # 1. Sauvegarde PDF
            pdf_name = secure_filename(pdf.filename)
            unique_pdf = f"book_{datetime.now().strftime('%Y%m%d%H%M')}_{pdf_name}"
            path_pdf = os.path.join(current_app.root_path, 'static', 'library', 'pdf')
            os.makedirs(path_pdf, exist_ok=True)
            pdf.save(os.path.join(path_pdf, unique_pdf))

            # 2. Sauvegarde Couverture (Optionnel)
            cover_name = 'default_book.jpg'
            if cover and cover.filename:
                c_name = secure_filename(cover.filename)
                unique_cover = f"cover_{datetime.now().strftime('%Y%m%d%H%M')}_{c_name}"
                path_cover = os.path.join(current_app.root_path, 'static', 'library', 'covers')
                os.makedirs(path_cover, exist_ok=True)
                cover.save(os.path.join(path_cover, unique_cover))
                cover_name = unique_cover

            nouveau_livre = Livre(
                titre=titre, auteur=auteur, categorie=categorie,
                description=description,
                fichier_pdf=unique_pdf, image_couverture=cover_name,
                etagere_id=int(etagere_id) if etagere_id else None,
                ajoute_par_id=current_user.id,
                ajoute_par_role='DIRECTEUR'
            )
            db.session.add(nouveau_livre)
            db.session.commit()
            flash(f"✅ Livre ajouté dans la catégorie '{categorie}' !", "success")

    except Exception as e:
        flash(f"Erreur: {str(e)}", "danger")

    return redirect(url_for('directeur.bibliotheque'))


@bp.route('/bibliotheque/supprimer/<int:livre_id>', methods=['POST'])
@directeur_required
def supprimer_livre(livre_id):
    """Supprimer un livre de la bibliothèque"""
    try:
        livre = Livre.query.get_or_404(livre_id)

        # Supprimer les fichiers physiques
        pdf_path = os.path.join(current_app.root_path, 'static', 'library', 'pdf', livre.fichier_pdf)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        if livre.image_couverture != 'default_book.jpg':
            cover_path = os.path.join(current_app.root_path, 'static', 'library', 'covers', livre.image_couverture)
            if os.path.exists(cover_path):
                os.remove(cover_path)

        db.session.delete(livre)
        db.session.commit()
        flash("Livre supprimé avec succès.", "success")
    except Exception as e:
        flash(f"Erreur: {str(e)}", "danger")

    return redirect(url_for('directeur.bibliotheque'))


@bp.route('/bibliotheque/etagere/creer', methods=['POST'])
@directeur_required
def creer_etagere():
    """Créer une nouvelle étagère"""
    nom = request.form.get('nom', '').strip()
    description = request.form.get('description', '').strip()
    icone = request.form.get('icone', 'fas fa-bookmark')
    couleur = request.form.get('couleur', '#667eea')

    if not nom:
        flash("Le nom de l'étagère est requis.", "warning")
        return redirect(url_for('directeur.bibliotheque'))

    if Etagere.query.filter_by(nom=nom).first():
        flash(f"L'étagère '{nom}' existe déjà.", "warning")
        return redirect(url_for('directeur.bibliotheque'))

    try:
        ordre = (db.session.query(db.func.max(Etagere.ordre)).scalar() or 0) + 1
        etagere = Etagere(nom=nom, description=description, icone=icone, couleur=couleur, ordre=ordre)
        db.session.add(etagere)
        db.session.commit()
        flash(f"✅ Étagère '{nom}' créée !", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur : {str(e)}", "danger")

    return redirect(url_for('directeur.bibliotheque'))


@bp.route('/bibliotheque/etagere/<int:etagere_id>/supprimer', methods=['POST'])
@directeur_required
def supprimer_etagere(etagere_id):
    """Supprimer une étagère (les livres sont déplacés dans 'non classés')"""
    etagere = Etagere.query.get_or_404(etagere_id)
    try:
        # Détacher les livres de cette étagère
        Livre.query.filter_by(etagere_id=etagere.id).update({'etagere_id': None})
        db.session.delete(etagere)
        db.session.commit()
        flash(f"Étagère '{etagere.nom}' supprimée. Les livres sont non-classés.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur : {str(e)}", "danger")
    return redirect(url_for('directeur.bibliotheque'))


@bp.route('/deliberations')
@directeur_required
def deliberations():
    classes = Classe.query.filter_by(active=True).all()
    return render_template('directeur/deliberations_choix.html', classes=classes)


@bp.route('/deliberations/calculer/<int:classe_id>', methods=['GET', 'POST'])
@directeur_required
def calculer_deliberation(classe_id):
    classe = Classe.query.get_or_404(classe_id)

    if request.method == 'POST':
        # 1. On nettoie les anciennes délibérations de cette classe pour éviter les doublons
        Deliberation.query.filter_by(classe_id=classe.id).delete()

        etudiants = classe.etudiants.filter_by(statut_inscription='accepté').all()
        resultats_temporaires = []

        # 2. Boucle sur chaque étudiant
        for etudiant in etudiants:
            # Récupération de toutes les notes
            notes = Note.query.filter_by(etudiant_id=etudiant.id).all()

            if not notes:
                moyenne = 0.0
            else:
                # Calcul simple (Somme / Nombre).
                # Tu peux améliorer ça avec des coefficients si tes UEs en ont.
                somme = sum([n.note for n in notes])
                moyenne = round(somme / len(notes), 2)

            # 3. Application des Règles de Passage
            if moyenne >= 16:
                decision = 'ADMIS'
                mention = 'Très Bien'
            elif moyenne >= 14:
                decision = 'ADMIS'
                mention = 'Bien'
            elif moyenne >= 12:
                decision = 'ADMIS'
                mention = 'Assez Bien'
            elif moyenne >= 10:
                decision = 'ADMIS'
                mention = 'Passable'
            elif moyenne >= 8:
                decision = 'RATTRAPAGE'  # Ou "Conditionnel"
                mention = 'Ajourné'
            else:
                decision = 'REFUSÉ'  # Redoublement
                mention = 'Insuffisant'

            # On stocke temporairement pour calculer le rang après
            resultats_temporaires.append({
                'etudiant': etudiant,
                'moyenne': moyenne,
                'decision': decision,
                'mention': mention
            })

        # 4. Calcul du RANG (Classement)
        # On trie la liste par moyenne décroissante (du plus grand au plus petit)
        resultats_temporaires.sort(key=lambda x: x['moyenne'], reverse=True)

        for index, res in enumerate(resultats_temporaires):
            nouvelle_delib = Deliberation(
                etudiant_id=res['etudiant'].id,
                classe_id=classe.id,
                moyenne_annuelle=res['moyenne'],
                decision=res['decision'],
                mention=res['mention'],
                rang=index + 1  # Le premier a le rang 1
            )
            db.session.add(nouvelle_delib)

        try:
            db.session.commit()
            flash(f"Délibération terminée pour {len(etudiants)} étudiants.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur calcul : {str(e)}", "danger")

        return redirect(url_for('directeur.voir_pv', classe_id=classe.id))

    return render_template('directeur/confirmer_calcul.html', classe=classe)


@bp.route('/deliberations/pv/<int:classe_id>')
@directeur_required
def voir_pv(classe_id):
    classe = Classe.query.get_or_404(classe_id)
    # On récupère les résultats triés par rang (1er, 2ème...)
    deliberations = Deliberation.query.filter_by(classe_id=classe.id).order_by(Deliberation.rang).all()

    # Statistiques rapides
    admis = Deliberation.query.filter_by(classe_id=classe.id, decision='ADMIS').count()
    total = len(deliberations)
    taux = round((admis / total * 100), 1) if total > 0 else 0

    return render_template('directeur/pv_deliberation.html',
                           classe=classe,
                           deliberations=deliberations,
                           stats={'admis': admis, 'total': total, 'taux': taux})


# =========================================================================
# DÉTAIL ÉCOLE (Encyclopédie / Tableau de bord école)
# =========================================================================
@bp.route('/detail-ecole')
@directeur_required
def detail_ecole():
    """Page encyclopédie de l'école avec toutes les infos"""
    from app.models import ConfigurationEcole
    config = ConfigurationEcole.query.first()
    departements = Departement.query.filter_by(active=True).order_by(Departement.nom).all()
    filieres = Filiere.query.filter_by(active=True).order_by(Filiere.nom_filiere).all()
    classes   = Classe.query.filter_by(active=True).order_by(Classe.nom_classe).all()
    ues       = UE.query.filter_by(active=True, parent_id=None).order_by(UE.code_ue).all()
    nb_etudiants   = Etudiant.query.count()
    nb_enseignants = Enseignant.query.filter_by(actif=True).count()
    return render_template('directeur/detail_ecole.html',
                           config=config,
                           departements=departements,
                           filieres=filieres,
                           classes=classes,
                           ues=ues,
                           nb_etudiants=nb_etudiants,
                           nb_enseignants=nb_enseignants)

@bp.route('/labo-architecture')
@directeur_required
def labo_architecture():
    """Page laboratoire architecture virtuelle EPS"""
    return render_template('directeur/labo_architecture.html')


# =========================================================================
# GUIDE D'ORIENTATION (accessible sans connexion depuis /guide)
# =========================================================================
# Route publique enregistrée dans auth.py → on crée ici la logique PDF
@bp.route('/guide-orientation')
@directeur_required
def guide_orientation_admin():
    """Prévisualisation du guide depuis le dashboard directeur"""
    return _render_guide()


def _render_guide():
    """Génère la page HTML du guide d'orientation"""
    from app.models import ConfigurationEcole
    config      = ConfigurationEcole.query.first()
    departements = Departement.query.filter_by(active=True).order_by(Departement.nom).all()
    filieres_fond = Filiere.query.filter_by(active=True, type_diplome='fondamental').order_by(Filiere.nom_filiere).all()
    filieres_pro  = Filiere.query.filter_by(active=True, type_diplome='professionnel').order_by(Filiere.nom_filiere).all()
    ues_majeures  = UE.query.filter_by(active=True, parent_id=None).order_by(UE.semestre, UE.code_ue).all()
    nb_etudiants  = Etudiant.query.count()
    return render_template('public/guide_orientation.html',
                           config=config,
                           departements=departements,
                           filieres_fond=filieres_fond,
                           filieres_pro=filieres_pro,
                           ues_majeures=ues_majeures,
                           nb_etudiants=nb_etudiants,
                           annee=datetime.now().year)


@bp.route('/guide-orientation/pdf')
@directeur_required
def guide_orientation_pdf():
    """Télécharge le guide d'orientation en PDF (ReportLab)"""
    return _generer_guide_pdf()


def _generer_guide_pdf():
    from app.models import ConfigurationEcole
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, PageBreak, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    config = ConfigurationEcole.query.first()
    nom_ecole = config.nom_ecole if config else "École Polytechnique de la State"
    nom_directeur = config.nom_directeur if config else "La Direction"

    departements = Departement.query.filter_by(active=True).order_by(Departement.nom).all()
    filieres     = Filiere.query.filter_by(active=True).order_by(Filiere.nom_filiere).all()
    ues_majeures = UE.query.filter_by(active=True, parent_id=None).order_by(UE.semestre, UE.code_ue).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    # Styles
    styles = getSampleStyleSheet()
    BLUE  = colors.HexColor('#003366')
    GOLD  = colors.HexColor('#CC9933')
    LIGHT = colors.HexColor('#EEF2FF')

    s_titre   = ParagraphStyle('Titre',   parent=styles['Title'],   textColor=BLUE,  fontSize=22, spaceAfter=8, alignment=TA_CENTER)
    s_h1      = ParagraphStyle('H1',      parent=styles['Heading1'], textColor=BLUE,  fontSize=14, spaceBefore=14, spaceAfter=6)
    s_h2      = ParagraphStyle('H2',      parent=styles['Heading2'], textColor=GOLD,  fontSize=12, spaceBefore=10, spaceAfter=4)
    s_body    = ParagraphStyle('Body',    parent=styles['Normal'],  fontSize=10, spaceAfter=4)
    s_center  = ParagraphStyle('Center',  parent=styles['Normal'],  fontSize=10, alignment=TA_CENTER)
    s_badge   = ParagraphStyle('Badge',   parent=styles['Normal'],  fontSize=9,  textColor=colors.white, backColor=BLUE, spaceAfter=2)

    story = []

    # ---- PAGE DE GARDE ----
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(nom_ecole.upper(), s_titre))
    story.append(HRFlowable(width="80%", thickness=2, color=GOLD, hAlign='CENTER'))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>Guide d'Orientation Officiel</b>", ParagraphStyle('GT', parent=s_titre, fontSize=16, textColor=GOLD)))
    story.append(Paragraph(f"Année Universitaire {datetime.now().year}-{datetime.now().year+1}", s_center))
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph(f"Direction Générale : <b>{nom_directeur}</b>", s_center))
    story.append(Paragraph(f"Mis à jour le : {datetime.now().strftime('%d/%m/%Y')}", s_center))
    story.append(PageBreak())

    # ---- MOT DE LA DIRECTION ----
    story.append(Paragraph("1. Mot de la Direction", s_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"Bienvenue à {nom_ecole}. Notre mission est de former les ingénieurs et innovateurs de demain. "
        "Ce guide présente l'ensemble de notre offre de formation, qui évolue constamment pour s'adapter "
        "aux défis technologiques et aux besoins du marché.", s_body))
    story.append(Spacer(1, 0.5*cm))

    # ---- DÉPARTEMENTS & FILIÈRES ----
    story.append(Paragraph("2. Nos Départements et Filières", s_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    story.append(Spacer(1, 0.3*cm))

    for dept in departements:
        story.append(Paragraph(f"Département : {dept.nom}", s_h2))
        if dept.chef:
            story.append(Paragraph(f"<b>Chef de département :</b> {dept.chef.nom} {dept.chef.prenom}", s_body))
        if dept.description:
            story.append(Paragraph(dept.description, s_body))

        # Tableau des filières du département
        fil_dept = [f for f in filieres if f.departement_id == dept.id]
        if fil_dept:
            data_table = [['Code', 'Filière', 'Cycle', 'Type']]
            for f in fil_dept:
                type_lbl = 'Fondamentale' if f.type_diplome == 'fondamental' else 'Professionnelle'
                data_table.append([f.code_filiere or '-', f.nom_filiere, f.cycle or '-', type_lbl])

            tbl = Table(data_table, colWidths=[2.5*cm, 8*cm, 3*cm, 4*cm])
            tbl.setStyle(TableStyle([
                ('BACKGROUND',  (0,0), (-1,0), BLUE),
                ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
                ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',    (0,0), (-1,-1), 9),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
                ('GRID',        (0,0), (-1,-1), 0.5, colors.lightgrey),
                ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(tbl)
        story.append(Spacer(1, 0.4*cm))

    story.append(PageBreak())

    # ---- UE MAJEURES ----
    story.append(Paragraph("3. Structure des Unités d'Enseignement (UE)", s_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    story.append(Spacer(1, 0.3*cm))

    if ues_majeures:
        data_ue = [['Code UE', 'Intitulé', 'Semestre', 'Crédits', 'Catégorie']]
        for ue in ues_majeures[:60]:  # max 60 lignes
            cat_map = {'fondamentale': '🔴 Fond.', 'specialite': '🔵 Spéc.',
                       'transversale': '🟢 Trans.', 'libre': '🟡 Libre'}
            cat = cat_map.get(ue.categorie or '', '-')
            data_ue.append([ue.code_ue, (ue.nom_ue or ue.intitule or '')[:45],
                             ue.semestre or '-', str(ue.credits or 0), cat])

        tbl_ue = Table(data_ue, colWidths=[2.5*cm, 9*cm, 2*cm, 2*cm, 2.5*cm])
        tbl_ue.setStyle(TableStyle([
            ('BACKGROUND',  (0,0), (-1,0), BLUE),
            ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
            ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
            ('GRID',        (0,0), (-1,-1), 0.4, colors.lightgrey),
        ]))
        story.append(tbl_ue)

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="80%", thickness=1, color=GOLD, hAlign='CENTER'))
    story.append(Paragraph(f"Pour plus d'informations, consultez votre portail en ligne.", s_center))

    doc.build(story)
    buffer.seek(0)

    filename = f"guide_orientation_{nom_ecole.replace(' ', '_')}_{datetime.now().year}.pdf"
    return send_file(buffer, as_attachment=True,
                     download_name=filename,
                     mimetype='application/pdf')

