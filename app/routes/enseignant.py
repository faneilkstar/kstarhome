# =========================================================
# 1. IMPORTS
# =========================================================
import csv
import io
import os
from datetime import datetime
from functools import wraps
import numpy as np

from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, current_app, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from config import Config

from app import db
from app.models import Enseignant, UE, Note, Etudiant, Classe, InscriptionUE, Document, ComposanteNote

# =========================================================
# CONFIGURATION
# =========================================================
bp = Blueprint('enseignant', __name__, url_prefix='/enseignant')

# =========================================================
# DÉCORATEURS
# =========================================================
def enseignant_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_enseignant:
            flash('Accès non autorisé.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_enseignant():
    if not current_user.is_authenticated:
        return None
    return current_user.enseignant_profile

# =========================================================
# ROUTE 1 : DASHBOARD
# =========================================================
@bp.route('/dashboard')
@enseignant_required
def dashboard():
    enseignant = get_current_enseignant()
    if not enseignant:
        return "Profil introuvable", 404

    ues = enseignant.ues
    total_etudiants = 0
    somme_notes = 0
    count_notes = 0

    for ue in ues:
        total_etudiants += ue.inscriptions.filter_by(statut='validé').count()
        notes = [n.note for n in ue.notes if n.note is not None]
        if notes:
            somme_notes += sum(notes)
            count_notes += len(notes)

    moyenne = round(somme_notes / count_notes, 2) if count_notes > 0 else 0

    return render_template('enseignant/dashboard.html',
                           enseignant=enseignant,
                           ues=ues,
                           total_etudiants=total_etudiants,
                           moyenne_globale=moyenne)

# =========================================================
# ROUTE 2 : MES UES
# =========================================================
@bp.route('/mes-ues')
@enseignant_required
def mes_ues():
    enseignant = get_current_enseignant()
    return render_template('enseignant/mes_ues.html', ues=enseignant.ues)

# =========================================================
# ROUTE 3 : DÉTAIL UE
# =========================================================
@bp.route('/ue/<int:ue_id>')
@enseignant_required
def detail_ue(ue_id):
    enseignant = get_current_enseignant()
    ue = UE.query.get_or_404(ue_id)

    if ue not in enseignant.ues:
        flash('Accès refusé.', 'danger')
        return redirect(url_for('enseignant.dashboard'))

    inscriptions = ue.inscriptions.filter_by(statut='validé').all()
    etudiants_notes = []
    for ins in inscriptions:
        note_obj = Note.query.filter_by(etudiant_id=ins.etudiant_id, ue_id=ue.id).first()
        etudiants_notes.append({
            'etudiant': ins.etudiant,
            'note': note_obj.note if note_obj else None,
            'session': note_obj.session if note_obj else 'normale'
        })

    return render_template('enseignant/detail_ue.html', ue=ue, etudiants_notes=etudiants_notes)

# =========================================================
# ROUTE 4 : SAISIR NOTES
# =========================================================
@bp.route('/ue/<int:ue_id>/saisir-notes', methods=['POST'])
@enseignant_required
def saisir_notes(ue_id):
    ue = UE.query.get_or_404(ue_id)
    count = 0
    for key, val in request.form.items():
        if key.startswith('note_') and val.strip():
            try:
                etu_id = int(key.split('_')[1])
                note_val = float(val)
                if 0 <= note_val <= 20:
                    note = Note.query.filter_by(etudiant_id=etu_id, ue_id=ue.id).first()
                    if note:
                        note.note = note_val
                    else:
                        db.session.add(Note(
                            etudiant_id=etu_id,
                            ue_id=ue.id,
                            note=note_val,
                            session='normale',
                            annee_academique=Config.ANNEE_ACADEMIQUE_ACTUELLE
                        ))
                    count += 1
            except ValueError:
                continue
    db.session.commit()
    flash(f'{count} notes enregistrées.', 'success')
    return redirect(url_for('enseignant.detail_ue', ue_id=ue_id))

# =========================================================
# ROUTE 5 : DOCUMENTS
# =========================================================
@bp.route('/documents')
@enseignant_required
def documents():
    enseignant = get_current_enseignant()
    ue_id = request.args.get('ue_id', type=int)

    ues = list(enseignant.ues)
    docs_query = Document.query.filter_by(enseignant_id=enseignant.id)

    if ue_id:
        ue = UE.query.get_or_404(ue_id)
        if ue not in enseignant.ues:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('enseignant.documents'))
        docs_query = docs_query.filter_by(classe_id=ue.classe_id)

    docs = docs_query.order_by(Document.date_creation.desc()).all()
    return render_template('enseignant/documents.html', documents=docs, ues=ues)


@bp.route('/documents/upload', methods=['POST'])
@enseignant_required
def upload_doc():
    enseignant = get_current_enseignant()
    titre = request.form.get('titre')
    ue_id = request.form.get('ue_id', type=int)
    fichier = request.files.get('file')

    if not (titre and ue_id and fichier):
        flash('Veuillez renseigner le titre, l’UE et le fichier.', 'warning')
        return redirect(url_for('enseignant.documents'))

    ue = UE.query.get_or_404(ue_id)
    if ue not in enseignant.ues:
        flash('Accès refusé.', 'danger')
        return redirect(url_for('enseignant.documents'))

    filename = secure_filename(fichier.filename)
    upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_path, exist_ok=True)
    fichier.save(os.path.join(upload_path, filename))

    doc = Document(
        titre=titre,
        nom_fichier=filename,
        type_doc='cours',
        enseignant_id=enseignant.id,
        classe_id=ue.classe_id
    )
    db.session.add(doc)
    db.session.commit()

    flash('Document publié.', 'success')
    return redirect(url_for('enseignant.documents', ue_id=ue_id))

# =========================================================
# ROUTE 6 : PUBLIER COURS
# =========================================================
@bp.route('/publier-cours', methods=['GET', 'POST'])
@enseignant_required
def publier_cours():
    enseignant = get_current_enseignant()
    classes = set([ue.classe for ue in enseignant.ues if ue.classe])

    if request.method == 'POST':
        titre = request.form.get('titre')
        classe_id = request.form.get('classe_id')
        fichier = request.files.get('fichier')

        if fichier and titre and classe_id:
            filename = secure_filename(fichier.filename)
            path = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(path, exist_ok=True)
            fichier.save(os.path.join(path, filename))

            doc = Document(
                titre=titre,
                nom_fichier=filename,
                type_doc='cours',
                enseignant_id=enseignant.id,
                classe_id=int(classe_id)
            )
            db.session.add(doc)
            db.session.commit()
            flash('Document publié.', 'success')
            return redirect(url_for('enseignant.dashboard'))

    return render_template('enseignant/publier_cours.html', classes=classes)

# =========================================================
# ROUTE 7 : LISTE ÉTUDIANTS (C'était le doublon !)
# =========================================================
@bp.route('/etudiants')
@enseignant_required
def liste_etudiants():
    enseignant = get_current_enseignant()
    etudiants_set = set()
    for ue in enseignant.ues:
        for ins in ue.inscriptions:
            if ins.statut == 'validé':
                etudiants_set.add(ins.etudiant)
    return render_template('enseignant/etudiants.html', etudiants=list(etudiants_set))

# =========================================================
# ROUTE 8 : EXPORT CSV
# =========================================================
@bp.route('/ue/<int:ue_id>/exporter-notes')
@enseignant_required
def exporter_notes(ue_id):
    ue = UE.query.get_or_404(ue_id)
    inscriptions = ue.inscriptions.filter_by(statut='validé').all()

    def generate():
        data = io.StringIO()
        w = csv.writer(data)
        w.writerow(['Matricule', 'Nom', 'Prénom', 'Note'])
        yield data.getvalue()
        data.seek(0); data.truncate(0)

        for ins in inscriptions:
            note = Note.query.filter_by(etudiant_id=ins.etudiant_id, ue_id=ue.id).first()
            val = str(note.note) if note else ""
            w.writerow([ins.etudiant.id, ins.etudiant.nom, ins.etudiant.prenom, val])
            yield data.getvalue()
            data.seek(0); data.truncate(0)

    return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename=notes_{ue.code_ue}.csv'})

# =========================================================
# ROUTE 9 : PROFIL
# =========================================================
@bp.route('/profil', methods=['GET', 'POST'])
@enseignant_required
def profil():
    enseignant = get_current_enseignant()
    if request.method == 'POST':
        if request.form.get('email'): enseignant.user.email = request.form.get('email')
        if request.form.get('specialite'): enseignant.specialite = request.form.get('specialite')
        if request.form.get('password'): enseignant.user.password = request.form.get('password')
        db.session.commit()
        flash('Profil mis à jour.', 'success')
    return render_template('enseignant/profil.html', enseignant=enseignant)


# =========================================================
# ROUTE 10 : CONFIGURER LES COMPOSANTES DE NOTES
# =========================================================
@bp.route('/ue/<int:ue_id>/configurer-composantes', methods=['GET', 'POST'])
@enseignant_required
def configurer_composantes(ue_id):
    """Permet à l'enseignant de définir les composantes de notes et leurs pondérations"""
    enseignant = get_current_enseignant()
    ue = UE.query.get_or_404(ue_id)

    # Vérifier que l'enseignant a accès à cette UE
    if ue not in enseignant.ues:
        flash('Accès refusé.', 'danger')
        return redirect(url_for('enseignant.dashboard'))

    if request.method == 'POST':
        try:
            # Supprimer les anciennes composantes
            ComposanteNote.query.filter_by(ue_id=ue_id).delete()

            # Récupérer les nouvelles composantes
            composantes_data = []
            index = 0
            while f'nom_{index}' in request.form:
                nom = request.form.get(f'nom_{index}', '').strip()
                ponderation = request.form.get(f'ponderation_{index}', '0')

                if nom and ponderation:
                    try:
                        pond_val = float(ponderation)
                        if 0 < pond_val <= 100:
                            composantes_data.append({
                                'nom': nom,
                                'ponderation': pond_val,
                                'ordre': index + 1
                            })
                    except ValueError:
                        pass
                index += 1

            # Vérifier que la somme des pondérations = 100%
            total_pond = sum([c['ponderation'] for c in composantes_data])
            if abs(total_pond - 100.0) > 0.01:
                flash(f'Erreur : La somme des pondérations doit être 100% (actuellement {total_pond}%)', 'danger')
                return redirect(url_for('enseignant.configurer_composantes', ue_id=ue_id))

            # Créer les nouvelles composantes
            for data in composantes_data:
                composante = ComposanteNote(
                    ue_id=ue_id,
                    nom=data['nom'],
                    ponderation=data['ponderation'],
                    ordre=data['ordre']
                )
                db.session.add(composante)

            db.session.commit()
            flash(f'Configuration des notes enregistrée avec succès ! ({len(composantes_data)} composantes)', 'success')
            return redirect(url_for('enseignant.detail_ue', ue_id=ue_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'enregistrement : {str(e)}', 'danger')

    # GET : Afficher le formulaire avec les composantes existantes
    composantes = ue.get_composantes_actives()
    return render_template('enseignant/configurer_composantes.html', ue=ue, composantes=composantes)


# =========================================================
# ROUTE 11 : SAISIR LES NOTES PAR COMPOSANTE
# =========================================================
@bp.route('/ue/<int:ue_id>/saisir-notes-composantes', methods=['GET', 'POST'])
@enseignant_required
def saisir_notes_composantes(ue_id):
    """Permet la saisie des notes pour chaque composante"""
    enseignant = get_current_enseignant()
    ue = UE.query.get_or_404(ue_id)

    if ue not in enseignant.ues:
        flash('Accès refusé.', 'danger')
        return redirect(url_for('enseignant.dashboard'))

    composante_id = request.args.get('composante_id', type=int)

    if not composante_id:
        flash('Veuillez sélectionner une composante.', 'warning')
        return redirect(url_for('enseignant.detail_ue', ue_id=ue_id))

    composante = ComposanteNote.query.get_or_404(composante_id)

    if composante.ue_id != ue_id:
        flash('Composante invalide.', 'danger')
        return redirect(url_for('enseignant.detail_ue', ue_id=ue_id))

    if request.method == 'POST':
        count = 0
        for key, val in request.form.items():
            if key.startswith('note_') and val.strip():
                try:
                    etu_id = int(key.split('_')[1])
                    note_val = float(val)

                    if 0 <= note_val <= 20:
                        # Chercher ou créer la note pour cette composante
                        note = Note.query.filter_by(
                            etudiant_id=etu_id,
                            ue_id=ue_id,
                            composante_id=composante_id
                        ).first()

                        if note:
                            note.note = note_val
                            note.date_saisie = datetime.utcnow()
                        else:
                            note = Note(
                                etudiant_id=etu_id,
                                ue_id=ue_id,
                                composante_id=composante_id,
                                note=note_val,
                                session='normale',
                                annee_academique=Config.ANNEE_ACADEMIQUE_ACTUELLE,
                                saisi_par_id=current_user.id
                            )
                            db.session.add(note)
                        count += 1
                except ValueError:
                    continue

        db.session.commit()
        flash(f'{count} notes enregistrées pour {composante.nom}.', 'success')
        return redirect(url_for('enseignant.detail_ue', ue_id=ue_id))

    # GET : Afficher le formulaire de saisie
    inscriptions = ue.inscriptions.filter_by(statut='validé').all()
    etudiants_notes = []

    for ins in inscriptions:
        note_obj = Note.query.filter_by(
            etudiant_id=ins.etudiant_id,
            ue_id=ue_id,
            composante_id=composante_id
        ).first()

        etudiants_notes.append({
            'etudiant': ins.etudiant,
            'note': note_obj.note if note_obj else None
        })

    return render_template('enseignant/saisir_notes_composantes.html',
                         ue=ue,
                         composante=composante,
                         etudiants_notes=etudiants_notes)


# =========================================================
# ROUTE 12 : SUPPRIMER UNE CONFIGURATION DE COMPOSANTES
# =========================================================
@bp.route('/ue/<int:ue_id>/supprimer-composantes', methods=['POST'])
@enseignant_required
def supprimer_composantes(ue_id):
    """Supprime la configuration des composantes et revient au système classique"""
    enseignant = get_current_enseignant()
    ue = UE.query.get_or_404(ue_id)

    if ue not in enseignant.ues:
        flash('Accès refusé.', 'danger')
        return redirect(url_for('enseignant.dashboard'))

    try:
        # Supprimer toutes les composantes de l'UE
        ComposanteNote.query.filter_by(ue_id=ue_id).delete()
        db.session.commit()
        flash('Configuration des composantes supprimée. Vous utilisez maintenant le système de notation classique.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur : {str(e)}', 'danger')

    return redirect(url_for('enseignant.detail_ue', ue_id=ue_id))


# Imports nécessaires
from app.models import Absence, Etudiant, UE


@bp.route('/appel')
@enseignant_required
def choix_appel():
    enseignant = get_current_enseignant()
    return render_template('enseignant/choix_appel.html', ues=enseignant.ues)


@bp.route('/appel/faire/<int:ue_id>', methods=['GET', 'POST'])
@enseignant_required
def faire_appel(ue_id):
    ue = UE.query.get_or_404(ue_id)
    enseignant = get_current_enseignant()

    # Vérif sécurité : est-ce son cours ?
    if ue not in enseignant.ues:
        flash("Ce n'est pas votre cours.", "danger")
        return redirect(url_for('enseignant.dashboard'))

    # On récupère les étudiants INSCRITS et VALIDÉS dans cette UE
    # (On passe par les inscriptions)
    etudiants = [ins.etudiant for ins in ue.inscriptions if ins.statut == 'validé']

    if request.method == 'POST':
        date_jour = datetime.utcnow().date()
        count = 0

        # On parcourt le formulaire
        # Le formulaire renvoie les IDs des élèves cochés comme "ABSENTS"
        absents_ids = request.form.getlist('absent_id')

        for etu_id in absents_ids:
            nouvelle_absence = Absence(
                etudiant_id=int(etu_id),
                ue_id=ue.id,
                enseignant_id=enseignant.id,
                date_absence=date_jour,
                justifiee=False,
                motif="Absence non justifiée"
            )
            db.session.add(nouvelle_absence)
            count += 1

        try:
            db.session.commit()
            flash(f"Appel enregistré : {count} absent(s).", "success")
            return redirect(url_for('enseignant.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {str(e)}", "danger")

    return render_template('enseignant/feuille_appel.html', ue=ue, etudiants=etudiants)


# =========================================================
# ROUTE 13 : BIBLIOTHÈQUE (NOUVEAU)
# =========================================================
from app.models import Livre

@bp.route('/bibliotheque')
@enseignant_required
def bibliotheque():
    """Page de gestion de la bibliothèque pour l'enseignant"""
    livres = Livre.query.order_by(Livre.date_ajout.desc()).all()
    return render_template('enseignant/bibliotheque.html', livres=livres)


@bp.route('/bibliotheque/ajouter', methods=['POST'])
@enseignant_required
def ajouter_livre():
    """Ajouter un livre à la bibliothèque"""
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
        db.session.rollback()
        flash(f"❌ Erreur: {str(e)}", "danger")

    return redirect(url_for('enseignant.bibliotheque'))
