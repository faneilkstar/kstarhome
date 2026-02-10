"""
Module de styles et d'utilitaires pour la génération de PDF élégants
Fournit des styles cohérents et professionnels pour tous les documents PDF
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime


# ============================================================
# COULEURS POLYTECH
# ============================================================
class PolytechColors:
    """Palette de couleurs institutionnelles"""
    BLUE_DARK = colors.HexColor("#1e3a8a")      # Bleu foncé principal
    BLUE_PRIMARY = colors.HexColor("#2563eb")    # Bleu primaire
    BLUE_LIGHT = colors.HexColor("#3b82f6")      # Bleu clair

    GOLD = colors.HexColor("#d97706")            # Or/Ambre
    GOLD_LIGHT = colors.HexColor("#f59e0b")      # Or clair

    SUCCESS = colors.HexColor("#10b981")         # Vert succès
    WARNING = colors.HexColor("#f59e0b")         # Orange warning
    DANGER = colors.HexColor("#ef4444")          # Rouge danger
    INFO = colors.HexColor("#3b82f6")            # Bleu info

    GRAY_DARK = colors.HexColor("#374151")       # Gris foncé
    GRAY = colors.HexColor("#6b7280")            # Gris moyen
    GRAY_LIGHT = colors.HexColor("#d1d5db")      # Gris clair

    WHITE = colors.white
    BLACK = colors.black


# ============================================================
# STYLES DE PARAGRAPHE
# ============================================================
def get_custom_styles():
    """Retourne un dictionnaire de styles personnalisés pour les PDF"""
    styles = getSampleStyleSheet()

    # Titre principal du document
    styles.add(ParagraphStyle(
        name='DocumentTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=PolytechColors.BLUE_DARK,
        spaceAfter=20,
        spaceBefore=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=28
    ))

    # Sous-titre
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=PolytechColors.BLUE_PRIMARY,
        spaceAfter=12,
        spaceBefore=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=20
    ))

    # Section heading
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=PolytechColors.BLUE_DARK,
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderPadding=(0, 0, 5, 0),
        borderWidth=2,
        borderColor=PolytechColors.GOLD,
        leading=18
    ))

    # Corps de texte élégant
    styles.add(ParagraphStyle(
        name='BodyText',
        parent=styles['Normal'],
        fontSize=11,
        textColor=PolytechColors.GRAY_DARK,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=16,
        firstLineIndent=0
    ))

    # Texte important/mis en valeur
    styles.add(ParagraphStyle(
        name='Highlight',
        parent=styles['Normal'],
        fontSize=12,
        textColor=PolytechColors.BLUE_PRIMARY,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=16
    ))

    # Pied de page
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=PolytechColors.GRAY,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=10
    ))

    # Citation/Note
    styles.add(ParagraphStyle(
        name='Note',
        parent=styles['Normal'],
        fontSize=10,
        textColor=PolytechColors.GRAY,
        spaceAfter=8,
        leftIndent=20,
        rightIndent=20,
        alignment=TA_JUSTIFY,
        fontName='Helvetica-Oblique',
        leading=14
    ))

    return styles


# ============================================================
# EN-TÊTE PROFESSIONNELLE
# ============================================================
def draw_header(canvas, width, height, title="POLYTECH ACADEMY"):
    """Dessine un en-tête professionnel avec le logo et les informations"""

    # Bordure décorative supérieure
    canvas.setStrokeColor(PolytechColors.BLUE_DARK)
    canvas.setLineWidth(4)
    canvas.line(0, height - 1*cm, width, height - 1*cm)

    canvas.setStrokeColor(PolytechColors.GOLD)
    canvas.setLineWidth(2)
    canvas.line(0, height - 1.2*cm, width, height - 1.2*cm)

    # Nom de l'institution
    canvas.setFont("Helvetica-Bold", 26)
    canvas.setFillColor(PolytechColors.BLUE_DARK)
    canvas.drawCentredString(width / 2, height - 2.5*cm, title)

    # Devise
    canvas.setFont("Helvetica-Oblique", 11)
    canvas.setFillColor(PolytechColors.GRAY)
    canvas.drawCentredString(width / 2, height - 3.2*cm, "Excellence • Innovation • Avenir")

    # Informations de contact
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(PolytechColors.GRAY_DARK)
    canvas.drawCentredString(width / 2, height - 3.8*cm,
                           "Campus Universitaire de Lomé • Tél: +228 XX XX XX XX • www.polytech-academy.tg")

    # Ligne de séparation élégante
    canvas.setStrokeColor(PolytechColors.GOLD)
    canvas.setLineWidth(1)
    canvas.line(2*cm, height - 4.5*cm, width - 2*cm, height - 4.5*cm)

    return height - 5*cm  # Retourne la position Y après l'en-tête


# ============================================================
# PIED DE PAGE PROFESSIONNEL
# ============================================================
def draw_footer(canvas, width, height, page_num=1, total_pages=1, doc_type="Document Officiel"):
    """Dessine un pied de page élégant avec numérotation"""

    footer_y = 2*cm

    # Ligne de séparation
    canvas.setStrokeColor(PolytechColors.GRAY_LIGHT)
    canvas.setLineWidth(1)
    canvas.line(2*cm, footer_y + 1*cm, width - 2*cm, footer_y + 1*cm)

    # Texte de gauche - Type de document
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(PolytechColors.GRAY)
    canvas.drawString(2*cm, footer_y + 0.4*cm, doc_type)

    # Texte du centre - Date de génération
    date_generation = datetime.now().strftime('%d/%m/%Y à %H:%M')
    canvas.drawCentredString(width / 2, footer_y + 0.4*cm, f"Généré le {date_generation}")

    # Texte de droite - Numéro de page
    canvas.drawRightString(width - 2*cm, footer_y + 0.4*cm, f"Page {page_num}/{total_pages}")

    # Mention légale
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(PolytechColors.GRAY)
    canvas.drawCentredString(width / 2, footer_y - 0.3*cm,
                            "Polytech Academy - Agrément N°2026/TG-ES - Document authentique")
    canvas.drawCentredString(width / 2, footer_y - 0.8*cm,
                            "Toute falsification est passible de poursuites judiciaires")


# ============================================================
# CADRE DÉCORATIF
# ============================================================
def draw_decorative_border(canvas, width, height, margin=1*cm):
    """Dessine un cadre décoratif élégant autour de la page"""

    # Cadre externe bleu
    canvas.setStrokeColor(PolytechColors.BLUE_PRIMARY)
    canvas.setLineWidth(3)
    canvas.rect(margin, margin, width - 2*margin, height - 2*margin, stroke=1, fill=0)

    # Cadre interne or (plus fin)
    canvas.setStrokeColor(PolytechColors.GOLD)
    canvas.setLineWidth(1)
    canvas.rect(margin + 0.2*cm, margin + 0.2*cm,
               width - 2*margin - 0.4*cm, height - 2*margin - 0.4*cm,
               stroke=1, fill=0)


# ============================================================
# TAMPON DE VALIDATION
# ============================================================
def draw_validation_stamp(canvas, x, y, status="VALIDÉ", color=None):
    """Dessine un tampon de validation élégant"""

    if color is None:
        color = PolytechColors.SUCCESS if status == "VALIDÉ" else PolytechColors.DANGER

    # Cercle externe
    canvas.setStrokeColor(color)
    canvas.setLineWidth(3)
    canvas.circle(x, y, 1.5*cm, stroke=1, fill=0)

    # Cercle interne
    canvas.setLineWidth(1.5)
    canvas.circle(x, y, 1.2*cm, stroke=1, fill=0)

    # Texte du tampon
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(color)
    canvas.drawCentredString(x, y + 0.2*cm, status.upper())

    # Date sous le status
    canvas.setFont("Helvetica", 7)
    date_str = datetime.now().strftime('%d/%m/%Y')
    canvas.drawCentredString(x, y - 0.4*cm, date_str)


# ============================================================
# SIGNATURE OFFICIELLE
# ============================================================
def draw_signature_block(canvas, x, y, titre="Le Directeur Général", nom="Kstar de la Kartz"):
    """Dessine un bloc de signature élégant"""

    # Titre
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(PolytechColors.BLUE_DARK)
    canvas.drawRightString(x, y, titre)

    # Nom
    canvas.setFont("Times-BoldItalic", 13)
    canvas.setFillColor(colors.black)
    canvas.drawRightString(x, y - 0.8*cm, nom)

    # Ligne de signature
    canvas.setStrokeColor(PolytechColors.GRAY_LIGHT)
    canvas.setLineWidth(1)
    canvas.line(x - 5*cm, y - 1.5*cm, x, y - 1.5*cm)


# ============================================================
# TABLEAU DE STYLE PROFESSIONNEL
# ============================================================
def get_table_style(header_color=None, alternate_rows=True):
    """Retourne un style de tableau professionnel"""
    from reportlab.platypus import TableStyle

    if header_color is None:
        header_color = PolytechColors.BLUE_DARK

    style = TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),

        # Corps du tableau
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),

        # Bordures
        ('GRID', (0, 0), (-1, -1), 1, PolytechColors.GRAY_LIGHT),
        ('LINEBELOW', (0, 0), (-1, 0), 2, header_color),

        # Alignement des nombres (supposant dernière colonne)
        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
    ])

    # Alternance de couleurs pour les lignes
    if alternate_rows:
        style.add('ROWBACKGROUNDS', (0, 1), (-1, -1),
                 [colors.white, colors.HexColor('#f9fafb')])

    return style


# ============================================================
# BOÎTE D'INFORMATION
# ============================================================
def draw_info_box(canvas, x, y, width, height, title, content, color=None):
    """Dessine une boîte d'information élégante"""

    if color is None:
        color = PolytechColors.BLUE_PRIMARY

    # Fond légèrement coloré
    canvas.setFillColor(colors.HexColor('#eff6ff'))
    canvas.setStrokeColor(color)
    canvas.setLineWidth(2)
    canvas.roundRect(x, y, width, height, 0.3*cm, stroke=1, fill=1)

    # Barre de titre
    canvas.setFillColor(color)
    canvas.roundRect(x, y + height - 1*cm, width, 1*cm, 0.3*cm, stroke=0, fill=1)

    # Titre
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(colors.white)
    canvas.drawString(x + 0.5*cm, y + height - 0.7*cm, title)

    # Contenu
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(PolytechColors.GRAY_DARK)

    # Si le contenu est une liste
    if isinstance(content, list):
        y_pos = y + height - 1.8*cm
        for line in content:
            canvas.drawString(x + 0.5*cm, y_pos, line)
            y_pos -= 0.5*cm
    else:
        canvas.drawString(x + 0.5*cm, y + height - 1.8*cm, content)


# ============================================================
# UTILITAIRES
# ============================================================
def format_date(date_obj, format_str='%d/%m/%Y'):
    """Formate une date de manière élégante"""
    if date_obj:
        return date_obj.strftime(format_str)
    return "Non définie"


def truncate_text(text, max_length=50, suffix='...'):
    """Tronque un texte trop long"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

