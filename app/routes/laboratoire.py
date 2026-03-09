"""
Routes pour le Laboratoire Virtuel et les Simulations
Gère les TPs, simulations et interactions IA
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import (
    User, Etudiant, Enseignant, TP, SessionTP, MesureSimulation,
    InteractionIA, UE
)

# Hiérarchie d'IA : V3 (Gemini Pro) > V2 (améliorée) > Ultra > Avancée > Basique
IA_VERSION = 'basique'
try:
    from app.services.ia_laboratoire_v3 import IAFactoryV3 as IAFactory
    IA_VERSION = 'v3-gemini-pro'
    print(f"✅ [LABORATOIRE] IA V3 chargée (Gemini Pro + Fallback intelligent)")
except Exception as e:
    print(f"⚠️  [LABO] IA V3 non disponible: {e}")
    try:
        from app.services.ia_laboratoire_v2 import IAFactoryV2 as IAFactory
        IA_VERSION = 'v2-amelioree'
        print(f"✅ [LABORATOIRE] IA V2 chargée (avec Gemini + Fallback robuste)")
    except Exception as e2:
        print(f"⚠️  [LABO] IA V2 non disponible: {e2}")
        try:
            from app.services.ia_laboratoire_ultra import IAFactoryUltra as IAFactory
            IA_VERSION = 'ultra'
            print(f"✅ [LABORATOIRE] IA Ultra chargée")
        except Exception as e3:
            print(f"⚠️  [LABO] IA Ultra non disponible: {e3}")
            try:
                from app.services.ia_laboratoire_avancee import IAFactoryAvancee as IAFactory
                IA_VERSION = 'avancee'
                print(f"✅ [LABORATOIRE] IA Avancée chargée")
            except Exception as e4:
                print(f"⚠️  [LABO] IA Avancée non disponible: {e4}")
                from app.services.ia_laboratoire import IAFactory
                IA_VERSION = 'basique'
                print(f"✅ [LABORATOIRE] IA Basique chargée (fallback)")

print(f"🔬 [LABORATOIRE] IA chargée: version {IA_VERSION}")

from datetime import datetime
import json

laboratoire_bp = Blueprint('laboratoire', __name__, url_prefix='/laboratoire')


# ============================================================
# DECORATEURS DE ROLE
# ============================================================
def enseignant_required(f):
    """Décorateur pour restreindre l'accès aux enseignants"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ENSEIGNANT':
            flash('Accès réservé aux enseignants', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def etudiant_required(f):
    """Décorateur pour restreindre l'accès aux étudiants"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ETUDIANT':
            flash('Accès réservé aux étudiants', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# HUB PRINCIPAL - SELON LE ROLE
# ============================================================
@laboratoire_bp.route('/')
@login_required
def hub():
    """Hub principal du laboratoire - redirige selon le rôle"""
    if current_user.role == 'DIRECTEUR':
        return redirect(url_for('laboratoire.hub_directeur'))
    elif current_user.role == 'ENSEIGNANT':
        return redirect(url_for('laboratoire.hub_enseignant'))
    elif current_user.role == 'ETUDIANT':
        return redirect(url_for('laboratoire.hub_etudiant'))
    else:
        flash('Rôle non reconnu', 'danger')
        return redirect(url_for('auth.login'))


# ============================================================
# HUB DIRECTEUR
# ============================================================
@laboratoire_bp.route('/directeur')
@login_required
def hub_directeur():
    """Hub du laboratoire pour le directeur"""
    # Statistiques globales
    total_tps = TP.query.count()
    total_sessions = SessionTP.query.count()
    tps_actifs = TP.query.filter_by(actif=True).count()
    total_mesures = MesureSimulation.query.count()
    total_interactions = InteractionIA.query.count()

    # Tous les TPs
    tps = TP.query.order_by(TP.date_creation.desc()).all()

    # TPs par type de simulation
    tps_par_type = db.session.query(
        TP.type_simulation,
        db.func.count(TP.id)
    ).group_by(TP.type_simulation).all()

    # Sessions récentes
    sessions_recentes = SessionTP.query.order_by(
        SessionTP.date_debut.desc()
    ).limit(10).all()

    return render_template('laboratoire/hub_directeur.html',
                         total_tps=total_tps,
                         total_sessions=total_sessions,
                         tps_actifs=tps_actifs,
                         total_mesures=total_mesures,
                         total_interactions=total_interactions,
                         tps=tps,
                         tps_par_type=tps_par_type,
                         sessions_recentes=sessions_recentes)


# ============================================================
# HUB ENSEIGNANT
# ============================================================
@laboratoire_bp.route('/enseignant')
@login_required
@enseignant_required
def hub_enseignant():
    """Hub du laboratoire pour l'enseignant"""
    try:
        enseignant = current_user.enseignant_profile

        if not enseignant:
            flash('⚠️ Profil enseignant introuvable. Veuillez contacter l\'administrateur.', 'danger')
            return redirect(url_for('enseignant.dashboard'))

        # TPs créés par cet enseignant
        mes_tps = TP.query.filter_by(enseignant_id=enseignant.id).order_by(TP.date_creation.desc()).all()

        # Regrouper les TPs par UE
        ues_tps = []
        for ue in enseignant.ues:
            tps_ue = [tp for tp in mes_tps if tp.ue_id == ue.id]
            if tps_ue or True:  # Afficher toutes les UE même sans TP
                ues_tps.append({
                    'ue': ue,
                    'tps': tps_ue,
                    'nb_tps': len(tps_ue)
                })

        # Sessions actives liées aux TPs de l'enseignant
        sessions_actives = db.session.query(SessionTP).join(TP).filter(
            TP.enseignant_id == enseignant.id,
            SessionTP.statut.in_(['en_cours', 'terminé'])
        ).order_by(SessionTP.date_debut.desc()).limit(20).all()

        # Statistiques globales
        total_tps = len(mes_tps)
        total_sessions = db.session.query(SessionTP).join(TP).filter(
            TP.enseignant_id == enseignant.id
        ).count()

        sessions_a_evaluer = db.session.query(SessionTP).join(TP).filter(
            TP.enseignant_id == enseignant.id,
            SessionTP.statut == 'terminé',
            SessionTP.note_finale == None
        ).count()

        return render_template('laboratoire/hub_enseignant.html',
                             enseignant=enseignant,
                             mes_tps=mes_tps,
                             ues_tps=ues_tps,
                             sessions_actives=sessions_actives,
                             total_tps=total_tps,
                             total_sessions=total_sessions,
                             sessions_a_evaluer=sessions_a_evaluer,
                             ia_version=IA_VERSION,
                             SessionTP=SessionTP)

    except Exception as e:
        print(f"❌ [ERREUR] Hub enseignant : {e}")
        import traceback
        traceback.print_exc()
        flash(f'❌ Erreur lors du chargement du laboratoire : {str(e)}', 'danger')
        return redirect(url_for('enseignant.dashboard'))


# ============================================================
# HUB ÉTUDIANT
# ============================================================
@laboratoire_bp.route('/etudiant')
@login_required
@etudiant_required
def hub_etudiant():
    """Hub du laboratoire pour l'étudiant"""
    etudiant = current_user.etudiant_profile

    # TPs disponibles par UE
    ues_avec_tps = []
    if etudiant.classe:
        # Récupérer les UEs de la classe de l'étudiant
        for ue in etudiant.classe.ues:
            tps_ue = TP.query.filter_by(ue_id=ue.id, actif=True).all()
            if tps_ue:
                ues_avec_tps.append({
                    'ue': ue,
                    'tps': tps_ue,
                    'nb_tps': len(tps_ue)
                })

    # Mes sessions
    mes_sessions = SessionTP.query.filter_by(etudiant_id=etudiant.id).order_by(
        SessionTP.date_debut.desc()
    ).all()

    # Sessions en cours
    sessions_en_cours = [s for s in mes_sessions if s.statut == 'en_cours']

    # Statistiques
    nb_sessions_total = len(mes_sessions)
    nb_sessions_terminees = len([s for s in mes_sessions if s.statut == 'terminé'])

    return render_template('laboratoire/hub_etudiant.html',
                         etudiant=etudiant,
                         ues_avec_tps=ues_avec_tps,
                         mes_sessions=mes_sessions,
                         sessions_en_cours=sessions_en_cours,
                         nb_sessions_total=nb_sessions_total,
                         nb_sessions_terminees=nb_sessions_terminees,
                         SessionTP=SessionTP)


# ============================================================
# CRÉATION DE TP (ENSEIGNANT)
# ============================================================
@laboratoire_bp.route('/creer-tp', methods=['GET', 'POST'])
@login_required
@enseignant_required
def creer_tp():
    """Créer un nouveau TP"""
    if request.method == 'POST':
        enseignant = current_user.enseignant_profile

        # Gestion du fichier sujet
        fichier_sujet_path = None
        if 'fichier_sujet' in request.files:
            file = request.files['fichier_sujet']
            if file and file.filename:
                try:
                    filename = secure_filename(f"tp_{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")

                    # Chemin local pour sauvegarde
                    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'tps')
                    os.makedirs(upload_dir, exist_ok=True)

                    file.save(os.path.join(upload_dir, filename))

                    # Chemin relatif pour la BDD (compatible static)
                    fichier_sujet_path = f"uploads/tps/{filename}"
                except Exception as e:
                    print(f"Erreur upload: {e}")
                    flash(f"Erreur lors de l'upload du fichier: {e}", 'warning')

        tp = TP(
            titre=request.form.get('titre'),
            description=request.form.get('description'),
            type_simulation=request.form.get('type_simulation'),
            ia_nom=request.form.get('ia_nom', 'ETA'),
            fichier_consigne=request.form.get('consignes', '{}'),
            fichier_sujet=fichier_sujet_path,
            bareme=request.form.get('criteres_evaluation', '{}'),
            enseignant_id=enseignant.id,
            actif=True,
            note_sur=20
        )

        # UE associée
        ue_id = request.form.get('ue_id')
        if ue_id:
            tp.ue_id = int(ue_id)

        # Date limite
        date_limite = request.form.get('date_limite')
        if date_limite:
            tp.date_limite = datetime.strptime(date_limite, '%Y-%m-%d')

        db.session.add(tp)
        db.session.commit()

        flash(f'TP "{tp.titre}" créé avec succès !', 'success')
        return redirect(url_for('laboratoire.hub_enseignant'))

    # GET - Afficher le formulaire
    enseignant = current_user.enseignant_profile
    mes_ues = enseignant.ues

    types_simulation = [
        ('buck', 'Convertisseur Buck'),
        ('signal_fourier', 'Traitement du Signal'),
        ('thermodynamique', 'Thermodynamique'),
        ('chute_libre', 'Mécanique - Chute Libre'),
        ('rdm_poutre', 'Résistance des Matériaux'),
        ('stock_flux', 'Gestion de Stock')
    ]

    assistants_ia = [
        ('ETA', 'ETA - Assistant Pédagogique'),
        ('ALPHA', 'ALPHA - Expert Électronique'),
        ('KAYT', 'KAYT - Spécialiste Simulations')
    ]

    return render_template('laboratoire/creer_tp.html',
                         mes_ues=mes_ues,
                         types_simulation=types_simulation,
                         assistants_ia=assistants_ia,
                         ue=None)  # Pour éviter l'erreur dans le template


# ============================================================
# ÉDITION DE TP
# ============================================================
@laboratoire_bp.route('/editer-tp/<int:tp_id>', methods=['GET', 'POST'])
@login_required
@enseignant_required
def editer_tp(tp_id):
    """Éditer un TP existant"""
    tp = TP.query.get_or_404(tp_id)
    enseignant = current_user.enseignant_profile

    # Vérifier que c'est bien le créateur
    if tp.enseignant_id != enseignant.id:
        flash('Vous ne pouvez éditer que vos propres TPs', 'danger')
        return redirect(url_for('laboratoire.hub_enseignant'))

    if request.method == 'POST':
        tp.titre = request.form.get('titre')
        tp.description = request.form.get('description')
        tp.type_simulation = request.form.get('type_simulation')
        tp.ia_nom = request.form.get('ia_nom', 'ETA')
        tp.fichier_consigne = request.form.get('consignes', '{}')
        tp.bareme = request.form.get('criteres_evaluation', '{}')
        tp.actif = request.form.get('actif') == 'on'

        ue_id = request.form.get('ue_id')
        tp.ue_id = int(ue_id) if ue_id else None

        date_limite = request.form.get('date_limite')
        if date_limite:
            tp.date_limite = datetime.strptime(date_limite, '%Y-%m-%d')

        db.session.commit()

        flash(f'TP "{tp.titre}" mis à jour !', 'success')
        return redirect(url_for('laboratoire.detail_tp', tp_id=tp.id))

    # GET
    mes_ues = enseignant.ues

    types_simulation = [
        ('buck', 'Convertisseur Buck'),
        ('signal_fourier', 'Traitement du Signal'),
        ('thermodynamique', 'Thermodynamique'),
        ('chute_libre', 'Mécanique - Chute Libre'),
        ('rdm_poutre', 'Résistance des Matériaux'),
        ('stock_flux', 'Gestion de Stock')
    ]

    assistants_ia = [
        ('ETA', 'ETA - Assistant Pédagogique'),
        ('ALPHA', 'ALPHA - Expert Électronique'),
        ('KAYT', 'KAYT - Spécialiste Simulations')
    ]

    return render_template('laboratoire/editer_tp.html',
                         tp=tp,
                         mes_ues=mes_ues,
                         types_simulation=types_simulation,
                         assistants_ia=assistants_ia)


# ============================================================
# DÉTAIL D'UN TP
# ============================================================
@laboratoire_bp.route('/tp/<int:tp_id>')
@login_required
def detail_tp(tp_id):
    """Voir les détails d'un TP"""
    tp = TP.query.get_or_404(tp_id)

    # Statistiques
    total_sessions = SessionTP.query.filter_by(tp_id=tp.id).count()
    sessions_terminees = SessionTP.query.filter_by(
        tp_id=tp.id,
        statut='terminé'
    ).count()

    # Note moyenne
    sessions_notees = SessionTP.query.filter_by(tp_id=tp.id).filter(
        SessionTP.note_finale.isnot(None)
    ).all()

    note_moyenne = None
    if sessions_notees:
        note_moyenne = sum(s.note_finale for s in sessions_notees) / len(sessions_notees)

    return render_template('laboratoire/detail_tp.html',
                         tp=tp,
                         total_sessions=total_sessions,
                         sessions_terminees=sessions_terminees,
                         note_moyenne=note_moyenne)


# ============================================================
# DÉMARRER UNE SESSION DE TP (ÉTUDIANT)
# ============================================================
@laboratoire_bp.route('/demarrer-tp/<int:tp_id>', methods=['POST'])
@login_required
@etudiant_required
def demarrer_tp(tp_id):
    """Démarrer une nouvelle session de TP"""
    tp = TP.query.get_or_404(tp_id)
    etudiant = current_user.etudiant_profile

    # Vérifier qu'il n'y a pas déjà une session en cours
    session_en_cours = SessionTP.query.filter_by(
        tp_id=tp.id,
        etudiant_id=etudiant.id,
        statut='en_cours'
    ).first()

    if session_en_cours:
        flash('Vous avez déjà une session en cours pour ce TP', 'warning')
        return redirect(url_for('laboratoire.salle_tp', session_id=session_en_cours.id))

    # Créer une nouvelle session
    session = SessionTP(
        tp_id=tp.id,
        etudiant_id=etudiant.id,
        date_debut=datetime.utcnow(),
        statut='en_cours'
    )

    db.session.add(session)
    db.session.commit()

    flash(f'Session de TP "{tp.titre}" démarrée !', 'success')
    return redirect(url_for('laboratoire.salle_tp', session_id=session.id))


# ============================================================
# SALLE DE TP (SIMULATION EN DIRECT)
# ============================================================
@laboratoire_bp.route('/salle/<string:session_id>')
@login_required
@etudiant_required
def salle_tp(session_id):
    """Salle de TP virtuelle avec simulation"""
    session = None
    tp = None
    interactions = []
    etudiant = current_user.etudiant_profile

    if session_id.isdigit():
        session = SessionTP.query.get_or_404(int(session_id))
        if session.etudiant_id != etudiant.id:
            flash('Cette session ne vous appartient pas', 'danger')
            return redirect(url_for('laboratoire.hub_etudiant'))
        tp = session.tp
        interactions = InteractionIA.query.filter_by(session_id=session.id).order_by(InteractionIA.timestamp.asc()).all()
    else:
        # Charger le TP virtuel par nom de module
        tp = TP.query.filter_by(type_simulation=session_id).first()
        session = None
        interactions = []
        # Vérifier la présence du JS de simulation
        import os
        js_path = os.path.join('static', 'js', f'simulation_{session_id}.js')
        full_js_path = os.path.join(os.path.dirname(__file__), '..', js_path)
        if not tp and not os.path.exists(full_js_path):
            return render_template('laboratoire/labo_not_found.html', session_id=session_id)
    return render_template('laboratoire/salle_tp.html', session=session, tp=tp, interactions=interactions)


# ============================================================
# API - SAUVEGARDER RÉSULTAT DE SIMULATION
# ============================================================
@laboratoire_bp.route('/api/sauvegarder-resultat', methods=['POST'])
@login_required
@etudiant_required
def sauvegarder_resultat():
    """Sauvegarder un résultat de simulation"""
    data = request.get_json()

    session_id = data.get('session_id')
    session = SessionTP.query.get_or_404(session_id)

    # Vérifier que c'est bien l'étudiant de cette session
    if session.etudiant_id != current_user.etudiant_profile.id:
        return jsonify({'error': 'Non autorisé'}), 403

    mesure = MesureSimulation(
        session_id=session.id,
        parametres=json.dumps(data.get('parametres', {})),
        resultats=json.dumps(data.get('resultats', {})),
        type_mesure=data.get('type_mesure', 'manuelle'),
        timestamp=datetime.utcnow()
    )

    db.session.add(mesure)

    # Mettre à jour le nombre de mesures
    session.nb_mesures = (session.nb_mesures or 0) + 1
    db.session.commit()

    return jsonify({
        'success': True,
        'mesure_id': mesure.id,
        'nb_mesures': session.nb_mesures
    })


# ============================================================
# API - INTERACTION AVEC L'IA
# ============================================================
@laboratoire_bp.route('/api/poser-question-ia', methods=['POST'])
@login_required
@etudiant_required
def poser_question_ia():
    """Poser une question à l'assistant IA"""
    data = request.get_json()

    session_id = data.get('session_id')
    question = data.get('question')
    contexte = data.get('contexte', {})
    ia_nom = data.get('ia_nom', 'ETA')  # ETA, ALPHA, ou KAYT

    session = SessionTP.query.get_or_404(session_id)

    # Vérifier les permissions
    if session.etudiant_id != current_user.etudiant_profile.id:
        return jsonify({'error': 'Non autorisé'}), 403

    try:
        # Utiliser le vrai système d'IA
        assistant = IAFactory.creer_assistant(ia_nom)
        reponse_data = assistant.generer_reponse(question, contexte, session)

        # Enregistrer l'interaction
        assistant.enregistrer_interaction(session.id, question, reponse_data, contexte)

        return jsonify({
            'success': True,
            'reponse': reponse_data['reponse'],
            'ia_nom': ia_nom,
            'pertinence': reponse_data.get('pertinence_question', 3),
            'aide_apportee': reponse_data.get('aide_apportee', True)
        })
    except Exception as e:
        # Fallback sur l'ancienne méthode en cas d'erreur
        reponse = generer_reponse_ia_fallback(question, contexte, ia_nom, session.tp)

        # Sauvegarder l'interaction
        interaction = InteractionIA(
            session_id=session.id,
            question_etudiant=question,
            reponse_ia=reponse,
            contexte_simulation=json.dumps(contexte),
            timestamp=datetime.utcnow(),
            ia_nom=ia_nom
        )
        db.session.add(interaction)
        db.session.commit()

        return jsonify({
            'success': True,
            'reponse': reponse,
            'ia_nom': ia_nom
        })


# ============================================================
# TERMINER UNE SESSION
# ============================================================
@laboratoire_bp.route('/terminer-session/<int:session_id>', methods=['POST'])
@login_required
@etudiant_required
def terminer_session(session_id):
    """Terminer une session de TP"""
    session = SessionTP.query.get_or_404(session_id)

    # Vérifier les permissions
    if session.etudiant_id != current_user.etudiant_profile.id:
        flash('Cette session ne vous appartient pas', 'danger')
        return redirect(url_for('laboratoire.hub_etudiant'))

    session.date_fin = datetime.utcnow()
    session.statut = 'terminé'

    # Calculer la durée
    if session.date_debut:
        duree = (session.date_fin - session.date_debut).total_seconds() / 60
        session.duree_minutes = int(duree)

    # Évaluation automatique par l'IA
    try:
        assistant = IAFactory.creer_assistant(session.tp.ia_nom)
        evaluation = assistant.evaluer_session(session)

        session.note_ia = evaluation['note']
        session.commentaire_ia = evaluation['commentaire']
        session.criteres_evaluation = json.dumps(evaluation.get('criteres', {}))

        # Afficher les badges obtenus (si disponibles)
        badges_obtenus = evaluation.get('badges_obtenus', [])
        if badges_obtenus:
            flash(f'🏆 Félicitations ! Tu as obtenu {len(badges_obtenus)} nouveau(x) badge(s) : {", ".join(badges_obtenus)}', 'success')

        flash(f'✅ Session terminée ! Note automatique : {evaluation["note"]:.1f}/20', 'info')
    except Exception as e:
        print(f"Erreur évaluation IA : {e}")
        flash('Session terminée ! L\'évaluation automatique sera faite plus tard.', 'info')

    db.session.commit()

    return redirect(url_for('laboratoire.resultat_tp', session_id=session.id))


# ============================================================
# RÉSULTAT D'UNE SESSION
# ============================================================
@laboratoire_bp.route('/resultat/<int:session_id>')
@login_required
def resultat_tp(session_id):
    """Afficher les résultats d'une session de TP"""
    session = SessionTP.query.get_or_404(session_id)

    # Vérifier les permissions
    etudiant = current_user.etudiant_profile if current_user.role == 'ETUDIANT' else None
    enseignant = current_user.enseignant_profile if current_user.role == 'ENSEIGNANT' else None

    if current_user.role == 'ETUDIANT' and session.etudiant_id != etudiant.id:
        flash('Ce résultat ne vous appartient pas', 'danger')
        return redirect(url_for('laboratoire.hub_etudiant'))

    if current_user.role == 'ENSEIGNANT' and session.tp.enseignant_id != enseignant.id:
        flash('Ce TP ne vous appartient pas', 'danger')
        return redirect(url_for('laboratoire.hub_enseignant'))

    # Récupérer toutes les mesures
    mesures = MesureSimulation.query.filter_by(
        session_id=session.id
    ).order_by(MesureSimulation.timestamp.asc()).all()

    # Interactions IA
    interactions = InteractionIA.query.filter_by(
        session_id=session.id
    ).order_by(InteractionIA.timestamp.asc()).all()

    return render_template('laboratoire/resultat_tp.html',
                         session=session,
                         mesures=mesures,
                         interactions=interactions)


# ============================================================
# FONCTION HELPER - GÉNÉRATION DE RÉPONSE IA FALLBACK
# ============================================================
def generer_reponse_ia_fallback(question, contexte, ia_nom, tp):
    """Génère une réponse d'assistant IA (fallback simple)"""

    # Personnalités des IAs
    personalities = {
        'ETA': "Je suis ETA, votre assistant pédagogique en Génie Civil.",
        'ALPHA': "Je suis ALPHA, expert en Mathématiques, Informatique et Logistique.",
        'KAYT': "Je suis KAYT, spécialiste en Génie Électrique."
    }

    intro = personalities.get(ia_nom, "Je suis votre assistant IA.")

    # Analyse simple de la question
    question_lower = question.lower()

    if 'aide' in question_lower or 'comment' in question_lower:
        reponse = f"{intro} Pour ce TP '{tp.titre}', je vous suggère de :\n\n"
        reponse += "1. Vérifier vos paramètres d'entrée\n"
        reponse += "2. Observer les variations sur le graphique\n"
        reponse += "3. Comparer avec les objectifs du TP\n\n"
        reponse += "N'hésitez pas à ajuster les paramètres et à faire plusieurs essais !"

    elif 'résultat' in question_lower or 'correct' in question_lower:
        reponse = f"{intro} Vos résultats semblent cohérents. "
        reponse += "Continuez à explorer différentes configurations pour mieux comprendre le phénomène !"

    elif 'erreur' in question_lower or 'problème' in question_lower:
        reponse = f"{intro} Si vous rencontrez une erreur, vérifiez que :\n\n"
        reponse += "- Les valeurs entrées sont dans les plages autorisées\n"
        reponse += "- Les unités sont correctes\n"
        reponse += "- Vous avez bien suivi les consignes du TP"

    else:
        reponse = f"{intro} Excellente question ! "
        reponse += f"Pour mieux vous aider avec le TP '{tp.titre}', "
        reponse += "pouvez-vous me préciser sur quel aspect vous avez besoin d'aide ?"

    return reponse


# ============================================================
# SUPPRIMER UN TP (ENSEIGNANT)
# ============================================================
@laboratoire_bp.route('/supprimer-tp/<int:tp_id>', methods=['POST'])
@login_required
@enseignant_required
def supprimer_tp(tp_id):
    """Supprimer un TP"""
    tp = TP.query.get_or_404(tp_id)
    enseignant = current_user.enseignant_profile

    if tp.enseignant_id != enseignant.id:
        flash('Vous ne pouvez supprimer que vos propres TPs', 'danger')
        return redirect(url_for('laboratoire.hub_enseignant'))

    # Vérifier qu'il n'y a pas de sessions actives
    sessions_actives = SessionTP.query.filter_by(
        tp_id=tp.id,
        statut='en_cours'
    ).count()

    if sessions_actives > 0:
        flash('Impossible de supprimer ce TP : des sessions sont en cours', 'danger')
        return redirect(url_for('laboratoire.detail_tp', tp_id=tp.id))

    titre = tp.titre
    db.session.delete(tp)
    db.session.commit()

    flash(f'TP "{titre}" supprimé avec succès', 'success')
    return redirect(url_for('laboratoire.hub_enseignant'))
