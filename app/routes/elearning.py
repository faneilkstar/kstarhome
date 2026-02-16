"""
Plateforme E-Learning
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

from app import db
from app.models import Cours, Quiz, QuestionQuiz, TentativeQuiz, Devoir, RenduDevoir, Etudiant

elearning_bp = Blueprint('elearning', __name__, url_prefix='/elearning')


@elearning_bp.route('/mes-cours')
@login_required
def mes_cours():
    """Liste des cours disponibles pour l'étudiant"""
    if current_user.role != 'ETUDIANT':
        flash('Accès réservé aux étudiants', 'danger')
        return redirect(url_for('main.index'))

    etudiant = current_user.etudiant_profile

    # Cours de ses UE
    cours_disponibles = Cours.query.filter(
        Cours.publie == True,
        Cours.matiere_id.in_([m.id for m in etudiant.classe.matieres])
    ).order_by(Cours.ordre).all()

    return render_template('elearning/mes_cours.html', cours=cours_disponibles)


@elearning_bp.route('/cours/<int:cours_id>')
@login_required
def voir_cours(cours_id):
    """Voir un cours"""
    cours = Cours.query.get_or_404(cours_id)

    return render_template('elearning/voir_cours.html', cours=cours)


@elearning_bp.route('/quiz/<int:quiz_id>')
@login_required
def voir_quiz(quiz_id):
    """Page de présentation d'un quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    etudiant = current_user.etudiant_profile

    # Tentatives précédentes
    tentatives = TentativeQuiz.query.filter_by(
        quiz_id=quiz.id,
        etudiant_id=etudiant.id
    ).order_by(TentativeQuiz.date_debut.desc()).all()

    # Vérifier si peut encore tenter
    peut_tenter = len([t for t in tentatives if t.terminee]) < quiz.tentatives_autorisees

    return render_template('elearning/voir_quiz.html',
                           quiz=quiz,
                           tentatives=tentatives,
                           peut_tenter=peut_tenter)


@elearning_bp.route('/quiz/<int:quiz_id>/commencer', methods=['POST'])
@login_required
def commencer_quiz(quiz_id):
    """Commencer une tentative de quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    etudiant = current_user.etudiant_profile

    # Vérifier le nombre de tentatives
    nb_tentatives = TentativeQuiz.query.filter_by(
        quiz_id=quiz.id,
        etudiant_id=etudiant.id,
        terminee=True
    ).count()

    if nb_tentatives >= quiz.tentatives_autorisees:
        flash('Nombre maximum de tentatives atteint', 'warning')
        return redirect(url_for('elearning.voir_quiz', quiz_id=quiz.id))

    # Créer la tentative
    tentative = TentativeQuiz(
        quiz_id=quiz.id,
        etudiant_id=etudiant.id,
        note_totale=sum(q.points for q in quiz.questions)
    )

    db.session.add(tentative)
    db.session.commit()

    return redirect(url_for('elearning.passer_quiz', tentative_id=tentative.id))


@elearning_bp.route('/quiz/tentative/<int:tentative_id>')
@login_required
def passer_quiz(tentative_id):
    """Interface pour passer le quiz"""
    tentative = TentativeQuiz.query.get_or_404(tentative_id)

    # Vérifier que c'est le bon étudiant
    if tentative.etudiant_id != current_user.etudiant_profile.id:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('elearning.mes_cours'))

    if tentative.terminee:
        flash('Quiz déjà terminé', 'info')
        return redirect(url_for('elearning.resultat_quiz', tentative_id=tentative.id))

    quiz = tentative.quiz
    questions = quiz.questions

    # Mélanger si nécessaire
    if quiz.melanger_questions:
        import random
        questions = list(questions)
        random.shuffle(questions)

    return render_template('elearning/passer_quiz.html',
                           tentative=tentative,
                           quiz=quiz,
                           questions=questions)


@elearning_bp.route('/quiz/tentative/<int:tentative_id>/soumettre', methods=['POST'])
@login_required
def soumettre_quiz(tentative_id):
    """Soumettre les réponses du quiz"""
    tentative = TentativeQuiz.query.get_or_404(tentative_id)

    if tentative.etudiant_id != current_user.etudiant_profile.id:
        return jsonify({'error': 'Non autorisé'}), 403

    if tentative.terminee:
        return jsonify({'error': 'Quiz déjà terminé'}), 400

    reponses = request.json.get('reponses', {})

    # Corriger automatiquement
    note_obtenue = 0
    quiz = tentative.quiz

    for question in quiz.questions:
        reponse_etudiant = reponses.get(str(question.id))
        reponses_correctes = json.loads(question.reponses_correctes)

        # Correction selon le type
        if question.type_question == 'qcm_unique':
            if reponse_etudiant in reponses_correctes:
                note_obtenue += question.points

        elif question.type_question == 'qcm_multiple':
            if set(reponse_etudiant) == set(reponses_correctes):
                note_obtenue += question.points

        elif question.type_question == 'vrai_faux':
            if reponse_etudiant == reponses_correctes[0]:
                note_obtenue += question.points

    # Enregistrer les résultats
    tentative.reponses = json.dumps(reponses)
    tentative.note_obtenue = note_obtenue
    tentative.pourcentage = (note_obtenue / tentative.note_totale) * 100
    tentative.date_fin = datetime.utcnow()
    tentative.duree_minutes = int((tentative.date_fin - tentative.date_debut).total_seconds() / 60)
    tentative.terminee = True
    tentative.reussie = tentative.note_obtenue >= quiz.note_passage

    db.session.commit()

    return jsonify({
        'success': True,
        'note': note_obtenue,
        'total': tentative.note_totale,
        'pourcentage': tentative.pourcentage,
        'reussie': tentative.reussie
    })


@elearning_bp.route('/quiz/resultat/<int:tentative_id>')
@login_required
def resultat_quiz(tentative_id):
    """Afficher les résultats d'un quiz"""
    tentative = TentativeQuiz.query.get_or_404(tentative_id)

    if tentative.etudiant_id != current_user.etudiant_profile.id:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('elearning.mes_cours'))

    # Détail des réponses
    reponses_etudiant = json.loads(tentative.reponses) if tentative.reponses else {}

    questions_detail = []
    for question in tentative.quiz.questions:
        reponse = reponses_etudiant.get(str(question.id))
        correctes = json.loads(question.reponses_correctes)

        questions_detail.append({
            'question': question,
            'reponse_etudiant': reponse,
            'reponses_correctes': correctes,
            'correct': reponse in correctes if question.type_question == 'qcm_unique' else set(reponse) == set(
                correctes)
        })

    return render_template('elearning/resultat_quiz.html',
                           tentative=tentative,
                           questions_detail=questions_detail)


@elearning_bp.route('/devoirs')
@login_required
def mes_devoirs():
    """Liste des devoirs de l'étudiant"""
    etudiant = current_user.etudiant_profile

    devoirs = Devoir.query.filter_by(classe_id=etudiant.classe_id).order_by(Devoir.date_limite).all()

    # Ajouter le statut de rendu
    devoirs_avec_statut = []
    for devoir in devoirs:
        rendu = RenduDevoir.query.filter_by(
            devoir_id=devoir.id,
            etudiant_id=etudiant.id
        ).first()

        devoirs_avec_statut.append({
            'devoir': devoir,
            'rendu': rendu,
            'en_retard': datetime.utcnow() > devoir.date_limite if not rendu else rendu.en_retard
        })

    return render_template('elearning/mes_devoirs.html', devoirs=devoirs_avec_statut)


@elearning_bp.route('/devoir/<int:devoir_id>/rendre', methods=['GET', 'POST'])
@login_required
def rendre_devoir(devoir_id):
    """Rendre un devoir"""
    devoir = Devoir.query.get_or_404(devoir_id)
    etudiant = current_user.etudiant_profile

    # Vérifier si déjà rendu
    rendu_existant = RenduDevoir.query.filter_by(
        devoir_id=devoir.id,
        etudiant_id=etudiant.id
    ).first()

    if request.method == 'POST':
        if rendu_existant:
            flash('Devoir déjà rendu', 'warning')
            return redirect(url_for('elearning.mes_devoirs'))

        fichier = request.files.get('fichier')
        commentaire = request.form.get('commentaire', '')

        if not fichier:
            flash('Veuillez joindre un fichier', 'danger')
            return redirect(url_for('elearning.rendre_devoir', devoir_id=devoir.id))

        # Sauvegarder le fichier
        upload_dir = f'documents/devoirs/rendus/{devoir.id}'
        os.makedirs(upload_dir, exist_ok=True)

        filename = secure_filename(f"{etudiant.matricule}_{fichier.filename}")
        filepath = os.path.join(upload_dir, filename)
        fichier.save(filepath)

        # Créer le rendu
        rendu = RenduDevoir(
            devoir_id=devoir.id,
            etudiant_id=etudiant.id,
            fichier_path=filepath,
            commentaire_etudiant=commentaire,
            en_retard=datetime.utcnow() > devoir.date_limite
        )

        db.session.add(rendu)
        db.session.commit()

        flash('Devoir rendu avec succès !', 'success')
        return redirect(url_for('elearning.mes_devoirs'))

    return render_template('elearning/rendre_devoir.html',
                           devoir=devoir,
                           rendu_existant=rendu_existant)