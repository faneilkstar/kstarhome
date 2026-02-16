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
    InscriptionUE, Statistique, Annonce, Document, Diplome
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
                           nb_filieres=nb_filieres)

# ÉTAPE 1 : Créer le compte utilisateur


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
        nom = request.form.get('nom_filiere').upper()
        # Génération code intelligent (ex: GENIE LOGICIEL -> GL)
        code = "".join([word[0] for word in nom.split() if word])[:4] + str(datetime.now().year)[-2:]
        cycle = request.form.get('cycle')

        # Vérification doublon
        if Filiere.query.filter_by(nom_filiere=nom).first():
            flash(f"La filière {nom} existe déjà.", "warning")
            return redirect(url_for('directeur.ajouter_filiere'))

        try:
            # 1. Création Filière
            filiere = Filiere(nom_filiere=nom, code_filiere=code, cycle=cycle, active=True)
            db.session.add(filiere)
            db.session.flush()

            # 2. Génération automatique des classes
            classes_config = {
                'Licence': [('L1', 1), ('L2', 2), ('L3', 3)],
                'Master': [('M1', 1), ('M2', 2)],
                'Doctorat': [('DOC1', 1), ('DOC2', 2), ('DOC3', 3)]
            }

            if cycle in classes_config:
                for grade, annee in classes_config[cycle]:
                    nom_classe = f"{grade} {code}"  # Ex: L1 GL24
                    nouvelle_classe = Classe(
                        nom_classe=nom_classe,
                        code_classe=f"{code}-{grade}",
                        cycle=cycle,
                        annee=annee,
                        filiere_id=filiere.id,
                        active=True
                    )
                    db.session.add(nouvelle_classe)

            db.session.commit()
            flash(f"Filière {nom} créée avec ses classes associées.", "success")
            return redirect(url_for('directeur.liste_filieres'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur technique : {str(e)}", "danger")

    return render_template('directeur/ajouter_filiere.html')


@bp.route('/filiere/<int:filiere_id>')
@directeur_required
def detail_filiere(filiere_id):
    filiere = Filiere.query.get_or_404(filiere_id)
    return render_template('directeur/detail_filiere.html', filiere=filiere)


@bp.route('/classes')
@directeur_required
def liste_classes():
    classes = Classe.query.order_by(Classe.nom_classe).all()
    return render_template('directeur/liste_classes.html', classes=classes)


@bp.route('/classe/<int:classe_id>')
@directeur_required
def detail_classe(classe_id):
    classe = Classe.query.get_or_404(classe_id)
    # Étudiants validés uniquement
    etudiants = Etudiant.query.filter_by(classe_id=classe.id, statut_inscription='accepté').all()
    return render_template('directeur/detail_classe.html', classe=classe, etudiants=etudiants)


# =========================================================================
# GESTION ENSEIGNANTS
# =========================================================================
@bp.route('/enseignants')
@directeur_required
def liste_enseignants():
    enseignants = Enseignant.query.order_by(Enseignant.nom).all()
    toutes_les_ues = UE.query.all()
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
    ues = UE.query.order_by(UE.code_ue).all()
    classes = Classe.query.filter_by(active=True).all()  # Pour les filtres éventuels
    return render_template('directeur/liste_ues.html', ues=ues, classes=classes)


@bp.route('/affectations-ues')
@directeur_required
def page_attribuer_ue():
    """Page pour attribuer les UE aux enseignants"""
    ues = UE.query.all()
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
    classes = Classe.query.filter_by(active=True).all()

    if request.method == 'POST':
        code_base = request.form.get('code_ue').upper()
        intitule = request.form.get('intitule')
        semestre = int(request.form.get('semestre'))

        # NOUVEAUX CHOIX (3 modes)
        mode_creation = request.form.get('mode_creation', 'ue_specifique')
        type_evaluation = request.form.get('type_evaluation', 'simple')

        try:
            classes_ids = request.form.getlist('classes_ids')

            if not classes_ids:
                flash("❌ Veuillez sélectionner au moins une classe.", "warning")
                return redirect(url_for('directeur.ajouter_ue'))

            ues_creees = []

            # =============================================
            # TYPE COMPOSITE : Créer UE Parent + Sous-UE
            # =============================================
            if type_evaluation == 'composite':
                # Récupérer les sous-UE
                sous_ues_data = []
                for i in range(1, 4):  # Jusqu'à 3 sous-UE
                    intitule_sous = request.form.get(f'sous_ue_{i}_intitule', '').strip()
                    credits_sous = int(request.form.get(f'sous_ue_{i}_credits', 0))

                    if intitule_sous and credits_sous > 0:
                        sous_ues_data.append({
                            'prefixe': str(i),
                            'intitule': intitule_sous,
                            'credits': credits_sous
                        })

                if len(sous_ues_data) < 2:
                    flash("❌ Une UE composite nécessite au moins 2 sous-UE.", "warning")
                    return redirect(url_for('directeur.ajouter_ue'))

                # Calculer le total des crédits
                credits_total = sum([s['credits'] for s in sous_ues_data])
                heures = credits_total * 12
                coefficient = credits_total

                # MODE SPÉCIFIQUE
                if mode_creation == 'ue_specifique':
                    if len(classes_ids) > 1:
                        flash("⚠️  Mode UE Spécifique : une seule classe autorisée.", "warning")
                        return redirect(url_for('directeur.ajouter_ue'))

                    classe = Classe.query.get(int(classes_ids[0]))

                    # Créer UE Parent
                    ue_parent = UE(
                        code_ue=code_base,
                        intitule=intitule,
                        credits=credits_total,
                        coefficient=coefficient,
                        heures=heures,
                        semestre=semestre,
                        classe_id=int(classes_ids[0]),
                        type_ue_creation='composite'
                    )
                    db.session.add(ue_parent)
                    db.session.flush()

                    # Créer les Sous-UE
                    for sous_ue in sous_ues_data:
                        code_sous = f"{sous_ue['prefixe']}{code_base}"
                        heures_sous = sous_ue['credits'] * 12

                        ue_enfant = UE(
                            code_ue=code_sous,
                            intitule=sous_ue['intitule'],
                            credits=sous_ue['credits'],
                            coefficient=sous_ue['credits'],
                            heures=heures_sous,
                            semestre=semestre,
                            classe_id=int(classes_ids[0]),
                            type_ue_creation='simple',
                            ue_parent_id=ue_parent.id
                        )
                        db.session.add(ue_enfant)

                    ues_creees.append(f"{code_base} Composite ({len(sous_ues_data)} sous-UE, {credits_total} ECTS)")

                # MODE TRONC COMMUN
                elif mode_creation == 'tronc_commun':
                    classes_obj = [Classe.query.get(int(cid)) for cid in classes_ids if Classe.query.get(int(cid))]
                    annees = set([c.annee for c in classes_obj if c.annee])

                    if annees:
                        niveaux = sorted([f"L{a}" for a in annees])
                        libelle_tronc = f"Tronc Commun {'/'.join(niveaux)}"
                    else:
                        libelle_tronc = "Tronc Commun"

                    # Créer UE Parent Tronc Commun
                    ue_parent = UE(
                        code_ue=code_base,
                        intitule=f"{intitule} ({libelle_tronc})",
                        credits=credits_total,
                        coefficient=coefficient,
                        heures=heures,
                        semestre=semestre,
                        classe_id=None,
                        type_ue_creation='composite_tronc'
                    )
                    db.session.add(ue_parent)
                    db.session.flush()

                    # Associer classes
                    for classe_id in classes_ids:
                        classe = Classe.query.get(int(classe_id))
                        if classe:
                            ue_parent.classes.append(classe)

                    # Créer les Sous-UE
                    for sous_ue in sous_ues_data:
                        code_sous = f"{sous_ue['prefixe']}{code_base}"
                        heures_sous = sous_ue['credits'] * 12

                        ue_enfant = UE(
                            code_ue=code_sous,
                            intitule=f"{sous_ue['intitule']} ({libelle_tronc})",
                            credits=sous_ue['credits'],
                            coefficient=sous_ue['credits'],
                            heures=heures_sous,
                            semestre=semestre,
                            classe_id=None,
                            type_ue_creation='simple',
                            ue_parent_id=ue_parent.id
                        )
                        db.session.add(ue_enfant)
                        db.session.flush()

                        # Associer classes aux sous-UE
                        for classe_id in classes_ids:
                            classe = Classe.query.get(int(classe_id))
                            if classe:
                                ue_enfant.classes.append(classe)

                    ues_creees.append(f"{code_base} Composite {libelle_tronc} ({len(sous_ues_data)} sous-UE)")

                # MODE UE FILLES
                elif mode_creation == 'ue_filles':
                    for classe_id in classes_ids:
                        classe = Classe.query.get(int(classe_id))
                        if classe:
                            code_parent = f"{code_base}-{classe.code_classe}"

                            # Créer UE Parent
                            ue_parent = UE(
                                code_ue=code_parent,
                                intitule=intitule,
                                credits=credits_total,
                                coefficient=coefficient,
                                heures=heures,
                                semestre=semestre,
                                classe_id=int(classe_id),
                                type_ue_creation='composite'
                            )
                            db.session.add(ue_parent)
                            db.session.flush()

                            # Créer Sous-UE
                            for sous_ue in sous_ues_data:
                                code_sous = f"{sous_ue['prefixe']}{code_base}-{classe.code_classe}"
                                heures_sous = sous_ue['credits'] * 12

                                ue_enfant = UE(
                                    code_ue=code_sous,
                                    intitule=sous_ue['intitule'],
                                    credits=sous_ue['credits'],
                                    coefficient=sous_ue['credits'],
                                    heures=heures_sous,
                                    semestre=semestre,
                                    classe_id=int(classe_id),
                                    type_ue_creation='simple',
                                    ue_parent_id=ue_parent.id
                                )
                                db.session.add(ue_enfant)

                            ues_creees.append(f"{code_parent} Composite ({classe.nom_classe})")

            # =============================================
            # TYPE SIMPLE (Sans sous-UE)
            # =============================================
            else:
                credits = int(request.form.get('credits'))
                heures = credits * 12
                coefficient = credits

                # MODE SPÉCIFIQUE
                if mode_creation == 'ue_specifique':
                    if len(classes_ids) > 1:
                        flash("⚠️  Mode UE Spécifique : une seule classe autorisée.", "warning")
                        return redirect(url_for('directeur.ajouter_ue'))

                    classe = Classe.query.get(int(classes_ids[0]))
                    if classe:
                        nouvelle_ue = UE(
                            code_ue=code_base,
                            intitule=intitule,
                            credits=credits,
                            coefficient=coefficient,
                            heures=heures,
                            semestre=semestre,
                            classe_id=int(classes_ids[0]),
                            type_ue_creation='simple'
                        )
                        db.session.add(nouvelle_ue)
                        ues_creees.append(f"{code_base} ({classe.nom_classe})")

                # MODE TRONC COMMUN
                elif mode_creation == 'tronc_commun':
                    classes_obj = [Classe.query.get(int(cid)) for cid in classes_ids if Classe.query.get(int(cid))]
                    annees = set([c.annee for c in classes_obj if c.annee])

                    if annees:
                        niveaux = sorted([f"L{a}" for a in annees])
                        libelle_tronc = f"Tronc Commun {'/'.join(niveaux)}"
                    else:
                        libelle_tronc = "Tronc Commun"

                    ue_tronc = UE(
                        code_ue=code_base,
                        intitule=f"{intitule} ({libelle_tronc})",
                        credits=credits,
                        coefficient=coefficient,
                        heures=heures,
                        semestre=semestre,
                        classe_id=None,
                        type_ue_creation='tronc_commun'
                    )
                    db.session.add(ue_tronc)
                    db.session.flush()

                    for classe_id in classes_ids:
                        classe = Classe.query.get(int(classe_id))
                        if classe:
                            ue_tronc.classes.append(classe)

                    classes_noms = [c.nom_classe for c in classes_obj]
                    ues_creees.append(f"{code_base} ({libelle_tronc})")

                # MODE UE FILLES
                elif mode_creation == 'ue_filles':
                    for classe_id in classes_ids:
                        classe = Classe.query.get(int(classe_id))
                        if classe:
                            code_ue_unique = f"{code_base}-{classe.code_classe}"

                            nouvelle_ue = UE(
                                code_ue=code_ue_unique,
                                intitule=intitule,
                                credits=credits,
                                coefficient=coefficient,
                                heures=heures,
                                semestre=semestre,
                                classe_id=int(classe_id),
                                type_ue_creation='simple'
                            )
                            db.session.add(nouvelle_ue)
                            ues_creees.append(f"{code_ue_unique} ({classe.nom_classe})")

            db.session.commit()

            if len(ues_creees) > 0:
                flash(f"✅ {len(ues_creees)} UE créée(s) : {', '.join(ues_creees)}", "success")
            else:
                flash("❌ Aucune UE n'a été créée.", "info")

            return redirect(url_for('directeur.liste_ues'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erreur : {str(e)}", "danger")
            import traceback
            traceback.print_exc()

    return render_template('directeur/ajouter_ue.html', classes=classes)


@bp.route('/ue/<int:ue_id>')
@directeur_required
def detail_ue(ue_id):
    ue = UE.query.get_or_404(ue_id)
    enseignants = Enseignant.query.filter_by(actif=True).all()

    # Calcul moyenne rapide
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
    ues = UE.query.all()
    enseignants = Enseignant.query.filter_by(actif=True).all()
    return render_template('directeur/affectations.html', ues=ues, enseignants=enseignants)


# NOUVELLE ROUTE : Affectation simplifiée avec checkboxes
@bp.route('/affectations-simplifiees')
@directeur_required
def affectations_simplifiees():
    """Page d'affectation simplifiée avec checkboxes"""
    ues = UE.query.order_by(UE.code_ue).all()
    enseignants = Enseignant.query.filter_by(actif=True).order_by(Enseignant.nom).all()

    # Calculer les UE non affectées (sans aucun enseignant)
    # INCLURE les UE Tronc Commun sans prof
    ues_non_affectees = [ue for ue in ues if len(ue.enseignants) == 0]

    # Séparer les troncs communs des autres
    troncs_communs_non_affectes = [ue for ue in ues_non_affectees if ue.type_ue_creation == 'tronc_commun']
    ue_filles_non_affectees = [ue for ue in ues_non_affectees if ue.type_ue_creation != 'tronc_commun']

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
# ANNONCES
# =========================================================================
@bp.route('/publier_annonce', methods=['POST'])
@directeur_required
def publier_annonce():
    titre = request.form.get('titre')
    message = request.form.get('message')
    # Logique pour enregistrer l'annonce en BDD ici...
    flash(f"DIFFUSION EXÉCUTÉE : {titre}", "success")
    return redirect(url_for('directeur.dashboard'))

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

    return render_template('directeur/fiche_enseignant_print.html',
                           enseignant=enseignant, user=user,
                           password=password_display, date_edition=date_edition)

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

    # === SCEAU OFFICIEL (design amélioré) ===

    sceau_x = 150
    sceau_y = 100

    # Cercle externe or
    c.setStrokeColor(PolytechColors.GOLD)
    c.setLineWidth(4)
    c.circle(sceau_x, sceau_y, 45, stroke=1, fill=0)

    # Cercle interne
    c.setFillColor(PolytechColors.GOLD)
    c.setFillAlpha(0.2)
    c.circle(sceau_x, sceau_y, 42, stroke=0, fill=1)
    c.setFillAlpha(1)

    # Texte du sceau
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(PolytechColors.GOLD)
    c.drawCentredString(sceau_x, sceau_y + 8, "SCEAU")
    c.drawCentredString(sceau_x, sceau_y - 5, "OFFICIEL")
    c.setFont("Helvetica", 7)
    c.drawCentredString(sceau_x, sceau_y - 15, "2026")

    # Étoile au centre du sceau
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
from app.models import Livre
from werkzeug.utils import secure_filename
import os


@bp.route('/bibliotheque')
@directeur_required
def bibliotheque():
    livres = Livre.query.order_by(Livre.date_ajout.desc()).all()
    return render_template('directeur/bibliotheque.html', livres=livres)


@bp.route('/bibliotheque/ajouter', methods=['POST'])
@directeur_required
def ajouter_livre():
    from app.services.ia_bibliotheque import BibliothequeIA

    try:
        titre = request.form.get('titre')
        auteur = request.form.get('auteur')
        categorie = request.form.get('categorie')
        description = request.form.get('description')

        # 🤖 TRI AUTOMATIQUE PAR IA si pas de catégorie sélectionnée
        if not categorie or categorie == "":
            biblio_ia = BibliothequeIA()
            categorie = biblio_ia.determiner_categorie(titre, auteur, description)

            # Générer description si absente
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
            if cover:
                c_name = secure_filename(cover.filename)
                unique_cover = f"cover_{datetime.now().strftime('%Y%m%d%H%M')}_{c_name}"
                path_cover = os.path.join(current_app.root_path, 'static', 'library', 'covers')
                os.makedirs(path_cover, exist_ok=True)
                cover.save(os.path.join(path_cover, unique_cover))
                cover_name = unique_cover

            nouveau_livre = Livre(
                titre=titre, auteur=auteur, categorie=categorie,
                description=description,
                fichier_pdf=unique_pdf, image_couverture=cover_name
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

