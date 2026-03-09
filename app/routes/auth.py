from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Etudiant, Enseignant, Filiere, Annonce
from datetime import datetime
import os
import io

# UN SEUL Blueprint défini ici
bp = Blueprint('auth', __name__)


# ============================================================
# 1. PAGE D'AIGUILLAGE (INDEX)
# ============================================================
@bp.route('/')
@login_required
def index():
    """Redirige l'utilisateur vers la bonne page selon son rôle"""

    # Cas 1 : Le Directeur (CORRIGÉ : Pas de parenthèses)
    if current_user.is_directeur:
        return redirect(url_for('directeur.dashboard'))

    # Cas 2 : L'Enseignant (CORRIGÉ : Pas de parenthèses)
    if current_user.is_enseignant:
        return redirect(url_for('enseignant.dashboard'))

    # Cas 3 : L'Étudiant (CORRIGÉ : Pas de parenthèses)
    if current_user.is_etudiant:
        etudiant = Etudiant.query.filter_by(user_id=current_user.id).first()
        if not etudiant:
            flash("Profil étudiant introuvable.", "danger")
            logout_user()
            return redirect(url_for('auth.login'))

        if etudiant.statut_inscription == 'en_attente':
            return render_template('etudiant/dashboard_attente.html', etudiant=etudiant)

        return redirect(url_for('etudiant.dashboard'))

    return "Bienvenue sur la plateforme Polytech de la State"


# ============================================================
# 2. CONNEXION (LOGIN)
# ============================================================
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si déjà connecté, on envoie vers l'index qui aiguille vers le bon dashboard
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        # On utilise la méthode verify_password de ton modèle User
        if user and user.verify_password(password):
            login_user(user)
            flash(f'Bienvenue, {user.username} !', 'success')
            return redirect(url_for('auth.index'))
        else:
            flash('Identifiants (pseudo ou mot de passe) incorrects.', 'danger')

    # Charger les annonces publiques pour la page de connexion
    annonces_publiques = Annonce.query.filter_by(visible_public=True).order_by(Annonce.date_publication.desc()).limit(5).all()
    guide = Annonce.query.filter_by(visible_public=True, categorie='guide').order_by(Annonce.date_publication.desc()).first()

    return render_template('auth/login.html', annonces=annonces_publiques, guide=guide)


# ============================================================
# ACTUALITÉS & ANNONCES PUBLIQUES (Accès public - pas besoin de connexion)
# ============================================================
@bp.route('/actualites')
def actualites_publiques():
    """Page publique des actualités et annonces de l'école"""
    annonces = Annonce.query.filter_by(visible_public=True).order_by(Annonce.date_publication.desc()).all()
    guides = Annonce.query.filter_by(visible_public=True, categorie='guide').order_by(Annonce.date_publication.desc()).all()
    actualites = Annonce.query.filter_by(visible_public=True, categorie='actualite').order_by(Annonce.date_publication.desc()).all()
    articles = Annonce.query.filter_by(visible_public=True, categorie='article').order_by(Annonce.date_publication.desc()).all()
    return render_template('auth/guide_orientation.html',
                           guides=guides, actualites=actualites, articles=articles, annonces=annonces)


@bp.route('/telecharger-guide/<int:annonce_id>')
def telecharger_guide(annonce_id):
    """Télécharger le fichier joint d'une annonce (accès public)"""
    annonce = Annonce.query.get_or_404(annonce_id)
    if not annonce.visible_public or not annonce.fichier_joint:
        flash('Fichier non disponible.', 'warning')
        return redirect(url_for('auth.actualites_publiques'))
    # Chemin absolu pour éviter le doublon app/app/static
    filepath = os.path.join(current_app.root_path, 'static', annonce.fichier_joint)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    flash('Fichier introuvable.', 'danger')
    return redirect(url_for('auth.guide_orientation'))


# ============================================================
# 3. INSCRIPTION (Étudiants uniquement)
# ============================================================

@bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if current_user.is_authenticated:
        return redirect(url_for('etudiant.dashboard'))

    if request.method == 'POST':
        # 1. Récupération des données AUTHENTIFICATION
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 2. Vérifications de base
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('auth.inscription'))

        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà pris.', 'danger')
            return redirect(url_for('auth.inscription'))

        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà enregistré.', 'danger')
            return redirect(url_for('auth.inscription'))

        # 3. Création du USER
        # Note: Le mot de passe est hashé automatiquement par le modèle User (via @password.setter)
        new_user = User(username=username, email=email, role='ETUDIANT', password=password)
        db.session.add(new_user)
        db.session.commit()  # On commit pour avoir l'ID du user

        # 4. Récupération des données ÉTUDIANT
        try:
            # Conversion sécurisée pour les chiffres (évite le crash si vide)
            def safe_float(val):
                return float(val) if val and val.strip() else None

            moyenne_bac = safe_float(request.form.get('moyenne_bac'))
            moyenne_licence = safe_float(request.form.get('moyenne_licence'))

            # Gestion de la filière (si pas sélectionnée)
            filiere_id = request.form.get('filiere_id')
            if not filiere_id:
                raise ValueError("Veuillez sélectionner une filière.")

            new_etudiant = Etudiant(
                user_id=new_user.id,

                # État Civil
                nom=request.form.get('nom'),
                prenom=request.form.get('prenom'),
                telephone=request.form.get('telephone'),
                sexe=request.form.get('sexe'),
                contact_urgence=request.form.get('contact_urgence'),

                # Parents
                nom_pere=request.form.get('nom_pere'),
                nom_mere=request.form.get('nom_mere'),

                # Académique
                filiere_id=int(filiere_id),
                moyenne_bac=moyenne_bac,
                serie_bac=request.form.get('serie_bac'),
                moyenne_licence=moyenne_licence,
                diplome_licence=request.form.get('diplome_licence'),

                # Statut par défaut
                statut_inscription='en_attente'
            )

            db.session.add(new_etudiant)
            db.session.commit()

            flash('Votre demande d\'inscription a été enregistrée avec succès ! Connectez-vous pour suivre son statut.',
                  'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()  # On annule tout si erreur
            # On supprime le user créé pour ne pas laisser de compte orphelin
            db.session.delete(new_user)
            db.session.commit()
            flash(f"Erreur lors de l'inscription : {str(e)}", 'danger')
            return redirect(url_for('auth.inscription'))

    # Affichage du formulaire (GET)
    filieres = Filiere.query.filter_by(active=True).all()
    return render_template('auth/inscription.html', filieres=filieres)

# ============================================================
# 4. DÉCONNEXION
# ============================================================
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))


# ============================================================
# 5. GESTION DU PROFIL (COMMUN À TOUS)
# ============================================================
@bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    if request.method == 'POST':
        # 1. Gestion de la Photo de Profil
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                # On renomme le fichier pour éviter les doublons (ex: user_12.jpg)
                _, ext = os.path.splitext(filename)
                new_filename = f"user_{current_user.id}{ext}"

                # Création du dossier s'il n'existe pas
                upload_path = os.path.join(current_app.root_path, 'static', 'avatars')
                os.makedirs(upload_path, exist_ok=True)

                # Sauvegarde
                file.save(os.path.join(upload_path, new_filename))

                # Mise à jour DB
                current_user.avatar = new_filename

        # 2. Gestion des Infos Personnelles (Email)
        new_email = request.form.get('email')
        if new_email and new_email != current_user.email:
            # Vérifier si l'email est libre
            if User.query.filter_by(email=new_email).first():
                flash("Cet email est déjà pris.", "warning")
            else:
                current_user.email = new_email

        # 3. Gestion des Infos Spécifiques (Étudiant / Enseignant)
        # Si c'est un étudiant, on peut mettre à jour son téléphone
        if current_user.is_etudiant:
            etudiant = current_user.etudiant_profile
            phone = request.form.get('telephone')
            adresse = request.form.get('adresse')
            if phone: etudiant.telephone = phone
            if adresse: etudiant.adresse = adresse  # Assure-toi d'avoir ce champ dans Etudiant

        # 4. Changement de Mot de Passe
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if password:
            if password == confirm:
                current_user.password = password  # Le setter hash automatiquement
                flash("Mot de passe mis à jour.", "success")
            else:
                flash("Les mots de passe ne correspondent pas.", "danger")
                return redirect(url_for('auth.profil'))

        try:
            db.session.commit()
            flash("Profil mis à jour avec succès !", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {str(e)}", "danger")

        return redirect(url_for('auth.profil'))

    return render_template('auth/profil.html')


# Route de redirection vers le profil spécifique
@bp.route('/mon-profil')
@login_required
def mon_profil_redirect():
    """Redirige vers le profil spécifique selon le rôle"""
    if current_user.role == 'ENSEIGNANT':
        return redirect(url_for('enseignant.profil'))
    elif current_user.role == 'ETUDIANT':
        return redirect(url_for('etudiant.profil'))
    return redirect(url_for('auth.profil'))


# ============================================================
# GUIDE D'ORIENTATION (route publique, sans connexion)
# ============================================================
@bp.route('/guide')
def guide_orientation():
    """Page publique du guide d'orientation – accessible sans connexion"""
    from app.models import ConfigurationEcole, Departement, Filiere, UE, Classe
    config        = ConfigurationEcole.query.first()
    departements  = Departement.query.filter_by(active=True).order_by(Departement.nom).all()
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


@bp.route('/guide/pdf')
def guide_orientation_pdf():
    """Télécharge le guide d'orientation en PDF (sans connexion)"""
    from app.models import ConfigurationEcole, Departement, Filiere, UE
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, PageBreak, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    config       = ConfigurationEcole.query.first()
    nom_ecole    = config.nom_ecole    if config else "École Polytechnique de la State"
    nom_directeur = config.nom_directeur if config else "La Direction"
    departements = Departement.query.filter_by(active=True).order_by(Departement.nom).all()
    filieres     = Filiere.query.filter_by(active=True).order_by(Filiere.nom_filiere).all()
    ues_majeures = UE.query.filter_by(active=True, parent_id=None).order_by(UE.semestre, UE.code_ue).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    BLUE  = colors.HexColor('#003366')
    GOLD  = colors.HexColor('#CC9933')
    LIGHT = colors.HexColor('#EEF2FF')

    s_titre  = ParagraphStyle('T',  parent=styles['Title'],   textColor=BLUE, fontSize=22, spaceAfter=8,  alignment=TA_CENTER)
    s_h1     = ParagraphStyle('H1', parent=styles['Heading1'], textColor=BLUE, fontSize=14, spaceBefore=14, spaceAfter=6)
    s_h2     = ParagraphStyle('H2', parent=styles['Heading2'], textColor=GOLD, fontSize=12, spaceBefore=10, spaceAfter=4)
    s_body   = ParagraphStyle('B',  parent=styles['Normal'],  fontSize=10, spaceAfter=4)
    s_center = ParagraphStyle('C',  parent=styles['Normal'],  fontSize=10, alignment=TA_CENTER)

    story = []
    # Page de garde
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(nom_ecole.upper(), s_titre))
    story.append(HRFlowable(width="80%", thickness=2, color=GOLD, hAlign='CENTER'))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("<b>Guide d'Orientation Officiel</b>",
                            ParagraphStyle('GT', parent=s_titre, fontSize=16, textColor=GOLD)))
    story.append(Paragraph(f"Année Universitaire {datetime.now().year}-{datetime.now().year+1}", s_center))
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(f"Directeur(trice) : <b>{nom_directeur}</b>", s_center))
    story.append(Paragraph(f"Mis à jour le : {datetime.now().strftime('%d/%m/%Y')}", s_center))
    story.append(PageBreak())

    # Mot de la direction
    story.append(Paragraph("1. Mot de la Direction", s_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"Bienvenue à {nom_ecole}. Notre mission est de former les ingénieurs et innovateurs de demain. "
        "Ce guide présente l'ensemble de notre offre de formation, qui évolue constamment pour répondre "
        "aux défis technologiques et aux besoins du marché de l'emploi.", s_body))

    # Départements & Filières
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("2. Nos Départements et Filières", s_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    for dept in departements:
        story.append(Paragraph(f"Département : {dept.nom}", s_h2))
        chef_txt = f"{dept.chef.nom} {dept.chef.prenom}" if dept.chef else "Non assigné"
        story.append(Paragraph(f"<b>Chef de département :</b> {chef_txt}", s_body))
        if dept.description:
            story.append(Paragraph(dept.description, s_body))

        fil_dept = [f for f in filieres if f.departement_id == dept.id]
        if fil_dept:
            data = [['Code', 'Filière', 'Cycle', 'Type', 'Classes']]
            for f in fil_dept:
                type_lbl = 'Fondamentale' if f.type_diplome == 'fondamental' else 'Professionnelle'
                classes_noms = ", ".join([c.nom_classe for c in f.classes.filter_by(active=True).all()])
                data.append([f.code_filiere or '-', f.nom_filiere, f.cycle or '-', type_lbl, classes_noms[:40]])
            tbl = Table(data, colWidths=[2*cm, 6.5*cm, 2.5*cm, 3.5*cm, 3.5*cm])
            tbl.setStyle(TableStyle([
                ('BACKGROUND',     (0,0), (-1,0), BLUE),
                ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
                ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',       (0,0), (-1,-1), 8),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
                ('GRID',           (0,0), (-1,-1), 0.4, colors.lightgrey),
            ]))
            story.append(tbl)
        story.append(Spacer(1, 0.3*cm))

    story.append(PageBreak())

    # UE
    story.append(Paragraph("3. Structure des Unités d'Enseignement", s_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    if ues_majeures:
        data_ue = [['Code', 'Intitulé', 'Semestre', 'Crédits', 'Catégorie']]
        for ue in ues_majeures[:60]:
            cat_map = {'fondamentale': 'Fondamentale', 'specialite': 'Spécialité',
                       'transversale': 'Transversale',  'libre': 'Libre'}
            cat = cat_map.get(ue.categorie or '', '-')
            data_ue.append([ue.code_ue, (ue.nom_ue or ue.intitule or '')[:45],
                             ue.semestre or '-', str(ue.credits or 0), cat])
        tbl_ue = Table(data_ue, colWidths=[2.5*cm, 9*cm, 2*cm, 2*cm, 2.5*cm])
        tbl_ue.setStyle(TableStyle([
            ('BACKGROUND',     (0,0), (-1,0), BLUE),
            ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
            ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',       (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
            ('GRID',           (0,0), (-1,-1), 0.4, colors.lightgrey),
        ]))
        story.append(tbl_ue)

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="80%", thickness=1, color=GOLD, hAlign='CENTER'))
    story.append(Paragraph("Pour plus d'informations, consultez votre portail en ligne.", s_center))

    doc.build(story)
    buffer.seek(0)
    filename = f"guide_orientation_{datetime.now().year}.pdf"
    return send_file(buffer, as_attachment=True,
                     download_name=filename,
                     mimetype='application/pdf')

