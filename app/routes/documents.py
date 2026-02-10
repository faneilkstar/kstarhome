from flask import Blueprint, render_template, redirect, url_for, flash, send_file, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Etudiant, Document
import os

# Import du générateur PDF
# Assure-toi que le fichier app/utils/pdf_generator.py existe bien !
from app.utils.pdf_generator import (
    generer_attestation_scolarite,
    generer_releve_notes,
    generer_bulletin_avec_graphique,
    generer_carte_etudiant
)

bp = Blueprint('documents', __name__, url_prefix='/documents')


# --- DÉCORATEUR DE SÉCURITÉ ---
def directeur_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_directeur():
            flash('Accès réservé à la direction.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


# --- 1. LISTE DES DOCUMENTS (C'est cette route que le Dashboard cherche) ---
@bp.route('/liste')
@directeur_required
def liste_documents_directeur():
    """Affiche la liste de tous les documents générés"""
    try:
        # On récupère les 100 derniers documents
        documents = Document.query.order_by(Document.date_creation.desc()).limit(100).all()
    except Exception as e:
        documents = []
        print(f"Erreur DB: {e}")

    return render_template('directeur/documents.html', documents=documents)


# --- 2. TÉLÉCHARGEMENT ---
@bp.route('/telecharger/<int:document_id>')
@login_required
def telecharger_document(document_id):
    """Télécharge un fichier s'il existe"""
    document = Document.query.get_or_404(document_id)

    # Vérification simple des droits
    if not current_user.is_directeur() and document.user_id != current_user.id:
        flash("Accès refusé.", "danger")
        return redirect(url_for('auth.login'))

    if os.path.exists(document.chemin_fichier):
        return send_file(document.chemin_fichier, as_attachment=True)
    else:
        flash('Fichier introuvable sur le serveur (peut-être supprimé ?).', 'danger')
        return redirect(request.referrer or url_for('documents.liste_documents_directeur'))


# --- 3. GÉNÉRATION DE PDF ---

@bp.route('/generer/attestation/<int:etudiant_id>')
@directeur_required
def generer_attestation(etudiant_id):
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    try:
        # 1. Création du PDF
        filename = generer_attestation_scolarite(etudiant)

        # 2. Enregistrement en base de données
        document = Document(
            type='attestation',
            chemin_fichier=filename,
            user_id=etudiant.user_id,
            description=f'Attestation - {etudiant.nom} {etudiant.prenom}'
        )
        db.session.add(document)
        db.session.commit()

        flash('Attestation générée avec succès !', 'success')
        return send_file(filename, as_attachment=True)

    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la génération : {str(e)}', 'danger')
        return redirect(url_for('directeur.detail_etudiant', etudiant_id=etudiant_id))


@bp.route('/generer/releve/<int:etudiant_id>')
@directeur_required
def generer_releve(etudiant_id):
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    try:
        filename = generer_releve_notes(etudiant)

        document = Document(
            type='releve',
            chemin_fichier=filename,
            user_id=etudiant.user_id,
            description=f'Relevé de notes - {etudiant.nom}'
        )
        db.session.add(document)
        db.session.commit()

        flash('Relevé généré !', 'success')
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
        return redirect(url_for('directeur.detail_etudiant', etudiant_id=etudiant_id))


@bp.route('/generer/carte/<int:etudiant_id>')
@directeur_required
def generer_carte(etudiant_id):
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    try:
        filename = generer_carte_etudiant(etudiant)

        document = Document(
            type='carte',
            chemin_fichier=filename,
            user_id=etudiant.user_id,
            description=f'Carte Étudiant - {etudiant.nom}'
        )
        db.session.add(document)
        db.session.commit()

        flash('Carte générée !', 'success')
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
        return redirect(url_for('directeur.detail_etudiant', etudiant_id=etudiant_id))

    # --- 4. VUE ÉTUDIANT (À AJOUTER) ---
@bp.route('/mes-documents')
@login_required
def mes_documents_etudiant():
    """Permet à l'étudiant de voir et télécharger ses propres documents"""
    if not current_user.is_etudiant():
        flash("Accès réservé aux étudiants.", "danger")
        return redirect(url_for('auth.login'))

    # On récupère les documents appartenant à l'utilisateur connecté
    mes_docs = Document.query.filter_by(user_id=current_user.id).order_by(Document.date_creation.desc()).all()

    return render_template('etudiant/documents.html', documents=mes_docs)