from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Etudiant, Enseignant, Filiere
from datetime import datetime
import os

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

    return render_template('auth/login.html')


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