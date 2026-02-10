from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user, logout_user
from functools import wraps
from config import Config
from datetime import datetime
import io
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from sqlalchemy import func, desc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from app.models import Examen


from app import db
from app.models import (
    Etudiant, UE, Note, InscriptionUE, User,
    Classe, Filiere, Absence, Document
)

bp = Blueprint('etudiant', __name__, url_prefix='/etudiant')


def etudiant_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'ETUDIANT':
            flash('Accès interdit : Cet espace est réservé aux étudiants.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        filiere_id = request.form.get('filiere_id')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        date_naiss = request.form.get('date_naissance')

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return redirect(url_for('etudiant.inscription'))

        if User.query.filter_by(username=username).first():
            flash("Cet identifiant est déjà utilisé.", "danger")
            return redirect(url_for('etudiant.inscription'))

        try:
            user = User(username=username, role='ETUDIANT', statut='actif')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            etudiant = Etudiant(
                user_id=user.id,
                nom=nom.upper() if nom else "",
                prenom=prenom.title() if prenom else "",
                filiere_id=filiere_id,
                statut_inscription="en_attente",
                date_inscription=datetime.now()
            )

            if date_naiss:
                etudiant.date_naissance = datetime.strptime(date_naiss, "%Y-%m-%d")

            db.session.add(etudiant)
            db.session.commit()

            flash("✅ Inscription réussie ! Connectez-vous pour suivre votre dossier.", "success")
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'inscription : {str(e)}", "danger")

    filieres = Filiere.query.filter_by(active=True).all()
    return render_template('etudiant/inscription.html', filieres=filieres)


@bp.route('/dashboard')
@etudiant_required
def dashboard():
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()

    if etudiant.statut_inscription != 'accepté':
        template = f'etudiant/dashboard_{etudiant.statut_inscription}.html'
        return render_template(template, etudiant=etudiant)

    inscriptions = etudiant.inscriptions_ue.all()
    total_credits_inscrits = sum(ins.ue.credits for ins in inscriptions if ins.ue)

    notes_data = db.session.query(
        func.avg(Note.note).label('moyenne'),
        func.count(Note.id).label('nb_notes')
    ).filter(Note.etudiant_id == etudiant.id, Note.note != None).first()

    moyenne_gen = round(notes_data.moyenne, 2) if notes_data.moyenne else None
    credits_valides = sum(n.ue_parent.credits for n in etudiant.notes if n.note and n.note >= 10)
    total_nj = etudiant.absences.filter_by(justifiee=False).count() if hasattr(etudiant, 'absences') else 0

    notes_recentes = etudiant.notes.order_by(Note.date_saisie.desc()).limit(5).all()
    documents = etudiant.user.documents.limit(3).all() if hasattr(etudiant.user, 'documents') else []

    return render_template('etudiant/dashboard_admis.html',
                           etudiant=etudiant,
                           inscriptions=inscriptions,
                           notes=notes_recentes,
                           total_credits=total_credits_inscrits,
                           credits_valides=credits_valides,
                           moyenne_generale=moyenne_gen,
                           total_non_justifiees=total_nj,
                           documents=documents)


@bp.route('/choisir-ues', methods=['GET', 'POST'])
@login_required
@etudiant_required
def choisir_ues():
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        ue_ids = request.form.getlist('ues')
        annee_actuelle = "2025-2026"

        try:
            InscriptionUE.query.filter_by(
                etudiant_id=etudiant.id,
                annee_academique=annee_actuelle
            ).delete()

            for uid in ue_ids:
                if uid:
                    nouvelle_ins = InscriptionUE(
                        etudiant_id=etudiant.id,
                        ue_id=int(uid),
                        annee_academique=annee_actuelle,
                        statut='validé'
                    )
                    db.session.add(nouvelle_ins)

            db.session.commit()
            flash("📚 Inscription mise à jour avec succès !", "success")
            return redirect(url_for('etudiant.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash("Erreur lors de l'enregistrement.", "danger")

    ues_disponibles = UE.query.filter_by(classe_id=etudiant.classe_id).all() if etudiant.classe_id else []
    inscrites = InscriptionUE.query.filter_by(etudiant_id=etudiant.id).all()
    ues_inscrites_ids = [i.ue_id for i in inscrites]

    return render_template('etudiant/choisir_ues.html',
                           ues_disponibles=ues_disponibles,
                           ues_inscrites_ids=ues_inscrites_ids,
                           etudiant=etudiant,
                           credits_max=60)


@bp.route('/telecharger-lettre')
@etudiant_required
def telecharger_lettre():
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()

    # Import du nouveau module de styles
    from app.utils.pdf_styles import (
        PolytechColors, draw_header, draw_footer, draw_decorative_border,
        draw_validation_stamp, draw_signature_block, draw_info_box, format_date
    )

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Cadre décoratif élégant
    draw_decorative_border(c, width, height)

    # En-tête professionnel
    y_pos = draw_header(c, width, height)

    # Date et référence
    date_jour = datetime.now().strftime('%d/%m/%Y')
    c.setFont("Helvetica", 10)
    c.setFillColor(PolytechColors.GRAY_DARK)
    c.drawRightString(width - 3*cm, y_pos, f"Lomé, le {date_jour}")
    c.drawRightString(width - 3*cm, y_pos - 0.5*cm, f"Réf: PTH/DES/{etudiant.id:04d}/2026")

    y_pos -= 2*cm

    # Destinataire dans un cadre élégant
    c.setFillColor(colors.HexColor('#f0f9ff'))
    c.roundRect(3*cm, y_pos - 2*cm, width - 6*cm, 2*cm, 0.3*cm, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PolytechColors.BLUE_DARK)
    c.drawString(3.5*cm, y_pos - 0.8*cm, f"À l'attention de M./Mme {etudiant.nom_complet}")
    c.setFont("Helvetica", 10)
    c.setFillColor(PolytechColors.GRAY_DARK)
    c.drawString(3.5*cm, y_pos - 1.3*cm, f"Dossier N°: {etudiant.id:04d}")
    c.drawString(3.5*cm, y_pos - 1.7*cm, "Objet: Notification de décision d'admission")

    y_pos -= 3.5*cm

    # Déterminer le contenu selon le statut
    nom_classe = etudiant.classe.nom_classe if etudiant.classe else "la formation demandée"

    if etudiant.statut_inscription == 'accepté':
        titre_doc = "NOTIFICATION D'ADMISSION"
        couleur_titre = PolytechColors.SUCCESS
        status_stamp = "ADMIS(E)"

        lignes = [
            ("Madame, Monsieur,", False),
            ("", False),
            ("Nous avons le plaisir de vous informer que votre candidature à l'École Polytechnique", False),
            ("a fait l'objet d'un avis FAVORABLE de la part de notre Commission d'Admission.", False),
            ("", False),
            (f"🎓 Vous êtes officiellement admis(e) en {nom_classe.upper()}", True),
            ("", False),
            ("Cette admission fait suite à l'examen attentif de votre dossier académique et témoigne", False),
            ("de la qualité de votre parcours et de votre potentiel.", False),
            ("", False),
            ("📋 Prochaines étapes:", True),
            ("", False),
            ("1. Confirmer votre inscription avant le 15/03/2026", False),
            ("2. Compléter votre dossier administratif", False),
            ("3. Procéder au règlement des frais de scolarité", False),
            ("", False),
            ("Nous vous félicitons chaleureusement pour cette réussite et avons hâte de vous", False),
            ("accueillir parmi nos étudiants pour cette nouvelle année académique.", False),
        ]

    elif etudiant.statut_inscription == 'refusé':
        titre_doc = "NOTIFICATION DE DÉCISION"
        couleur_titre = PolytechColors.DANGER
        status_stamp = "REFUSÉ"

        lignes = [
            ("Madame, Monsieur,", False),
            ("", False),
            ("Nous accusons réception de votre candidature à l'École Polytechnique et vous", False),
            ("remercions de l'intérêt que vous portez à notre établissement.", False),
            ("", False),
            ("Après examen approfondi des dossiers par notre Commission d'Admission,", False),
            ("nous sommes au regret de vous informer que nous ne sommes pas en mesure", False),
            ("de donner une suite favorable à votre candidature pour l'année 2025-2026.", False),
            ("", False),
            ("Cette décision a été prise dans un contexte de forte sélectivité, le nombre", False),
            ("de places étant limité par rapport au volume de candidatures reçues.", False),
            ("", False),
            ("Nous tenons à souligner que ce refus ne remet nullement en cause la qualité", False),
            ("de votre parcours académique.", False),
            ("", False),
            ("Nous vous souhaitons pleine réussite dans la poursuite de vos études et de", False),
            ("vos projets professionnels.", False),
        ]

    else:  # en_attente
        titre_doc = "ACCUSÉ DE RÉCEPTION"
        couleur_titre = PolytechColors.INFO
        status_stamp = "EN COURS"

        filiere_nom = etudiant.filiere_objet.nom_filiere if etudiant.filiere_objet else 'Non spécifiée'

        lignes = [
            ("Madame, Monsieur,", False),
            ("", False),
            ("Nous accusons bonne réception de votre dossier de candidature à l'École", False),
            ("Polytechnique et vous en remercions.", False),
            ("", False),
            (f"📁 Filière demandée: {filiere_nom}", True),
            ("", False),
            ("Votre dossier est actuellement en cours d'examen par notre Commission", False),
            ("d'Admission. Chaque candidature fait l'objet d'une étude approfondie afin", False),
            ("de garantir l'équité et la transparence du processus de sélection.", False),
            ("", False),
            ("⏰ Calendrier indicatif:", True),
            ("", False),
            ("• Délibération de la Commission: jusqu'au 28/02/2026", False),
            ("• Notification des décisions: avant le 05/03/2026", False),
            ("• Confirmation d'inscription: avant le 15/03/2026", False),
            ("", False),
            ("Vous recevrez une notification par email dès qu'une décision sera prise", False),
            ("concernant votre candidature.", False),
        ]

    # Titre du document avec fond coloré
    c.setFillColor(couleur_titre)
    c.setFillAlpha(0.1)
    c.roundRect(2*cm, y_pos - 1*cm, width - 4*cm, 1.2*cm, 0.3*cm, stroke=0, fill=1)
    c.setFillAlpha(1)

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(couleur_titre)
    c.drawCentredString(width / 2, y_pos - 0.7*cm, titre_doc)

    y_pos -= 2.5*cm

    # Corps du texte avec mise en forme améliorée
    c.setFont("Helvetica", 11)
    line_height = 0.55*cm

    for ligne, is_important in lignes:
        if is_important:
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(PolytechColors.BLUE_PRIMARY)
        else:
            c.setFont("Helvetica", 11)
            c.setFillColor(PolytechColors.GRAY_DARK)

        if ligne.strip():  # Si la ligne n'est pas vide
            c.drawString(3*cm, y_pos, ligne)

        y_pos -= line_height

    # Bloc de signature élégant
    y_sig = 7*cm
    draw_signature_block(c, width - 3*cm, y_sig)

    # Tampon de validation
    draw_validation_stamp(c, width - 4.5*cm, y_sig - 1.2*cm, status_stamp, couleur_titre)

    # Pied de page professionnel
    draw_footer(c, width, height, page_num=1, total_pages=1, doc_type=titre_doc)

    c.showPage()
    c.save()
    buffer.seek(0)

    # Nom de fichier sécurisé
    safe_name = f"Notification_{etudiant.nom.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=safe_name,
        mimetype='application/pdf'
    )


@bp.route('/mes-notes')
@etudiant_required
def mes_notes():
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()
    notes = etudiant.notes.all()

    # Calculs statistiques
    notes_valides = [n.note for n in notes if n.note is not None]
    moyenne_generale = round(sum(notes_valides) / len(notes_valides), 2) if notes_valides else 0

    # Stats par UE pour histogrammes
    ues_stats = {}
    for note in notes:
        if note.note is not None:
            ue_nom = note.ue.intitule
            if ue_nom not in ues_stats:
                ues_stats[ue_nom] = {
                    'note': note.note,
                    'coef': note.ue.coefficient,
                    'credits': note.ue.credits,
                    'code': note.ue.code_ue
                }

    # Répartition des notes
    distribution = {'<10': 0, '10-12': 0, '12-14': 0, '14-16': 0, '>=16': 0}
    for n in notes_valides:
        if n < 10: distribution['<10'] += 1
        elif n < 12: distribution['10-12'] += 1
        elif n < 14: distribution['12-14'] += 1
        elif n < 16: distribution['14-16'] += 1
        else: distribution['>=16'] += 1

    # Absences
    absences = Absence.query.filter_by(etudiant_id=etudiant.id).count()
    absences_justifiees = Absence.query.filter_by(etudiant_id=etudiant.id, justifiee=True).count()

    return render_template('etudiant/mes_notes.html',
                         notes=notes,
                         etudiant=etudiant,
                         moyenne_generale=moyenne_generale,
                         ues_stats=ues_stats,
                         distribution=distribution,
                         absences=absences,
                         absences_justifiees=absences_justifiees)


@bp.route('/telecharger-bulletin')
@etudiant_required
def telecharger_bulletin():
    """Génère et télécharge le bulletin de notes en PDF avec histogrammes"""
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()

    from app.utils.pdf_styles import PolytechColors, draw_header, draw_footer, get_table_style
    from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.graphics.shapes import Drawing, Rect, String as DrawString
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics import renderPDF

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # En-tête
    story.append(Paragraph(
        f'<para align="center" fontSize="24" fontName="Helvetica-Bold" textColor="{PolytechColors.BLUE_DARK.hexval()}">BULLETIN DE NOTES</para>',
        ParagraphStyle('temp', fontSize=24, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 0.5*cm))

    # Infos étudiant
    story.append(Paragraph(
        f'<para align="center" fontSize="14"><b>{etudiant.nom_complet}</b><br/>{etudiant.classe.nom_classe if etudiant.classe else "Sans classe"}</para>',
        ParagraphStyle('temp', fontSize=14, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 1*cm))

    # Calcul moyenne
    notes = etudiant.notes.all()
    notes_valides = [n.note for n in notes if n.note is not None]
    moyenne = round(sum(notes_valides) / len(notes_valides), 2) if notes_valides else 0

    # Tableau résumé
    resume_data = [
        ['INDICATEUR', 'VALEUR'],
        ['Moyenne Générale', f'{moyenne}/20'],
        ['UE Évaluées', str(len([n for n in notes if n.note is not None]))],
        ['UE Validées', str(len([n for n in notes if n.note and n.note >= 10]))],
    ]
    resume_table = Table(resume_data, colWidths=[10*cm, 5*cm])
    resume_table.setStyle(get_table_style())
    story.append(resume_table)
    story.append(Spacer(1, 1*cm))

    # Histogramme
    drawing = Drawing(400, 200)
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 125
    chart.width = 300

    # Données pour l'histogramme
    ues_data = [(n.ue.code_ue, n.note) for n in notes if n.note is not None]
    if ues_data:
        chart.data = [[n[1] for n in ues_data]]
        chart.categoryAxis.categoryNames = [n[0] for n in ues_data]
        chart.bars[0].fillColor = PolytechColors.BLUE_PRIMARY

    drawing.add(chart)
    story.append(drawing)
    story.append(Spacer(1, 1*cm))

    # Tableau détaillé
    table_data = [['Code UE', 'Intitulé', 'Crédits', 'Coef', 'Note', 'Statut']]
    for note in notes:
        if note.note is not None:
            statut = '✓ Validé' if note.note >= 10 else '✗ Échec'
            table_data.append([
                note.ue.code_ue,
                note.ue.intitule[:30],
                str(note.ue.credits),
                str(note.ue.coefficient),
                f'{note.note}/20',
                statut
            ])

    if len(table_data) > 1:
        detail_table = Table(table_data)
        detail_table.setStyle(get_table_style())
        story.append(detail_table)

    doc.build(story)
    buffer.seek(0)

    filename = f"Bulletin_{etudiant.nom}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')


@bp.route('/telecharger-observations')
@etudiant_required
def telecharger_observations():
    """Génère un rapport d'observations avec analyse IA, statistiques et recommandations"""
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()

    from app.utils.pdf_styles import PolytechColors, get_custom_styles, get_table_style
    from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = get_custom_styles()

    # Titre
    story.append(Paragraph("RAPPORT D'OBSERVATIONS & ANALYSE", styles['DocumentTitle']))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"{etudiant.nom_complet} - {etudiant.classe.nom_classe if etudiant.classe else 'N/A'}", styles['Subtitle']))
    story.append(Spacer(1, 1*cm))

    # Calculs
    notes = etudiant.notes.all()
    notes_valides = [n.note for n in notes if n.note is not None]
    moyenne = round(sum(notes_valides) / len(notes_valides), 2) if notes_valides else 0
    absences = Absence.query.filter_by(etudiant_id=etudiant.id).count()
    absences_just = Absence.query.filter_by(etudiant_id=etudiant.id, justifiee=True).count()

    # Section 1: Synthèse
    story.append(Paragraph("1. SYNTHÈSE ACADÉMIQUE", styles['SectionHeading']))
    story.append(Spacer(1, 0.5*cm))

    synthese_data = [
        ['INDICATEUR', 'VALEUR', 'APPRÉCIATION'],
        ['Moyenne Générale', f'{moyenne}/20', '✓ Satisfaisant' if moyenne >= 10 else '⚠ Insuffisant'],
        ['UE Validées', f'{len([n for n in notes if n.note and n.note >= 10])}/{len(notes_valides)}', ''],
        ['Absences Totales', str(absences), f'{absences_just} justifiées'],
        ['Taux de Présence', f'{100 - (absences * 2) if absences < 50 else 0}%', ''],
    ]
    synthese_table = Table(synthese_data, colWidths=[6*cm, 4*cm, 5*cm])
    synthese_table.setStyle(get_table_style())
    story.append(synthese_table)
    story.append(Spacer(1, 1*cm))

    # Section 2: Analyse IA
    story.append(Paragraph("2. ANALYSE AUTOMATISÉE (IA)", styles['SectionHeading']))
    story.append(Spacer(1, 0.5*cm))

    # Génération analyse IA
    if moyenne >= 16:
        analyse = f"<b>Profil: EXCELLENCE</b><br/>L'étudiant {etudiant.nom_complet} démontre une maîtrise exceptionnelle avec une moyenne de {moyenne}/20. Performances constantes et homogènes. Recommandation: Poursuivre sur cette lancée et viser l'excellence maximale."
    elif moyenne >= 14:
        analyse = f"<b>Profil: TRÈS BIEN</b><br/>Solides performances académiques ({moyenne}/20). L'étudiant présente un bon niveau de compréhension. Quelques marges de progression identifiées. Recommandation: Consolider les acquis et viser 16+."
    elif moyenne >= 12:
        analyse = f"<b>Profil: BIEN</b><br/>Résultats satisfaisants ({moyenne}/20) avec des performances correctes. Potentiel d'amélioration détecté. Recommandation: Renforcer le travail personnel pour atteindre 14+."
    elif moyenne >= 10:
        analyse = f"<b>Profil: PASSABLE</b><br/>Niveau juste acceptable ({moyenne}/20). Fragilités détectées dans certaines matières. Recommandation: Soutien pédagogique recommandé, travail régulier indispensable."
    else:
        analyse = f"<b>Profil: INSUFFISANT</b><br/>Moyenne de {moyenne}/20 en dessous du seuil. Difficultés majeures identifiées. Recommandation URGENTE: Accompagnement personnalisé, révision des bases, entretien pédagogique."

    story.append(Paragraph(analyse, styles['BodyText']))
    story.append(Spacer(1, 1*cm))

    # Section 3: Observations par UE
    story.append(Paragraph("3. OBSERVATIONS PAR MATIÈRE", styles['SectionHeading']))
    story.append(Spacer(1, 0.5*cm))

    ue_detail_data = [['UE', 'Note', 'Observation IA']]
    for note in notes:
        if note.note is not None:
            if note.note >= 16:
                obs = "Excellente maîtrise"
            elif note.note >= 14:
                obs = "Très bonne compréhension"
            elif note.note >= 12:
                obs = "Bonne acquisition"
            elif note.note >= 10:
                obs = "Acquis minimal"
            else:
                obs = "Lacunes à combler"

            ue_detail_data.append([note.ue.code_ue, f'{note.note}/20', obs])

    if len(ue_detail_data) > 1:
        ue_table = Table(ue_detail_data, colWidths=[4*cm, 3*cm, 8*cm])
        ue_table.setStyle(get_table_style())
        story.append(ue_table)

    story.append(Spacer(1, 1*cm))

    # Section 4: Recommandations
    story.append(Paragraph("4. RECOMMANDATIONS PERSONNALISÉES", styles['SectionHeading']))
    story.append(Spacer(1, 0.5*cm))

    reco_text = "<b>Actions prioritaires:</b><br/>"
    if moyenne < 10:
        reco_text += "• Rendez-vous obligatoire avec le responsable pédagogique<br/>• Plan de remise à niveau à mettre en place<br/>• Suivi hebdomadaire recommandé"
    elif moyenne < 12:
        reco_text += "• Renforcer le travail personnel<br/>• Participer aux séances de tutorat<br/>• Revoir les bases des matières faibles"
    elif moyenne < 14:
        reco_text += "• Maintenir l'effort actuel<br/>• Viser l'excellence dans les matières fortes<br/>• Consolider les matières moyennes"
    else:
        reco_text += "• Continuer sur cette excellente voie<br/>• Approfondir les connaissances<br/>• Participer aux projets avancés"

    story.append(Paragraph(reco_text, styles['BodyText']))
    story.append(Spacer(1, 0.5*cm))

    # Signature
    story.append(Paragraph(
        f'<para align="right" fontSize="10" textColor="gray"><i>Rapport généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")}<br/>Système d\'analyse académique Infinity AI</i></para>',
        styles['Footer']
    ))

    doc.build(story)
    buffer.seek(0)

    filename = f"Observations_{etudiant.nom}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')


@bp.route('/mes-ues')
@etudiant_required
def mes_ues():
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()

    inscriptions = InscriptionUE.query.filter_by(etudiant_id=etudiant.id).all()

    ues_avec_notes = []
    total_valides = 0
    somme_notes = 0
    nb_notes = 0

    for ins in inscriptions:
        note_obj = Note.query.filter_by(etudiant_id=etudiant.id, ue_id=ins.ue_id).first()
        val_note = note_obj.note if note_obj else None

        is_validee = val_note is not None and val_note >= 10
        if is_validee and ins.ue:
            total_valides += ins.ue.credits

        if val_note is not None:
            somme_notes += val_note
            nb_notes += 1

        ues_avec_notes.append({
            'ue': ins.ue,
            'note': val_note,
            'validee': is_validee
        })

    moyenne = round(somme_notes / nb_notes, 2) if nb_notes > 0 else None

    return render_template('etudiant/mes_ues.html',
                           ues_avec_notes=ues_avec_notes,
                           total_credits_valides=total_valides,
                           moyenne_actuelle=moyenne)


@bp.route('/profil', methods=['GET', 'POST'])
@etudiant_required
def profil():
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        etudiant.telephone = request.form.get('telephone')
        etudiant.situation_matrimoniale = request.form.get('situation_matrimoniale')

        new_password = request.form.get('new_password')
        if new_password:
            current_user.set_password(new_password)

        db.session.commit()
        flash("✅ Profil mis à jour avec succès.", "success")
        return redirect(url_for('etudiant.profil'))

    return render_template('etudiant/profil.html', etudiant=etudiant)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('auth.login'))



@bp.route('/ressources-pedagogiques')
@etudiant_required
def ressources_pedagogiques():
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()

    if etudiant.classe:
        documents = Document.query.filter_by(classe_id=etudiant.classe_id).order_by(Document.date_creation.desc()).all()
    else:
        documents = []

    return render_template('etudiant/ressources.html', documents=documents)


@bp.route('/mes-documents')
@etudiant_required
def mes_documents():
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()

    ressources = []
    if etudiant.classe:
        ressources = Document.query.filter_by(classe_id=etudiant.classe_id).order_by(Document.date_creation.desc()).all()

    docs_admin = []

    return render_template('etudiant/documents.html', ressources=ressources, docs_admin=docs_admin)


@bp.route('/mes-absences')
@etudiant_required
def mes_absences():
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()
    absences = etudiant.absences.order_by(Absence.date_absence.desc()).all()

    total_absences = len(absences)
    total_justifiees = sum(1 for a in absences if a.justifiee)
    total_non_justifiees = sum(1 for a in absences if not a.justifiee)

    # Répartition par UE
    absences_par_ue = {}
    for absence in absences:
        if absence.ue:
            code = absence.ue.code_ue
            if code not in absences_par_ue:
                absences_par_ue[code] = {
                    'ue': absence.ue,
                    'total': 0,
                    'justifiees': 0,
                    'non_justifiees': 0
                }
            absences_par_ue[code]['total'] += 1
            if absence.justifiee:
                absences_par_ue[code]['justifiees'] += 1
            else:
                absences_par_ue[code]['non_justifiees'] += 1

    return render_template('etudiant/mes_absences.html',
                         absences=absences,
                         total_absences=total_absences,
                         total_justifiees=total_justifiees,
                         total_non_justifiees=total_non_justifiees,
                         absences_par_ue=absences_par_ue)




@bp.route('/ma-convocation')
@login_required  # (Supposons que tu as un wrapper etudiant_required)
def telecharger_convocation():
    if not current_user.is_etudiant:
        return redirect(url_for('auth.index'))

    etudiant = current_user.etudiant_profile
    if not etudiant or not etudiant.classe:
        flash("Vous n'êtes inscrit dans aucune classe.", "warning")
        return redirect(url_for('etudiant.dashboard'))

    # Récupérer les examens de SA classe
    examens = Examen.query.filter_by(classe_id=etudiant.classe_id) \
        .order_by(Examen.date_examen).all()

    if not examens:
        flash("Aucun examen programmé pour votre classe.", "info")
        return redirect(url_for('etudiant.dashboard'))

    # --- GÉNÉRATION PDF ---
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # 1. En-tête Officiel
    c.setLineWidth(2)
    c.rect(20, 20, width - 40, height - 40)  # Cadre global

    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 60, "CONVOCATION AUX EXAMENS")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 80, f"Session : {datetime.now().year}")

    # 2. Identité Étudiant (Cadre)
    c.rect(40, height - 200, width - 80, 100)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 130, f"Nom & Prénom : {etudiant.nom.upper()} {etudiant.prenom}")
    c.drawString(50, height - 155, f"Matricule : {etudiant.matricule or 'En cours'}")
    c.drawString(50, height - 180, f"Classe : {etudiant.classe.nom_classe}")

    # 3. Tableau des Examens
    y = height - 250
    c.setFont("Helvetica-Bold", 12)
    # Titres colonnes
    c.drawString(50, y, "Date")
    c.drawString(150, y, "Heure")
    c.drawString(250, y, "Matière (UE)")
    c.drawString(450, y, "Salle")
    c.line(40, y - 5, width - 40, y - 5)

    y -= 30
    c.setFont("Helvetica", 11)

    for exam in examens:
        date_fmt = exam.date_examen.strftime('%d/%m/%Y')
        heure_fmt = f"{exam.heure_debut.strftime('%H:%M')} - {exam.heure_fin.strftime('%H:%M')}"

        c.drawString(50, y, date_fmt)
        c.drawString(150, y, heure_fmt)
        c.drawString(250, y, exam.ue.intitule[:25])  # On coupe si trop long
        c.drawString(450, y, exam.salle)

        y -= 25
        if y < 100:  # Nouvelle page si plus de place
            c.showPage()
            y = height - 50

    # 4. Consignes (Footer)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 80, "IMPORTANT :")
    c.drawString(50, 65, "- La présentation de cette convocation et de la carte d'étudiant est obligatoire.")
    c.drawString(50, 50, "- Tout retard supérieur à 15 minutes interdira l'accès à la salle.")
    c.drawString(50, 35, "- Les téléphones portables sont strictement interdits.")

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"Convocation_{etudiant.matricule}.pdf")


# Ajoute Seance dans tes imports
from app.models import Seance
from flask import jsonify


# 1. La page HTML qui contient le calendrier
@bp.route('/emploi-du-temps')
@login_required
def emploi_du_temps():
    if not current_user.is_etudiant:
        return redirect(url_for('auth.index'))
    return render_template('etudiant/calendrier.html')


# 2. L'API JSON (C'est ici que le JavaScript va chercher les infos)
@bp.route('/api/evenements')
@login_required
def api_evenements():
    etudiant = current_user.etudiant_profile
    if not etudiant or not etudiant.classe:
        return jsonify([])  # Liste vide si pas de classe

    # On récupère les cours de sa classe
    seances = Seance.query.filter_by(classe_id=etudiant.classe_id).all()

    # On transforme les données en format compatible FullCalendar
    events = []
    for s in seances:
        events.append({
            'title': f"{s.titre} ({s.salle})",
            'start': s.start.isoformat(),  # Format: "2026-02-12T08:00:00"
            'end': s.end.isoformat(),
            'backgroundColor': s.couleur,
            'borderColor': s.couleur
        })

    return jsonify(events)


# Dans app/routes/etudiant.py
from app.models import Livre

@bp.route('/bibliotheque-ecole')
@login_required
def bibliotheque_ecole():
    # On récupère tous les livres
    livres = Livre.query.order_by(Livre.titre).all()
    return render_template('etudiant/bibliotheque.html', livres=livres)