import os
from datetime import datetime
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF


def get_output_path(filename):
    """Crée le chemin complet de sauvegarde"""
    # On récupère le dossier configuré dans Config (config.py)
    folder = current_app.config.get('DOCUMENTS_FOLDER', 'documents')

    # Si le chemin est relatif, on le rend absolu
    if not os.path.isabs(folder):
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        folder = os.path.join(base_dir, folder)

    if not os.path.exists(folder):
        os.makedirs(folder)

    return os.path.join(folder, filename)


def apply_stamps_to_pdf(c, page_width, page_height, stamps_config=None):
    """
    Applique des cachets/sceaux officiels sur un canvas PDF ReportLab.

    Args:
        c: ReportLab Canvas
        page_width, page_height: dimensions de la page
        stamps_config: liste de dict {sceau_id, count, position, size} ou None pour auto
    """
    try:
        from app.models import Sceau, ConfigurationEcole

        # Récupérer la taille configurée par le directeur
        config = ConfigurationEcole.query.first()
        default_stamp_cm = 5.0  # Taille par défaut agrandie (anciennement 2.5)
        if config and config.taille_cachet_pdf:
            default_stamp_cm = config.taille_cachet_pdf

        if stamps_config:
            # Mode sélection manuelle
            for stamp_info in stamps_config:
                sceau = Sceau.query.get(stamp_info.get('sceau_id'))
                if not sceau or not sceau.image_path:
                    continue
                img_path = os.path.join(current_app.root_path, 'static', sceau.image_path)
                if not os.path.exists(img_path):
                    continue
                count = min(int(stamp_info.get('count', 1)), 3)
                # Taille personnalisée ou taille config directeur
                custom_size_cm = float(stamp_info.get('size', default_stamp_cm))
                stamp_size = custom_size_cm * cm
                # Positions multiples
                positions = [
                    (page_width - stamp_size - 2 * cm, 2 * cm),     # bas-droite
                    (2 * cm, 2 * cm),                                 # bas-gauche
                    (page_width / 2 - stamp_size / 2, 2 * cm),      # bas-centre
                ]
                for i in range(count):
                    if i < len(positions):
                        px, py = positions[i]
                        c.drawImage(img_path, px, py, width=stamp_size, height=stamp_size,
                                   preserveAspectRatio=True, mask='auto')
        else:
            # Mode automatique : placer le cachet de l'école s'il existe
            if config and config.cachet_path:
                img_path = os.path.join(current_app.root_path, 'static', config.cachet_path)
                if os.path.exists(img_path):
                    stamp_size = default_stamp_cm * cm
                    c.drawImage(img_path, page_width - stamp_size - 2 * cm, 2 * cm,
                               width=stamp_size, height=stamp_size,
                               preserveAspectRatio=True, mask='auto')
    except Exception:
        pass  # Ne pas crasher le PDF si le cachet ne fonctionne pas


# =========================================================================
# 1. ATTESTATION DE SCOLARITÉ
# =========================================================================
def generer_attestation_scolarite(etudiant):
    filename = f"attestation_{etudiant.id}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
    filepath = get_output_path(filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # En-tête
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 3 * cm, "ÉCOLE POLYTECHNIQUE")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 4 * cm, "Direction des Études")

    # Titre
    c.setLineWidth(2)
    c.line(4 * cm, height - 6 * cm, width - 4 * cm, height - 6 * cm)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 7 * cm, "ATTESTATION D'INSCRIPTION")

    # Corps
    text_y = height - 10 * cm
    c.setFont("Helvetica", 12)

    # Gestion sécurisée des données manquantes
    filiere_nom = etudiant.filiere.nom_filiere if etudiant.filiere else "Non définie"
    classe_nom = etudiant.classe.nom_classe if etudiant.classe else "Non affecté"
    matricule = etudiant.get_matricule() if hasattr(etudiant, 'get_matricule') else f"ETU-{etudiant.id}"
    annee = current_app.config.get('ANNEE_ACADEMIQUE_ACTUELLE', '2025-2026')

    content = [
        f"Je soussigné, Directeur de l'École Polytechnique,",
        f"Certifie que l'étudiant(e) : {etudiant.nom} {etudiant.prenom}",
        f"Né(e) le : {etudiant.date_naissance.strftime('%d/%m/%Y') if etudiant.date_naissance else 'N/A'}",
        f"Matricule : {matricule}",
        f"Est régulièrement inscrit(e) pour l'année académique {annee}",
        f"Filière : {filiere_nom}",
        f"Niveau : {classe_nom}"
    ]

    for line in content:
        c.drawString(3 * cm, text_y, line)
        text_y -= 1.5 * cm

    # Pied de page
    c.drawString(12 * cm, text_y - 2 * cm, f"Fait à Lomé, le {datetime.now().strftime('%d/%m/%Y')}")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(12 * cm, text_y - 3 * cm, "Le Directeur Académique")

    # Cachet officiel
    apply_stamps_to_pdf(c, width, height)

    c.save()
    return filename


# =========================================================================
# 2. RELEVÉ DE NOTES (Tableau)
# =========================================================================
def generer_releve_notes(etudiant):
    filename = f"releve_{etudiant.id}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
    filepath = get_output_path(filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Titre
    elements.append(Paragraph("RELEVÉ DE NOTES", styles['Title']))
    elements.append(Paragraph(f"Étudiant: {etudiant.nom} {etudiant.prenom}", styles['Heading2']))
    matricule = etudiant.get_matricule() if hasattr(etudiant, 'get_matricule') else f"ETU-{etudiant.id}"
    elements.append(Paragraph(f"Matricule: {matricule}", styles['Normal']))
    elements.append(Spacer(1, 1 * cm))

    # Données du tableau
    data = [['Code UE', 'Intitulé', 'Crédits', 'Note /20', 'Résultat']]

    somme_notes = 0
    total_coef = 0
    credits_valides = 0

    # On vérifie si l'étudiant a des notes
    if hasattr(etudiant, 'notes'):
        for note in etudiant.notes:
            if note.note is not None:
                statut = "Validé" if note.note >= 10 else "Ajourné"
                if note.note >= 10: credits_valides += note.ue.credits

                somme_notes += (note.note * note.ue.coefficient)
                total_coef += note.ue.coefficient

                data.append([
                    note.ue.code_ue,
                    note.ue.intitule[:30],
                    str(note.ue.credits),
                    str(note.note),
                    statut
                ])

    # Création du tableau ReportLab
    table = Table(data, colWidths=[3 * cm, 8 * cm, 2 * cm, 3 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 1 * cm))

    # Moyenne
    if total_coef > 0:
        moyenne = round(somme_notes / total_coef, 2)
        elements.append(Paragraph(f"<b>Moyenne Générale : {moyenne} / 20</b>", styles['Heading3']))
        elements.append(Paragraph(f"Crédits validés : {credits_valides} / 60", styles['Normal']))

    doc.build(elements)
    return filename


# =========================================================================
# 3. BULLETIN AVEC GRAPHIQUE (Alias)
# =========================================================================
def generer_bulletin_avec_graphique(etudiant):
    return generer_releve_notes(etudiant)


# =========================================================================
# 4. CARTE D'ÉTUDIANT (QR Code)
# =========================================================================
def generer_carte_etudiant(etudiant):
    filename = f"carte_{etudiant.id}.pdf"
    filepath = get_output_path(filename)

    # Format carte de crédit
    width = 8.56 * cm
    height = 5.4 * cm

    c = canvas.Canvas(filepath, pagesize=(width, height))

    # Design
    c.setFillColorRGB(0.1, 0.2, 0.5)  # Bleu nuit
    c.rect(0, 0, width, height, fill=1)

    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width, 1.5 * cm, fill=1)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * cm, height - 1 * cm, "ÉCOLE POLYTECHNIQUE")

    c.setFont("Helvetica", 6)
    c.drawString(0.5 * cm, height - 1.4 * cm, "CARTE D'ÉTUDIANT 2025-2026")

    # Infos
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2.5 * cm, 1 * cm, f"{etudiant.nom}")
    c.setFont("Helvetica", 8)
    c.drawString(2.5 * cm, 0.6 * cm, f"{etudiant.prenom}")

    # Cadre Photo
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(0.3 * cm, 0.3 * cm, 2 * cm, 2.5 * cm)
    c.setFont("Helvetica", 6)
    c.drawCentredString(1.3 * cm, 1.5 * cm, "PHOTO")

    # QR Code
    matricule = etudiant.get_matricule() if hasattr(etudiant, 'get_matricule') else f"ETU-{etudiant.id}"
    qr_code = qr.QrCodeWidget(matricule)
    qr_code.barWidth = 1.5
    qr_code.barHeight = 1.5
    qr_code.qrVersion = 1

    d = Drawing(40, 40)
    d.add(qr_code)
    renderPDF.draw(d, c, width - 2.5 * cm, 0.5 * cm)

    c.save()
    return filename